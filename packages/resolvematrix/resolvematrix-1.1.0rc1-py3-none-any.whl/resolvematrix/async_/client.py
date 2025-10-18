import httpx, logging, pydantic, json, re, typing

from ..client import ClientVersionsResponse, handle_client_well_known, __version__, SERVER_NAME_REGEX, limited_read
from ..err import ResolutionError
from ..cache import BaseCache, BasicResolutionCache

class AsyncClientResolver:
    """
    Resolves a Matrix server's client-to-server API endpoint using the client well-known method,
    falling back to a default (https://{server_name}:8448).

    Caches results in a provided cache backend (or an in-memory cache by default).

    :param client: An optional httpx.Client instance to use for HTTP requests. If not provided, a default client
    will be created.
    :param cache: An optional cache backend implementing the BaseCache interface. If not provided, an in-memory
    cache will be used.
    :param verify_tls: Whether to verify TLS certificates. Defaults to True.
    """
    RESPONSE_SIZE_LIMIT = 1024 * 64  # 64 KiB
    RESPONSE_CHUNK_SIZE = 1024 * 8  # 8 KiB

    def __init__(
            self,
            client: httpx.AsyncClient | None = None,
            cache: BaseCache | None = None,
            verify_tls: bool = True
    ):
        self.client = client or httpx.AsyncClient(
            headers={
                "User-Agent": f"resolvematrix/{__version__}",
                "Accept": "application/json",
            },
            timeout=10.0,
            follow_redirects=False,
            max_redirects=30,  # MSC2499 (can't be overridden per-call for some reason)
            trust_env=True,
            verify=verify_tls,
        )
        self.cache = cache or BasicResolutionCache()
        self.log = logging.getLogger("resolvematrix.client")

    async def get_client_versions(self, base_url: str) -> ClientVersionsResponse:
        """
        Attempts to fetch the /_matrix/client/versions endpoint from a given base URL, and validates the response.
        :param base_url: The base URL of the Matrix server.
        :return: True if the endpoint was fetched and parsed successfully, False otherwise.
        """
        url = base_url.rstrip("/") + "/_matrix/client/versions"
        response = (await self.client.get(url)).raise_for_status()
        data = limited_read(response, self.RESPONSE_SIZE_LIMIT, self.RESPONSE_CHUNK_SIZE)
        v = ClientVersionsResponse.model_validate(data, strict=True)
        self.log.debug("Client versions at %s: %s", base_url, v)
        return v

    async def get_well_known(self, server_name: str, msc4299: bool = False) -> tuple[typing.Any, int]:
        """
        Fetches and returns the well-known configuration for a given Matrix server.

        :param server_name: The domain name of the Matrix server.
        :param msc4299: Whether to use the MSC4299 changes for well-known lookups.
        :return: The parsed JSON data if available.
        """
        url = f"https://{server_name}/.well-known/matrix/client"
        response = (await self.client.get(url, follow_redirects=msc4299)).raise_for_status()
        expires = 0
        if "Cache-Control" in response.headers:
            cache_control = response.headers["Cache-Control"]
            match = re.search(r"max-age=(\d+)", cache_control)
            if match:
                try:
                    expires = int(match.group(1))
                except ValueError:
                    pass
        return (
            limited_read(response, 50 * 1024 if msc4299 else self.RESPONSE_SIZE_LIMIT, self.RESPONSE_CHUNK_SIZE),
            expires,
        )

    async def resolve(self, server_name: str, extra_validation: bool = True, unstable_follow_redirects: bool = False) -> str:
        """
        Resolves a Matrix server's client-to-server API endpoint.
        :param server_name: The domain name of the Matrix server.
        :param extra_validation: Whether to perform extra validation on the resolved URL by calling the client versions
        endpoint. Slightly increases response time but ensures the server is actually a Matrix server.
        :param unstable_follow_redirects: Whether to follow HTTP redirects, which is not explicitly defined in the
        specification yet. See: MSC2499
        :return: the resolved base URL without a trailing slash.
        :raises ResolutionError: - the server cannot be resolved.
        :raises ValueError: - the server name format is invalid.
        """
        # Cheat: if the server name is actually a URL, just return that.
        if server_name.startswith("http://") or server_name.startswith("https://"):
            parsed = httpx.URL(server_name)
            if parsed.host != "" and parsed.scheme in ("http", "https"):
                return str(parsed).rstrip("/")

        # Fetch from cache first
        if cached := self.cache.get(server_name):
            self.log.debug("Cache hit for %s: %s", server_name, cached)
            return cached

        # Step 1: Extract the server name from user ID (done before this function is called)
        # Step 2: Extract the hostname from the server name
        match = SERVER_NAME_REGEX.match(server_name.strip())
        if not match:
            raise ValueError("Invalid server name")
        hostname = match.group(0)
        default_dest = "https://" + hostname

        # Step 3: Fetch the well-known file
        try:
            self.log.debug("Resolving well-known for %s", hostname)
            well_known, expires = await self.get_well_known(hostname, unstable_follow_redirects)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # Step 3.1: If the response status is 404, IGNORE.
                # Our interpretation of "IGNORE" is to just use the default.
                self.log.info("No well-known file found found %s, using default destination", hostname)
                self.cache.add(server_name, default_dest)
                self.cache.mark_offline(server_name)  # forces resolution sooner
                return default_dest
            # Step 3.2: If the response status is not 200, or the response body is invalid, FAIL.
            raise ResolutionError("Failed to fetch well-known", e) from e
        except (httpx.HTTPError, ResolutionError) as e:
            # Step 3.2: If the response status is not 200, or the response body is invalid, FAIL.
            raise ResolutionError("Failed to fetch well-known", e) from e
        except (OSError, json.JSONDecodeError) as e:
            # Step 3.2: If the response status is not 200, or the response body is invalid, FAIL.
            raise ResolutionError("Failed to read or parse well-known", e) from e

        # Step 3-5.1: Parse and validate the well-known
        current_dest = handle_client_well_known(well_known) or default_dest

        # Step 5.2: Clients SHOULD validate that the URL points to a valid homeserver before accepting it by connecting
        # to the /_matrix/client/versions endpoint, ensuring that it does not return an error, and parsing and
        # validating that the data conforms with the expected response format. If any step in the validation fails,
        # then FAIL.
        if extra_validation:
            self.log.debug("Validating resolved base URL %s for %s", current_dest, hostname)
            try:
                await self.get_client_versions(current_dest)
            except (httpx.HTTPError, IOError, pydantic.ValidationError) as e:
                raise ResolutionError("Resolved base URL did not validate as a Matrix homeserver", e) from e

        # Return the resolved base URL without a trailing slash
        self.cache.add(server_name, current_dest, expires)
        return current_dest.rstrip("/")
