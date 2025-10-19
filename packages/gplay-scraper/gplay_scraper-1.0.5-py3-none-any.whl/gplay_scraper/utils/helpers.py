"""Helper functions for data processing and manipulation.

This module contains utility functions for:
- Text unescaping and cleaning
- JSON string cleaning
- Date parsing and calculations
- Install metrics calculations
"""

import re
import json
import os
from html import unescape
from typing import Any, List, Optional, Dict
from datetime import datetime, timezone

from urllib.parse import urlparse
from .constants import PHONE_PREFIXES

def unescape_text(s: Optional[str]) -> Optional[str]:
    """Unescape HTML entities and remove HTML tags from text.
    
    Args:
        s: Input string with HTML
        
    Returns:
        Cleaned text without HTML tags
    """
    if s is None:
        return None
    
    text = s.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    text = text.replace("<b>", "").replace("</b>", "")
    text = text.replace("<i>", "").replace("</i>", "")
    text = text.replace("<u>", "").replace("</u>", "")
    text = text.replace("<strong>", "").replace("</strong>", "")
    text = text.replace("<em>", "").replace("</em>", "")
    
    text = re.sub(r'<[^>]+>', '', text)
    
    return unescape(text).strip()


def clean_json_string(json_str: str) -> str:
    """Clean malformed JSON string from Google Play Store.
    
    Args:
        json_str: Raw JSON string
        
    Returns:
        Cleaned JSON string
    """
    json_str = re.sub(r',\s*sideChannel:\s*\{\}', '', json_str)
    
    json_str = re.sub(r'([{,]\s*)([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:', r'\1"\2":', json_str)
    
    json_str = re.sub(r'\bfunction\s*\([^)]*\)\s*\{[^}]*\}', 'null', json_str)
    json_str = re.sub(r'\bundefined\b', 'null', json_str)
    
    json_str = re.sub(r":\s*'([^']*)'", r': "\1"', json_str)
    
    json_str = re.sub(r'(\])\s*(\[)', r'\1,\2', json_str)
    json_str = re.sub(r'(\})\s*(\{)', r'\1,\2', json_str)
    
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
    
    json_str = re.sub(r',,+', ',', json_str)
    
    json_str = re.sub(r':\s*\$([0-9.]+)', r': "$\1"', json_str)
    
    json_str = re.sub(r'"version"\s*:\s*([0-9.]+)(?=\s*[,}])', r'"version": "\1"', json_str)
    
    return json_str


def alternative_json_clean(json_str: str) -> str:
    """Alternative JSON cleaning method using bracket matching.
    
    Fallback method for cleaning malformed JSON when the primary cleaning fails.
    Uses bracket counting to extract valid JSON arrays from complex structures.
    
    Args:
        json_str: Raw JSON string from Google Play Store
        
    Returns:
        Cleaned JSON string ready for parsing
        
    Process:
        1. Find 'data:' marker in the string
        2. Use bracket counting to extract complete array
        3. Wrap in standard ds:5 format
        4. Apply basic cleaning as fallback
        
    Example:
        >>> alternative_json_clean('data: [1,2,3] extra content')
        '{"key": "ds:5", "hash": "13", "data": [1,2,3]}'
    """
    # Look for data array marker
    data_start = json_str.find('data:')
    if data_start != -1:
        bracket_start = json_str.find('[', data_start)
        if bracket_start != -1:
            bracket_count = 0
            pos = bracket_start
            
            # Count brackets to find complete array
            while pos < len(json_str):
                if json_str[pos] == '[':
                    bracket_count += 1
                elif json_str[pos] == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        data_end = pos + 1
                        break
                pos += 1
            
            # Extract and parse the complete array
            if bracket_count == 0:
                data_array = json_str[bracket_start:data_end]
                
                try:
                    parsed_array = json.loads(data_array)
                    
                    # Wrap in standard ds:5 format
                    return json.dumps({
                        "key": "ds:5",
                        "hash": "13",
                        "data": parsed_array
                    })
                except json.JSONDecodeError:
                    pass
    
    # Fallback: basic cleaning
    json_str = re.sub(r'\bNaN\b', 'null', json_str)
    return clean_json_string(json_str)

def parse_release_date(release_date_str: Optional[str]) -> Optional[datetime]:
    """Parse release date string to datetime object.
    
    Converts Google Play Store date format to Python datetime object
    for date calculations and comparisons.
    
    Args:
        release_date_str: Date string in format 'Mon DD, YYYY' (e.g., 'Jan 15, 2020')
        
    Returns:
        Datetime object or None if parsing fails
        
    Example:
        >>> parse_release_date('Jan 15, 2020')
        datetime.datetime(2020, 1, 15, 0, 0)
        >>> parse_release_date('invalid date')
        None
    """
    if release_date_str is None:
        return None
    try:
        # Parse Google Play Store date format
        return datetime.strptime(release_date_str, "%b %d, %Y")
    except (ValueError, TypeError):
        # Return None for invalid date formats
        return None


def calculate_app_age(release_date_str: Optional[str], current_date: datetime) -> Optional[int]:
    """Calculate app age in days since release.
    
    Computes the number of days between app release date and current date,
    useful for analyzing app maturity and growth metrics.
    
    Args:
        release_date_str: Release date string (e.g., 'Jan 15, 2020')
        current_date: Current date for calculation (usually datetime.now())
        
    Returns:
        Number of days since release (non-negative) or None if date invalid
        
    Example:
        >>> from datetime import datetime
        >>> current = datetime(2023, 1, 15)
        >>> calculate_app_age('Jan 15, 2020', current)
        1095  # 3 years = ~1095 days
    """
    release_date = parse_release_date(release_date_str)
    if release_date is None:
        return None
    
    # Handle timezone differences
    if current_date.tzinfo is not None and release_date.tzinfo is None:
        release_date = release_date.replace(tzinfo=timezone.utc)
    
    # Calculate days difference
    days_since_release = (current_date - release_date).days
    # Ensure non-negative result
    return max(0, days_since_release)


def parse_installs_string(installs_str: str) -> Optional[int]:
    """Parse install count string to integer.
    
    Converts Google Play Store install count strings (with commas and plus signs)
    to numeric values for calculations and comparisons.
    
    Args:
        installs_str: Install count string (e.g., '1,000,000+', '500,000')
        
    Returns:
        Integer install count or None if parsing fails
        
    Example:
        >>> parse_installs_string('1,000,000+')
        1000000
        >>> parse_installs_string('500,000')
        500000
        >>> parse_installs_string('invalid')
        None
    """
    if installs_str is None:
        return None
    
    # Remove formatting characters
    cleaned_str = installs_str.replace(',', '').replace('+', '')
    try:
        return int(cleaned_str)
    except (ValueError, TypeError):
        return None


def calculate_daily_installs(install_count, release_date_str: Optional[str], current_date: datetime) -> Optional[int]:
    """Calculate average daily installs since release.
    
    Computes the average number of installs per day since app release,
    providing insight into app growth rate and popularity trends.
    
    Args:
        install_count: Total install count (int or string like '1,000,000+')
        release_date_str: Release date string (e.g., 'Jan 15, 2020')
        current_date: Current date for calculation
        
    Returns:
        Average daily installs (integer) or None if calculation impossible
        
    Example:
        >>> from datetime import datetime
        >>> current = datetime(2023, 1, 15)
        >>> calculate_daily_installs(1000000, 'Jan 15, 2020', current)
        913  # ~1M installs over ~1095 days
    """
    # Convert string install count to integer if needed
    if isinstance(install_count, str):
        install_count = parse_installs_string(install_count)
    
    if install_count is None or release_date_str is None:
        return None
    
    release_date = parse_release_date(release_date_str)
    if release_date is None:
        return None
    
    # Handle timezone differences
    if current_date.tzinfo is not None and release_date.tzinfo is None:
        release_date = release_date.replace(tzinfo=timezone.utc)
    
    days_since_release = (current_date - release_date).days
    if days_since_release <= 0:
        return 0
    
    # Calculate average daily installs
    return int(install_count / days_since_release)


def calculate_monthly_installs(install_count, release_date_str: Optional[str], current_date: datetime) -> Optional[int]:
    """Calculate average monthly installs since release.
    
    Computes the average number of installs per month since app release,
    useful for understanding monthly growth patterns and trends.
    
    Args:
        install_count: Total install count (int or string like '1,000,000+')
        release_date_str: Release date string (e.g., 'Jan 15, 2020')
        current_date: Current date for calculation
        
    Returns:
        Average monthly installs (integer) or None if calculation impossible
        
    Note:
        Uses 30.44 days per month (365.25/12) for accurate monthly calculations
        
    Example:
        >>> from datetime import datetime
        >>> current = datetime(2023, 1, 15)
        >>> calculate_monthly_installs(1000000, 'Jan 15, 2020', current)
        27777  # ~1M installs over ~36 months
    """
    # Convert string install count to integer if needed
    if isinstance(install_count, str):
        install_count = parse_installs_string(install_count)
    
    if install_count is None or release_date_str is None:
        return None
    
    release_date = parse_release_date(release_date_str)
    if release_date is None:
        return None
    
    # Handle timezone differences
    if current_date.tzinfo is not None and release_date.tzinfo is None:
        release_date = release_date.replace(tzinfo=timezone.utc)
    
    days_since_release = (current_date - release_date).days
    if days_since_release <= 0:
        return 0
    
    # Convert days to months (using average month length)
    months_since_release = days_since_release / 30.44  # 365.25/12
    return int(install_count / months_since_release)


def tamp_to_date(value) -> str:
    """Convert timestamp to date format 'Jul 21, 2023' if value is a timestamp.
    
    Detects Unix timestamps and converts them to human-readable date format.
    Non-timestamp values are returned unchanged.
    
    Args:
        value: Value to check and convert (int, float, or any other type)
        
    Returns:
        Formatted date string (e.g., 'Jul 21, 2023') if timestamp, otherwise original value
        
    Example:
        >>> tamp_to_date(1642780800)
        'Jan 21, 2022'
        >>> tamp_to_date('not a timestamp')
        'not a timestamp'
    """
    # Check if value looks like a Unix timestamp (> 1 billion = after 2001)
    if isinstance(value, (int, float)) and value > 1000000000:
        try:
            dt = datetime.fromtimestamp(value)
            return dt.strftime("%b %d, %Y")
        except (ValueError, OSError):
            # Invalid timestamp, return original value
            pass
    return value


def get_publisher_country(phone: Optional[str], address: Optional[str]) -> str:
    """Determine publisher country from phone and address information.
    
    Analyzes developer contact information to determine their likely country
    of origin by extracting country codes from phone numbers and addresses.
    
    Args:
        phone: Developer phone number (e.g., '+1-555-123-4567')
        address: Developer address string (may contain country name)
        
    Returns:
        Country name(s) or 'Unknown' if cannot be determined
        
    Examples:
        >>> get_publisher_country('+1-555-123-4567', None)
        'United States'
        >>> get_publisher_country(None, 'London, UK')
        'United Kingdom'
        >>> get_publisher_country('+1-555-123', 'Berlin, Germany')
        'United States/Germany'
    """
    # Extract country codes from phone and address
    phone_code = pho_count(phone) if phone else None
    address_code = add_count(address) if address else None
    
    # Convert country codes to readable names
    code_to_name = {item[1]: item[2].title() for item in PHONE_PREFIXES}
    
    phone_country = code_to_name.get(phone_code) if phone_code else None
    address_country = code_to_name.get(address_code) if address_code else None
    
    # Determine final country based on available information
    if not phone_country and not address_country:
        return "Unknown"
    elif phone_country and not address_country:
        return phone_country
    elif address_country and not phone_country:
        return address_country
    elif phone_country == address_country:
        return phone_country
    else:
        # Different countries detected, show both
        return f"{phone_country}/{address_country}"

def add_count(address):
    """Extract country code from address string.
    
    Parses address text to find country names or codes and returns
    the corresponding country code for country identification.
    
    Args:
        address: Address string with country information (e.g., 'London, UK')
        
    Returns:
        Country code (e.g., 'gb') or None if not found
        
    Example:
        >>> add_count('123 Main St\nLondon, UK')
        'gb'
        >>> add_count('Berlin, Germany')
        'de'
        >>> add_count('Unknown location')
        None
    """
    if not address:
        return None
    
    # Split address into parts (lines)
    parts = address.split('\n')
    
    # Create lookup dictionaries from phone prefixes data
    code_to_code = {item[1].lower(): item[1] for item in PHONE_PREFIXES}
    name_to_code = {item[2].lower(): item[1] for item in PHONE_PREFIXES}
    
    # Check each part of the address for country matches
    for part in parts:
        part_lower = part.strip().lower()
        # Check for exact country code match
        if part_lower in code_to_code:
            return code_to_code[part_lower]
        # Check for country name match
        if part_lower in name_to_code:
            return name_to_code[part_lower]
    
    return None


def pho_count(phone):
    """Extract country code from phone number.
    
    Analyzes phone number format to determine the country code by matching
    against known international phone prefixes.
    
    Args:
        phone: Phone number string (e.g., '+1-555-123-4567', '44-20-1234-5678')
        
    Returns:
        Country code (e.g., 'us', 'gb') or None if not found
        
    Example:
        >>> pho_count('+1-555-123-4567')
        'us'
        >>> pho_count('44-20-1234-5678')
        'gb'
        >>> pho_count('invalid')
        None
    """
    if not isinstance(phone, str) or len(phone) < 10:
        return None
    
    # Remove leading '+' if present
    phone = phone.lstrip('+')
    
    # Create lookup dictionary from phone prefixes
    prefix_to_code = {item[0]: item[1] for item in PHONE_PREFIXES}
    
    # Handle North American numbers (starting with 1)
    if phone.startswith('1'):
        try:
            # North American numbers use 4-digit area codes
            prefix = int(phone[:4])
            return prefix_to_code.get(prefix)
        except ValueError:
            return None
    else:
        # Try different prefix lengths (longest first)
        for length in range(7, 0, -1):
            try:
                prefix = int(phone[:length])
                if prefix in prefix_to_code:
                    return prefix_to_code[prefix]
            except ValueError:
                continue
        return None



