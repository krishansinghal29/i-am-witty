"""
Location service to get user's location context from IP address.
Uses ip-api.com for free IP geolocation (no API key required).
"""

import requests
from typing import Optional, Dict
from helpers.logger import logger


def get_location_from_ip(ip_address: Optional[str] = None) -> Optional[Dict[str, str]]:
    """
    Get location context from IP address using ip-api.com.

    Args:
        ip_address: IP address to geolocate. If None, uses the request's IP.

    Returns:
        Dict with location context:
        {
            "country": "India",
            "city": "Mumbai",
            "region": "Maharashtra",
            "country_code": "IN",
            "latitude": 19.0760,
            "longitude": 72.8777,
            "timezone": "Asia/Kolkata"
        }
        Returns None if geolocation fails.
    """
    try:
        # ip-api.com endpoint (free, no auth required)
        # Limit: 45 requests per minute from an IP address
        url = "http://ip-api.com/json/"

        if ip_address:
            url += ip_address
        # If no IP provided, ip-api automatically detects the requesting IP

        # Request specific fields for efficiency
        params = {
            "fields": "status,message,country,countryCode,region,regionName,city,lat,lon,timezone"
        }

        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()

        data = response.json()

        # Check if request was successful
        if data.get("status") != "success":
            logger.warning(f"IP geolocation failed: {data.get('message', 'Unknown error')}")
            return None

        # Build location context
        location_context = {
            "country": data.get("country", ""),
            "country_code": data.get("countryCode", ""),
            "city": data.get("city", ""),
            "region": data.get("regionName", ""),
            "latitude": data.get("lat"),
            "longitude": data.get("lon"),
            "timezone": data.get("timezone", "")
        }

        logger.info(f"Location detected: {location_context['city']}, {location_context['country']}")
        return location_context

    except requests.exceptions.Timeout:
        logger.error("IP geolocation request timed out")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"IP geolocation request failed: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in IP geolocation: {str(e)}")
        return None


def get_location_from_request_headers(headers: Dict[str, str]) -> Optional[Dict[str, str]]:
    """
    Extract IP from request headers and get location.

    Common headers to check (in order of preference):
    - X-Forwarded-For: Set by proxies/load balancers (most common)
    - X-Real-IP: Set by nginx
    - CF-Connecting-IP: Set by Cloudflare
    - X-Client-IP: Set by some proxies

    Args:
        headers: Request headers dict (case-insensitive)

    Returns:
        Location context dict or None
    """
    # Normalize headers to lowercase for case-insensitive lookup
    headers_lower = {k.lower(): v for k, v in headers.items()}

    # Try different header names in order of preference
    ip_headers = [
        'x-forwarded-for',
        'x-real-ip',
        'cf-connecting-ip',
        'x-client-ip'
    ]

    ip_address = None
    for header in ip_headers:
        if header in headers_lower:
            # X-Forwarded-For can contain multiple IPs, take the first (client IP)
            ip_value = headers_lower[header]
            ip_address = ip_value.split(',')[0].strip()
            logger.info(f"Extracted IP {ip_address} from header {header}")
            break

    if not ip_address:
        logger.warning("Could not extract IP from request headers")
        return None

    return get_location_from_ip(ip_address)


# Cache for location lookups to avoid repeated API calls
# Format: {ip_address: (location_context, timestamp)}
_location_cache = {}
_CACHE_TTL = 3600  # Cache for 1 hour


def get_location_cached(ip_address: Optional[str] = None) -> Optional[Dict[str, str]]:
    """
    Get location with caching to reduce API calls.

    Args:
        ip_address: IP address to geolocate

    Returns:
        Location context dict or None
    """
    import time

    cache_key = ip_address or "auto"

    # Check cache
    if cache_key in _location_cache:
        cached_location, timestamp = _location_cache[cache_key]
        if time.time() - timestamp < _CACHE_TTL:
            logger.info(f"Using cached location for {cache_key}")
            return cached_location
        else:
            # Cache expired
            del _location_cache[cache_key]

    # Fetch new location
    location = get_location_from_ip(ip_address)

    if location:
        _location_cache[cache_key] = (location, time.time())

    return location
