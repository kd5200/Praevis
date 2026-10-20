"""Destination / IP safety checks (SSRF defenses)."""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

# Well-known cloud metadata / link-local targets
BLOCKED_HOSTNAMES = {
    "metadata.google.internal",
    "metadata.goog",
    "kubernetes.default",
    "kubernetes.default.svc",
}


class DestinationValidationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def is_blocked_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Return True if the address must not be fetched."""

    if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_multicast:
        return True
    if ip.is_reserved or ip.is_unspecified:
        return True
    # Cloud metadata IPv4
    if isinstance(ip, ipaddress.IPv4Address) and ip == ipaddress.IPv4Address("169.254.169.254"):
        return True
    # Unique local IPv6 already covered by is_private in Python 3.11+ for fc00::/7
    return False


def _parse_int_literal(part: str) -> int:
    """Parse one legacy IPv4 part: decimal, octal (leading 0), or hex (0x)."""

    if part.lower().startswith("0x"):
        return int(part, 16)
    if len(part) > 1 and part.startswith("0"):
        return int(part, 8)
    return int(part, 10)


def _parse_legacy_ipv4(host: str) -> ipaddress.IPv4Address | None:
    """Normalize inet_aton-style IPv4 spellings to an address.

    Accepts 1-4 dot-separated parts where the final part holds the remaining
    bits (e.g. ``127.1`` -> ``127.0.0.1``) and each part may be decimal,
    octal (leading 0), or hex (0x). Returns None when the host is not a
    legacy IPv4 spelling.
    """

    parts = host.split(".")
    if not 1 <= len(parts) <= 4 or any(not part for part in parts):
        return None
    suffix_bits = {1: 32, 2: 24, 3: 16, 4: 8}[len(parts)]
    value = 0
    try:
        for i, part in enumerate(parts):
            parsed = _parse_int_literal(part)
            bits = suffix_bits if i == len(parts) - 1 else 8
            if parsed < 0 or parsed >= 1 << bits:
                return None
            value = (value << bits) | parsed
    except ValueError:
        return None
    return ipaddress.IPv4Address(value)


def _coerce_ip_literal(host: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    try:
        return ipaddress.ip_address(host)
    except ValueError:
        return _parse_legacy_ipv4(host)


def validate_ip_literal(host: str) -> None:
    ip = _coerce_ip_literal(host)
    if ip is None:
        return
    if is_blocked_ip(ip):
        raise DestinationValidationError(
            "destination_blocked_ip",
            f"Destination IP {host} is not allowed",
        )


def validate_hostname_policy(host: str) -> None:
    lowered = host.lower().rstrip(".")
    if lowered in BLOCKED_HOSTNAMES:
        raise DestinationValidationError(
            "destination_blocked_host",
            f"Destination host {host} is not allowed",
        )
    if lowered == "localhost" or lowered.endswith(".localhost"):
        raise DestinationValidationError(
            "destination_blocked_host",
            "localhost destinations are not allowed",
        )
    validate_ip_literal(lowered)


def resolve_host_ips(host: str) -> list[str]:
    """Resolve host to IP strings. Raises on DNS failure."""

    try:
        infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise DestinationValidationError(
            "dns_resolution_failed", f"DNS resolution failed for {host}"
        ) from exc

    ips: list[str] = []
    for info in infos:
        sockaddr = info[4]
        ip = str(sockaddr[0])
        if ip not in ips:
            ips.append(ip)
    if not ips:
        raise DestinationValidationError(
            "dns_resolution_failed", f"No addresses resolved for {host}"
        )
    return ips


def validate_resolved_ips(ips: list[str]) -> None:
    for ip_str in ips:
        ip = ipaddress.ip_address(ip_str)
        if is_blocked_ip(ip):
            raise DestinationValidationError(
                "destination_blocked_ip",
                f"Resolved IP {ip_str} is not allowed",
            )


def validate_destination_url(url: str, *, resolve_dns: bool = True) -> list[str]:
    """Validate URL host policy and optionally DNS resolution / IP ranges.

    Returns resolved IP strings when resolve_dns is True, else [].
    """

    parsed = urlparse(url)
    host = parsed.hostname
    if not host:
        raise DestinationValidationError("url_malformed", "URL host is missing")
    validate_hostname_policy(host)
    if not resolve_dns:
        return []
    ips = resolve_host_ips(host)
    validate_resolved_ips(ips)
    return ips
