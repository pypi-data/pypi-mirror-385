"""
Malti Utilities

Utility functions and configuration helpers for the Malti telemetry system.
"""

import ipaddress
import logging
import os
from typing import Any, Dict, Optional

from .core import get_telemetry_system

logger = logging.getLogger(__name__)


def extract_ip_from_forwarded_for(forwarded_for_header: str) -> Optional[str]:
    """
    Extract the first (leftmost) IP address from X-Forwarded-For header.
    
    Args:
        forwarded_for_header: The X-Forwarded-For header value
        
    Returns:
        The first IP address from the header, or None if invalid
    """
    if not forwarded_for_header:
        return None
    
    # Split by comma and take the first (leftmost) IP
    ips = [ip.strip() for ip in forwarded_for_header.split(',')]
    if not ips:
        return None
    
    first_ip = ips[0]
    if is_valid_ip(first_ip):
        return first_ip
    
    return None


def is_valid_ip(ip_str: str) -> bool:
    """
    Validate if a string is a valid IP address (IPv4 or IPv6).
    
    Args:
        ip_str: The IP address string to validate
        
    Returns:
        True if valid IP address, False otherwise
    """
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False


def anonymize_ip(ip_str: str) -> str:
    """
    Anonymize an IP address using simple octet masking.
    
    For IPv4: Replace last octet with 'xxx' (e.g., 192.168.1.xxx)
    For IPv6: Replace last 64 bits with 'xxxx:xxxx:xxxx:xxxx'
    
    Args:
        ip_str: The IP address to anonymize
        
    Returns:
        The anonymized IP address, or original string if invalid
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        
        if isinstance(ip, ipaddress.IPv4Address):
            # For IPv4, replace last octet with 'xxx'
            octets = str(ip).split('.')
            octets[-1] = 'xxx'
            return '.'.join(octets)
        elif isinstance(ip, ipaddress.IPv6Address):
            # For IPv6, replace last 64 bits (4 groups) with 'xxxx'
            # First expand the IPv6 address to full form to ensure we have 8 groups
            expanded = ip.exploded  # This gives us the full form like 2001:0db8:0000:0000:0000:0000:0000:0001
            groups = expanded.split(':')
            if len(groups) >= 4:
                groups[-4:] = ['xxxx', 'xxxx', 'xxxx', 'xxxx']
            return ':'.join(groups)
        
    except ValueError:
        # If IP is invalid, return original string
        pass
    
    return ip_str


def get_malti_stats() -> Dict[str, Any]:
    """Get statistics from the global telemetry system instance"""
    telemetry_system = get_telemetry_system()
    return telemetry_system.get_stats()


def configure_malti(
    service_name: Optional[str] = None,
    api_key: Optional[str] = None,
    malti_url: Optional[str] = None,
    node: Optional[str] = None,
    batch_size: Optional[int] = None,
    batch_interval: Optional[float] = None,
    clean_mode: Optional[bool] = None,
    use_ip_as_consumer: Optional[bool] = None,
    ip_anonymize: Optional[bool] = None,
) -> None:
    """
    Configure Malti middleware settings.

    This function sets environment variables that the middleware will read.
    Call this before creating your FastAPI app.

    Args:
        service_name: Service name for telemetry
        api_key: Malti API key
        malti_url: Malti server URL
        node: Node identifier
        batch_size: Batch size for sending telemetry
        batch_interval: Batch interval in seconds
        clean_mode: Enable clean mode to ignore 401/404 responses (default: True)
        use_ip_as_consumer: Enable IP address extraction as consumer fallback (default: False)
        ip_anonymize: Enable IP address anonymization with simple octet masking (default: False)
    """
    if service_name:
        os.environ["MALTI_SERVICE_NAME"] = service_name
    if api_key:
        os.environ["MALTI_API_KEY"] = api_key
    if malti_url:
        os.environ["MALTI_URL"] = malti_url
    if node:
        os.environ["MALTI_NODE"] = node
    if batch_size:
        os.environ["MALTI_BATCH_SIZE"] = str(batch_size)
    if batch_interval:
        os.environ["MALTI_BATCH_INTERVAL"] = str(batch_interval)
    if clean_mode is not None:
        os.environ["MALTI_CLEAN_MODE"] = str(clean_mode)
    if use_ip_as_consumer is not None:
        os.environ["MALTI_USE_IP_AS_CONSUMER"] = str(use_ip_as_consumer)
    if ip_anonymize is not None:
        os.environ["MALTI_IP_ANONYMIZE"] = str(ip_anonymize)

    logger.info("Malti configuration updated")
