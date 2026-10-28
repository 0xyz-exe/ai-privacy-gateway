import hashlib
import ipaddress
import secrets
import socket
from urllib.parse import urlparse

def generate_api_key(prefix: str = "aipg_live_") -> tuple[str, str, str]:
    """
    Returns (raw_key, key_hash, key_prefix)
    Raw key is shown only once to user.
    """
    random_part = secrets.token_urlsafe(32)
    raw_key = f"{prefix}{random_part}"
    key_hash = hash_api_key(raw_key)
    display_prefix = raw_key[:12] + "..."
    return raw_key, key_hash, display_prefix

def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

def verify_api_key(raw_key: str, key_hash: str) -> bool:
    computed = hash_api_key(raw_key)
    return secrets.compare_digest(computed, key_hash)

def validate_upstream_url(url: str, allow_local: bool = False) -> bool:
    """
    SSRF Protection:
    - Validates scheme is http or https
    - Resolves hostname to IP addresses
    - Blocks loopback, link-local, private IP spaces, cloud metadata (169.254.169.254)
    - allow_local=True permits localhost/127.0.0.1 for local Ollama adapter
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        
        hostname = parsed.hostname
        if not hostname:
            return False
            
        if hostname.lower() in ("localhost", "127.0.0.1", "::1"):
            return allow_local
            
        # Resolve DNS
        addr_info = socket.getaddrinfo(hostname, None)
        for item in addr_info:
            ip_str = item[4][0]
            ip = ipaddress.ip_address(ip_str)
            
            if ip.is_loopback:
                if not allow_local:
                    return False
            elif ip.is_private or ip.is_link_local or ip.is_multicast or ip.is_reserved:
                return False
            # AWS / GCP metadata IP
            if str(ip) == "169.254.169.254":
                return False
                
        return True
    except Exception:
        return False
