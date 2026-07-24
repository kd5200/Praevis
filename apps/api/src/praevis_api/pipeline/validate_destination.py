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


def validate_ip_literal(host: str) -> None:
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
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
