import ipaddress
import logging
import random
import typing

import dns.asyncresolver
import httpx
import pydantic

from ..cache import BaseCache, BasicResolutionCache
from ..client import SERVER_NAME_REGEX, __version__, limited_read
from ..err import ResolutionError
from ..server import ServerDestination, DNSMode, ServerKeys

if typing.TYPE_CHECKING:
    ANY_ADDRESS = ipaddress.IPv6Address | ipaddress.IPv4Address


class AsyncServerResolver:
    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
        dns_mode: DNSMode = DNSMode.IPV4_FIRST,
        dns_resolver: dns.resolver.Resolver | None = None,
        cache: BaseCache | None = None,
        verify_tls: bool = True
    ):
        self.client = client or httpx.AsyncClient(
            headers={"User-Agent": f"resolvematrix/{__version__}"},
            timeout=30.0,
            trust_env=True,
            verify=verify_tls,
        )
        self.dns_mode = dns_mode
        self.dns_resolver: dns.asyncresolver.Resolver = dns_resolver or dns.asyncresolver.get_default_resolver()
        self.log = logging.getLogger("resolvematrix.server")
        self.cache = cache or BasicResolutionCache()

    async def _lookup_a(self, domain: str) -> list[ipaddress.IPv4Address]:
        """
        Resolves a domain name to a list of IPv4 addresses using DNS A records.

        :param domain: The domain name to resolve.
        :return: A list of IPv4Address objects. An empty list if no A records are found.
        """
        try:
            answers = await self.dns_resolver.resolve(domain, "A")
            return [ipaddress.IPv4Address(rdata.to_text()) for rdata in answers]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.DNSException):
            return []

    async def _lookup_aaaa(self, domain: str) -> list[ipaddress.IPv6Address]:
        """
        Resolves a domain name to a list of IPv6 addresses using DNS AAAA records.

        :param domain: The domain name to resolve.
        :return: A list of IPv6Address objects. An empty list if no AAAA records are found.
        """
        try:
            answers = await self.dns_resolver.resolve(domain, "AAAA")
            return [ipaddress.IPv6Address(rdata.to_text()) for rdata in answers]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.DNSException):
            return []

    async def lookup_domain(self, domain: str) -> "ANY_ADDRESS":
        """
        Resolves a domain name to an IP address using DNS A/AAAA records.

        :param domain: The domain name to resolve.
        :return: An IPv4Address or IPv6Address object. Chooses a random address if multiple are found.
        :raises ResolutionError: If no A or AAAA records are found.
        """
        if self.dns_mode == DNSMode.IPV4_ONLY:
            records = await self._lookup_a(domain)
        elif self.dns_mode == DNSMode.IPV6_ONLY:
            records = await self._lookup_aaaa(domain)
        elif self.dns_mode == DNSMode.IPV4_FIRST:
            records = await self._lookup_a(domain)
            if not records:
                records = await self._lookup_aaaa(domain)
        else:  # DNSMode.IPV6_FIRST
            records = await self._lookup_aaaa(domain)
            if not records:
                records = await self._lookup_a(domain)

        if not records:
            raise ResolutionError(f"No DNS records found for domain: {domain}")
        random.shuffle(records)
        return records[0]

    async def _srv_lookup(self, record_name: str) -> tuple["ANY_ADDRESS", int] | None:
        """
        Performs an SRV lookup and additional A/AAAA lookups for the target hosts,
        returning an (IP address, port) tuple, or None if no valid records are found.
        """
        try:
            answers = await self.dns_resolver.resolve(record_name, "SRV")
            records = [(rdata.target.to_text(omit_final_dot=True), rdata.port) for rdata in answers]
            if records:
                records.sort(key=lambda x: (x[0], -x[1]), reverse=True)

                for record in records:
                    # Return the first one that can be resolved
                    target, port = record
                    try:
                        ip = ipaddress.ip_address(target)
                        return ip, port
                    except ValueError:
                        pass

                    try:
                        await self.lookup_domain(target)
                        return target, port
                    except ResolutionError:
                        continue

        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.DNSException):
            pass
        return None

    async def modern_srv_lookup(self, domain: str) -> tuple[str, int] | None:
        """
        Performs an SRV lookup for _matrix-fed._tcp.<domain> as per the modern Matrix server name resolution process.

        :param domain: The domain name to look up.
        :return: A tuple of (target, port) if an SRV record is found, otherwise None.
        """
        return await self._srv_lookup(f"_matrix-fed._tcp.{domain}")

    async def deprecated_srv_lookup(self, domain: str) -> tuple[str, int] | None:
        """
        Performs an SRV lookup for _matrix._tcp.<domain> as per the deprecated Matrix server name resolution process.

        :param domain: The domain name to look up.
        :return: A tuple of (target, port) if an SRV record is found, otherwise None.
        """
        return await self._srv_lookup(f"_matrix._tcp.{domain}")

    async def srv_lookup(self, domain: str, allow_deprecated: bool = True) -> tuple[str, int, bool] | tuple[None, None, None]:
        """
        Performs an SRV lookup for the given domain, first trying the modern _matrix-fed._tcp.<domain> record,
        and falling back to the deprecated _matrix._tcp.<domain> record if allowed.

        :param domain: The domain name to look up.
        :param allow_deprecated: Whether to allow falling back to the deprecated SRV record.
        :return: A tuple of (target, port) if an SRV record is found, otherwise None.
        """
        result = await self.modern_srv_lookup(domain)
        modern = True
        if allow_deprecated and result is None:
            result = await self.deprecated_srv_lookup(domain)
            modern = False
        if result is None or result[0] is None:
            return None, None, None
        return result[0], result[1], modern

    async def resolve_well_known(self, destination: ServerDestination) -> ServerDestination:
        """
        Performs resolution steps 3 through 3.5 of the server name resolution process.

        :param destination: The server name to resolve.
        :return: A ServerDestination object with the resolved address and port set.
        :raises ResolutionError: If the well-known file cannot be fetched or parsed.
        """
        url = f"https://{destination.hostname}/.well-known/matrix/server"
        try:
            self.log.debug("requesting well-known for %r", destination.hostname)
            response = (await self.client.get(
                url,
                headers={"Host": destination.hostname},
                follow_redirects=True,  # s2s explicitly allows redirects, unlike c2s
            )).raise_for_status()
            data = limited_read(response, 1024 * 64, 1024 * 8)
            assert "m.server" in data, "Invalid well-known response"
            delegated_location = data["m.server"]
            self.log.debug("%r is delegated to %r", destination.hostname, delegated_location)
            assert SERVER_NAME_REGEX.match(delegated_location) is not None, "Invalid m.server value in well-known"
        except (httpx.RequestError, httpx.HTTPStatusError, ValueError, AssertionError) as e:
            raise ResolutionError("Failed to fetch or parse well-known file", e) from e

        ipv6, ipv4, delegated_hostname, delegated_port = SERVER_NAME_REGEX.match(delegated_location).groups()

        # 3.1: If <delegated_hostname> is an IP literal, then that IP address should be used together with the
        # <delegated_port> or 8448 if no port is provided.
        if ipv4 or ipv6:
            ip = ipv4 or ipv6
            self.log.debug("delegated hostname %r for %r is an IP literal", delegated_hostname, destination.hostname)
            destination.hostname = f"{ip}:{delegated_port or 8448}"
            destination.host_header = ip
            destination.sni = ip
            destination._step = 3.1
            return destination

        # 3.2: If <delegated_hostname> is not an IP literal, and <delegated_port> is present, an IP address is
        # discovered by looking up CNAME, AAAA or A records for <delegated_hostname>.
        # The resulting IP address is used, alongside the <delegated_port>.
        # Requests must be made with a Host header of <delegated_hostname>:<delegated_port>.
        # The target server must present a valid certificate for <delegated_hostname>.
        if delegated_port:
            self.log.debug(
                "delegated hostname %r for %r includes explicit port, skipping SRV lookup",
                delegated_hostname,
                destination.hostname,
            )
            await self.lookup_domain(delegated_hostname)
            destination.hostname = f"{delegated_hostname}:{delegated_port}"
            destination.host_header = f"{delegated_hostname}:{delegated_port}"
            destination.sni = delegated_hostname
            destination._step = 3.2
            return destination

        # 3.3+3.4: If <delegated_hostname> is not an IP literal and no <delegated_port> is present,
        # an SRV record is looked up...
        self.log.debug(
            "%r delegates to %r without explicit port, performing SRV lookups", destination.hostname, delegated_hostname
        )
        new_address, new_port, modern = await self.srv_lookup(delegated_hostname)
        if new_address and new_port:
            self.log.debug("found SRV record for %r: %r:%d", delegated_hostname, new_address, new_port)
            destination.hostname = f"{new_address}:{new_port}"
            destination.host_header = delegated_hostname
            destination.sni = delegated_hostname
            destination._step = 3.3 if modern else 3.4
            return destination

        # 3.5: If no SRV record is found, an IP address is resolved using CNAME, AAAA or A records.
        # Requests are then made to the resolved IP address and a port of 8448,
        # using a Host header of <delegated_hostname>.
        self.log.debug("no SRV record found for %r, falling back to A/AAAA lookup", delegated_hostname)
        await self.lookup_domain(delegated_hostname)
        destination.hostname = f"{delegated_hostname}:8448"
        destination.host_header = delegated_hostname
        destination.sni = delegated_hostname
        destination._step = 3.5
        return destination

    def create_request(
            self,
            destination: ServerDestination,
            method: str,
            uri: str,
            *,
            headers: dict[str, str] | None = None,
            json_data: dict | None = None,
            content: bytes | None = None,
            params: dict[str, str] | None = None,
            **kwargs,
    ) -> httpx.Request:
        """
        Creates a httpx.Request object for the given ServerDestination.

        :param destination: The resolved destination
        :param method: The HTTP method to use (e.g. "GET", "POST").
        :param uri: The URI to request (e.g. "/_matrix/federation/v1/version").
        :param headers: Optional additional headers to include in the request.
        :param json_data: Optional JSON data to include in the request body.
        :param content: Optional raw bytes to include in the request body.
        :param params: Optional query parameters to include in the request URL.
        :param kwargs: Additional keyword arguments to pass to httpx.Client.build_request.
        :return: A httpx.Request object
        """
        headers = headers or {}
        extensions = kwargs.get("extensions", {})
        if destination.sni:
            extensions["sni_hostname"] = destination.sni
        return self.client.build_request(
            method,
            f"{destination.base_url}{uri}",
            content=content,
            json=json_data,
            params=params,
            headers={**headers, "Host": destination.host_header},
            extensions=extensions or None,
        )

    async def get_server_version(self, destination: ServerDestination) -> tuple[str, str]:
        """
        Fetches the server version from the /_matrix/federation/v1/version endpoint.

        :param destination: The resolved destination
        :return: A tuple of [software_name, version]
        """
        try:
            self.log.debug("requesting server version for %r", destination.hostname)
            response = (await self.client.send(
                self.create_request(destination, "GET", "/_matrix/federation/v1/version"),
            )).raise_for_status()
            data = limited_read(response, 1024 * 64, 1024 * 8)
            if not isinstance(data, dict):
                raise ValueError("Invalid version response - not a JSON object")
            server = data.get("server", {})
            if not isinstance(server, dict):
                raise ValueError("Invalid version response - 'server' is not an object")
            software_name = server.get("name") or ""
            version = server.get("version") or ""
            return software_name, version
        except (httpx.RequestError, httpx.HTTPStatusError, ValueError, AssertionError) as e:
            raise ResolutionError("Failed to fetch or parse server version", e) from e

    async def get_server_keys(self, destination: ServerDestination) -> ServerKeys:
        """
        Fetches the server keys from the /_matrix/key/v2/server endpoint.

        :param destination: The resolved destination
        :return: A ServerKeys object containing the server's keys and signatures.
        """
        try:
            self.log.debug("requesting server keys for %r", destination.hostname)
            response = (await self.client.send(
                self.create_request(destination, "GET", "/_matrix/key/v2/server"),
            )).raise_for_status()
            data = limited_read(response, 1024 * 256, 1024 * 16)
            return ServerKeys.model_validate(data)
        except (httpx.RequestError, httpx.HTTPStatusError, pydantic.ValidationError) as e:
            raise ResolutionError("Failed to fetch or parse server keys", e) from e

    async def resolve(self, server_name: str) -> ServerDestination:
        if not (match := SERVER_NAME_REGEX.match(server_name)):
            raise ValueError("Invalid server name")

        ipv6, ipv4, hostname, port_str = match.groups()
        port = int(port_str) if port_str else 8448
        destination = ServerDestination(hostname=hostname)
        success = True

        # 1: If the hostname is an IP literal, then that IP address should be used, together with the given port number,
        # or 8448 if no port is given.
        if ipv4 or ipv6:
            self.log.debug("server name %r is an IP literal, skipping well-known and SRV lookups", server_name)
            ip = ipv4 or ipv6
            destination.hostname = f"{ip}:{port}"
            destination.sni = ip
            destination.host_header = server_name
            destination.step = 1
        else:
            if port_str:
                self.log.debug(
                    "server name %r includes explicit port, skipping well-known and SRV lookups", server_name
                )
                # 2: If the hostname is not an IP literal, and the server name includes an explicit port,
                # resolve the hostname to an IP address using CNAME, AAAA or A records
                await self.lookup_domain(hostname)
                destination.hostname = f"{hostname}:{port}"
                destination.host_header = server_name
                destination.step = 2
            else:
                # 3: well-known shenanigans
                try:
                    destination = await self.resolve_well_known(destination)
                except (OSError, ResolutionError):
                    self.log.debug("well-known lookup failed for %r, falling back to SRV and A/AAAA lookups", hostname)
                    # 4+5: If the /.well-known request resulted in an error response,
                    # a server is found by resolving an SRV record
                    new_address, new_port, modern = await self.srv_lookup(hostname)
                    if new_address and new_port:
                        self.log.debug("found SRV record for %r: %r:%d", hostname, new_address, new_port)
                        destination.hostname = f"{new_address}:{new_port}"
                        destination.host_header = hostname
                        destination.sni = hostname
                        destination._step = 4 if modern else 5
                    else:
                        # 6: If the /.well-known request returned an error response, and no SRV records were found,
                        # an IP address is resolved using CNAME, AAAA and A records.
                        # Requests are made to the resolved IP address using port 8448
                        # and a Host header containing the <hostname>
                        success = False
                        self.log.debug("no SRV record found for %r, falling back to A/AAAA lookup", hostname)
                        await self.lookup_domain(hostname)
                        destination.hostname = f"{hostname}:8448"
                        destination.host_header = hostname
                        destination.sni = hostname
                        destination._step = 6
        self.cache.add(server_name, destination)
        if not success:
            # Mark as offline so that we re-resolve sooner
            # We might not actually be offline, but generally servername:8448 indicates a lookup error,
            # since most servers will have a well-known or SRV record.
            self.cache.mark_offline(server_name)
        return destination
