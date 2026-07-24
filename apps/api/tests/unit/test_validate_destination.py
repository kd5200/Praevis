"""IP / destination validation unit tests."""

import ipaddress

import pytest

from praevis_api.pipeline.validate_destination import (
    DestinationValidationError,
    is_blocked_ip,
    validate_destination_url,
    validate_hostname_policy,
)


@pytest.mark.security
@pytest.mark.parametrize(
    "ip",
    [
        "127.0.0.1",
        "10.0.0.5",
        "192.168.1.1",
        "172.16.0.1",
        "169.254.169.254",
        "::1",
        "fc00::1",
        "fe80::1",
    ],
)
def test_blocked_ips(ip: str) -> None:
    assert is_blocked_ip(ipaddress.ip_address(ip))


@pytest.mark.security
def test_public_ip_allowed() -> None:
    assert not is_blocked_ip(ipaddress.ip_address("8.8.8.8"))


@pytest.mark.security
def test_localhost_hostname_blocked() -> None:
    with pytest.raises(DestinationValidationError):
        validate_hostname_policy("localhost")


@pytest.mark.security
def test_metadata_hostname_blocked() -> None:
    with pytest.raises(DestinationValidationError):
        validate_hostname_policy("metadata.google.internal")


@pytest.mark.security
def test_ip_literal_in_url_blocked() -> None:
    with pytest.raises(DestinationValidationError) as exc:
        validate_destination_url("http://127.0.0.1/", resolve_dns=False)
    assert exc.value.code == "destination_blocked_ip"
