from urllib.parse import urlparse
from ipaddress import ip_address
from app.config import Config
from app.services.demo_target_service import is_demo_target_url


def _host_is_allowed(host: str) -> bool:
    if not host:
        return False
    if host in Config.ALLOWED_HOSTS:
        return True
    if is_demo_target_url(f"https://{host}"):
        return True
    try:
        ip = ip_address(host)
        return ip.is_loopback or ip.is_private
    except ValueError:
        return host.endswith(".local") and host.startswith(("demo.", "shop.", "files.", "api.", "admin."))


def validate_target_url(url: str):
    if not url:
        return False, "Please enter a target URL."

    try:
        parsed = urlparse(url)
    except Exception:
        return False, "Invalid URL format."

    if parsed.scheme not in ("http", "https"):
        return False, "Only http and https URLs are allowed."

    if not parsed.netloc:
        return False, "URL must include a valid host."

    host = parsed.hostname.lower() if parsed.hostname else ""

    if not _host_is_allowed(host):
        return False, (
            f"Target host '{host}' is not allowed in this educational build. "
            f"Allowed hosts: {', '.join(Config.ALLOWED_HOSTS)} plus configured demo targets."
        )

    return True, "Valid target."