"""SSRF regression tests for non-standard loopback IP spellings.

``ipaddress.ip_address`` only understands canonical literals, so legacy
inet_aton-style forms such as decimal dwords (``2130706433``), shorthand
(``127.1``), octal (``0177.0.0.1``), and hex (``0x7f.0.0.1``) used to slip
past the destination validator. These tests pin that they are normalized and
rejected with ``destination_blocked_ip``.
"""

from __future__ import annotations

import pytest

from praevis_api.pipeline.validate_destination import (
    DestinationValidationError,
    validate_destination_url,
    validate_hostname_policy,
)

LEGACY_LOOPBACK_HOSTS = [
    "2130706433",  # decimal dword -> 127.0.0.1
    "127.1",  # shorthand -> 127.0.0.1
    "0177.0.0.1",  # octal -> 127.0.0.1
    "0x7f.0.0.1",  # hex -> 127.0.0.1
]


@pytest.mark.security
@pytest.mark.parametrize("host", LEGACY_LOOPBACK_HOSTS)
def test_legacy_loopback_spelling_blocked_in_host_policy(host: str) -> None:
    with pytest.raises(DestinationValidationError) as exc:
        validate_hostname_policy(host)
    assert exc.value.code == "destination_blocked_ip"


@pytest.mark.security
@pytest.mark.parametrize("host", LEGACY_LOOPBACK_HOSTS)
def test_legacy_loopback_spelling_blocked_in_url(host: str) -> None:
    with pytest.raises(DestinationValidationError) as exc:
        validate_destination_url(f"http://{host}/", resolve_dns=False)
    assert exc.value.code == "destination_blocked_ip"


@pytest.mark.security
@pytest.mark.parametrize(
    "host",
    [
        "10.1",  # shorthand -> 10.0.0.1 (private rfc1918)
        "0251.254.0.1",  # octal -> 169.254.0.1 (link-local)
    ],
)
def test_other_blocked_ranges_in_legacy_spelling(host: str) -> None:
    with pytest.raises(DestinationValidationError) as exc:
        validate_destination_url(f"http://{host}/", resolve_dns=False)
    assert exc.value.code == "destination_blocked_ip"


@pytest.mark.security
def test_public_legacy_spelling_is_not_blocked() -> None:
    # Decimal dword for 8.8.8.8 is a public address; policy must allow it.
    validate_destination_url("http://134744072/", resolve_dns=False)