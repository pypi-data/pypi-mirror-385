import logging

import pytest

from ..client import server_from_user_id
from .client import AsyncClientResolver
from .server import AsyncServerResolver
from ..err import ResolutionError


@pytest.mark.parametrize(
    "user_id,extra,expected,fail",
    [
        ("@github:maunium.net", True, "https://api.mau.chat", None),
        ("@nex:continuwuity.rocks", True, "https://continuwuity.rocks", None),
        ("@nex:timedout.uk:69", True, "https://timedout.uk:69", None),
        ("@nex:nexy7574.co.uk", True, "https://matrix.nexy7574.co.uk", None),
        ("@nex:transgender.ing", True, "https://matrix.transgender.ing", None),
        ("@nex:localhost:8448", False, "https://localhost:8448", ResolutionError),
        ("@nex:localhost", False, "https://localhost", ResolutionError),
        ("@nex:localhost..invalid", True, "", ResolutionError),
    ],
)
@pytest.mark.asyncio
async def test_client_resolver(user_id: str, extra: bool, expected: str, fail: Exception | None):
    server_name = server_from_user_id(user_id)
    resolver = AsyncClientResolver()
    if fail:
        with pytest.raises(fail):
            await resolver.resolve(server_name, extra_validation=extra)
    else:
        resolved = await resolver.resolve(server_name, extra_validation=extra)
        assert resolved == expected, f"Expected {expected}, got {resolved}"


@pytest.mark.parametrize(
    "server_name,fail",
    [
        ("maunium.net", None),
        ("continuwuity.rocks", None),
        ("timedout.uk:69", None),
        ("nexy7574.co.uk", None),
        ("transgender.ing", None),
        ("matrix.org", None),
        ("2.s.resolvematrix.dev:7652", None),
        ("3b.s.resolvematrix.dev", None),
        ("3c.s.resolvematrix.dev", None),
        ("3d.s.resolvematrix.dev", None),
        ("4.s.resolvematrix.dev", None),
        ("5.s.resolvematrix.dev", None),
        ("3c.msc4040.s.resolvematrix.dev", None),
        ("4.msc4040.s.resolvematrix.dev", None),
    ],
)
@pytest.mark.asyncio
async def test_server_resolver(caplog, server_name: str, fail: Exception | None):
    caplog.set_level(logging.DEBUG)
    logger = logging.getLogger("resolvematrix.test")
    resolver = AsyncServerResolver()
    if fail:
        with pytest.raises(fail):
            await resolver.resolve(server_name)
    else:
        resolved = await resolver.resolve(server_name)
        logger.info("Resolved %s to %r", server_name, resolved)
        logger.info(
            "Fetching %s/_matrix/federation/v1/version (%r, base_url=%r)",
            resolved.base_url,
            resolved,
            resolved.base_url,
        )
        key_req = resolver.client.build_request(
            "GET",
            f"{resolved.base_url}/_matrix/federation/v1/version",
            headers={"Host": resolved.host_header},
            extensions={"sni_hostname": resolved.sni} if resolved.sni else None,
        )
        response = await resolver.client.send(key_req)
        logger.debug("Response: %s", response.text)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
