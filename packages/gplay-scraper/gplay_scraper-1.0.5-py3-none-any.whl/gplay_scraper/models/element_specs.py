"""Element specifications for data extraction from Google Play Store.

This module defines ElementSpec class and ElementSpecs for all 7 method types.
Each spec defines how to extract specific fields from raw JSON data.
"""

from typing import Any, Callable, List, Optional, Dict, Union
import html
from datetime import datetime
from ..utils.helpers import unescape_text
from ..config import Config


def parse_permissions(perms_data: Any) -> Dict[str, List[str]]:
    """Parse permissions from various Google Play Store data formats.
    
    Google Play Store uses complex nested data structures for app permissions.
    This function handles all known formats and extracts human-readable permission
    descriptions organized by category.
    
    Data Structure Patterns:
        - Format 1: [[[category, [...], [[null, description]], [...]]]] 
        - Format 2: [[category, [...], [description1, description2]]]
        - Format 3: Mixed with "Other" category for uncategorized permissions
        - Format 4: Empty/null data for apps with no permissions
    
    Args:
        perms_data: Raw permissions data from Play Store JSON (nested lists/dicts)
        
    Returns:
        Dictionary mapping permission categories to lists of permission descriptions
        Example: {"Location": ["GPS access"], "Storage": ["Read files", "Write files"]}
        
    Examples:
        >>> parse_permissions(None)
        {}
        >>> parse_permissions([[[["Location", [...], [[null, "GPS access"]], [...]]]])
        {"Location": ["GPS access"]}
        >>> parse_permissions([["Storage", [...], ["Read files", "Write files"]]])
        {"Storage": ["Read files", "Write files"]}
    """
    if not perms_data:
        return {}
    
    permissions = {}
    
    try:
        if isinstance(perms_data, list) and len(perms_data) > 2:
            sections = perms_data[2] if len(perms_data) > 2 else []
            if isinstance(sections, list):
                for section in sections:
                    if not isinstance(section, list):
                        continue
                    for perm_group in section:
                        if not isinstance(perm_group, list) or len(perm_group) < 3:
                            continue
                        category = None
                        if isinstance(perm_group[0], str):
                            category = perm_group[0]
                        elif isinstance(perm_group[0], list) and len(perm_group[0]) > 0:
                            category = perm_group[0][0] if isinstance(perm_group[0][0], str) else "Other"
                        if not category:
                            category = "Other"
                        details = []
                        perm_details = perm_group[2] if len(perm_group) > 2 else []
                        if isinstance(perm_details, list):
                            for detail in perm_details:
                                if isinstance(detail, list) and len(detail) > 1:
                                    if detail[1] and isinstance(detail[1], str):
                                        details.append(detail[1])
                                elif isinstance(detail, str):
                                    details.append(detail)
                        if details:
                            if category in permissions:
                                permissions[category].extend(details)
                            else:
                                permissions[category] = details
                if len(sections) > 2:
                    additional_perms = sections[2] if len(sections) > 2 else []
                    if isinstance(additional_perms, list):
                        other_perms = []
                        for item in additional_perms:
                            if isinstance(item, list) and len(item) > 1 and isinstance(item[1], str):
                                other_perms.append(item[1])
                        if other_perms:
                            if "Other" in permissions:
                                permissions["Other"].extend(other_perms)
                            else:
                                permissions["Other"] = other_perms
        elif isinstance(perms_data, list):
            for item in perms_data:
                if isinstance(item, list) and len(item) > 2:
                    category = item[0] if isinstance(item[0], str) else "Other"
                    details = []
                    if isinstance(item[2], list):
                        for detail in item[2]:
                            if isinstance(detail, list) and len(detail) > 1 and isinstance(detail[1], str):
                                details.append(detail[1])
                    if details:
                        permissions[category] = details
        permissions = {k: v for k, v in permissions.items() if v}
    except (IndexError, KeyError, TypeError, AttributeError):
        pass
    
    return permissions


def nested_lookup(obj: Any, key_list: List) -> Any:
    """Safely navigate nested dictionary/list structure.
    
    Traverses complex nested data structures (mix of dicts and lists) following
    a path of keys/indices. Returns None if any step in the path fails.
    
    Args:
        obj: Object to navigate (dict, list, or any nested structure)
        key_list: List of keys/indices to follow (e.g., [0, 'data', 1, 'title'])
        
    Returns:
        Value at the nested location or None if path doesn't exist
        
    Examples:
        >>> data = {'users': [{'name': 'John'}, {'name': 'Jane'}]}
        >>> nested_lookup(data, ['users', 1, 'name'])
        'Jane'
        >>> nested_lookup(data, ['users', 5, 'name'])  # Index out of range
        None
        >>> nested_lookup(data, ['invalid', 'path'])
        None
    """
    current = obj
    for key in key_list:
        try:
            current = current[key]
        except (IndexError, KeyError, TypeError):
            return None
    return current


def format_image_url(url: str, size: str = None) -> str:
    """Format image URL with size parameter.
    
    Google Play Store images can be resized by appending size parameters.
    This function adds the appropriate size parameter to get images in desired resolution.
    
    Args:
        url: Base image URL from Google Play Store
        size: Size parameter - SMALL (512px), MEDIUM (1024px), LARGE (2048px), ORIGINAL (max)
        
    Returns:
        Formatted URL with size parameter appended, or None if url is empty
        
    Examples:
        >>> format_image_url('https://play-lh.googleusercontent.com/abc123', 'LARGE')
        'https://play-lh.googleusercontent.com/abc123=w2048'
        >>> format_image_url('https://example.com/image.jpg', 'SMALL')
        'https://example.com/image.jpg=w512'
        >>> format_image_url('', 'LARGE')
        None
    """
    if not url:
        return None
    size_param = Config.get_image_size(size)
    return f"{url}={size_param}"


class ElementSpec:
    """Specification for extracting a single field from raw data.
    
    Defines how to extract a specific piece of information from Google Play Store's
    complex nested JSON data structures. Each spec contains a navigation path and
    optional processing logic.
    
    The extraction process:
        1. Navigate through nested data using data_map path
        2. Apply post_processor function if specified
        3. Return fallback_value if extraction fails
        4. Handle asset sizing for image URLs
    
    Attributes:
        ds_num: Dataset number (legacy, kept for compatibility)
        data_map: List of keys/indices to navigate to the field (e.g., [1, 2, 0, 0])
        post_processor: Optional function to process extracted value (e.g., unescape_text)
        fallback_value: Value to return if extraction fails (can be another ElementSpec)
        assets: Asset size parameter for image URLs
        
    Examples:
        # Simple field extraction
        title_spec = ElementSpec("raw", [1, 2, 0, 0])
        
        # With post-processing
        price_spec = ElementSpec("raw", [1, 2, 57, 0], lambda x: x / 1000000)
        
        # With fallback
        version_spec = ElementSpec("raw", [1, 2, 140, 0], fallback_value="Unknown")
    """
    
    def __init__(
        self,
        ds_num: Optional[int],
        data_map: List[int],
        post_processor: Callable = None,
        fallback_value: Any = None,
        assets: str = None,
    ):
        """Initialize ElementSpec with extraction parameters."""
        self.ds_num = ds_num
        self.data_map = data_map
        self.post_processor = post_processor
        self.fallback_value = fallback_value
        self.assets = assets

    def extract_content(self, source: dict, assets: str = None) -> Any:
        """Extract content from source using data_map.
        
        Performs the actual data extraction by following the navigation path,
        applying post-processing, and handling fallbacks.
        
        Args:
            source: Source dictionary/list (Google Play Store JSON data)
            assets: Override asset size for this extraction (SMALL, MEDIUM, LARGE, ORIGINAL)
            
        Returns:
            Extracted and processed value, or fallback_value if extraction fails
            
        Process:
            1. Navigate through source data using data_map path
            2. Apply post_processor function if available
            3. Handle image URL formatting for asset-related fields
            4. Return fallback_value if any step fails
            
        Examples:
            >>> spec = ElementSpec("raw", [1, 2, 0, 0])
            >>> spec.extract_content({'1': {'2': [['App Title']]})
            'App Title'
            >>> spec.extract_content({'invalid': 'data'})
            None  # or fallback_value if specified
        """
        try:
            result = nested_lookup(source, self.data_map)
            
            if self.post_processor is not None:
                try:
                    if hasattr(self.post_processor, '__name__') and 'image' in self.post_processor.__name__:
                        result = self.post_processor(result, assets or self.assets)
                    else:
                        result = self.post_processor(result)
                except Exception:
                    pass
        except (KeyError, IndexError, TypeError, AttributeError):
            result = None
            
        if result is None and self.fallback_value is not None:
            if isinstance(self.fallback_value, ElementSpec):
                result = self.fallback_value.extract_content(source, assets)
            else:
                result = self.fallback_value
        return result


class ElementSpecs:
    """Collection of element specifications for all method types.
    
    Central registry of data extraction specifications for all Google Play Store
    data types. Each specification defines exactly how to extract specific fields
    from the complex nested JSON structures returned by Google's APIs.
    
    Data Categories:
        - App: 65+ fields for complete app details (ratings, installs, permissions, etc.)
        - Search: Fields for search results (title, developer, price, etc.)
        - Review: Fields for user reviews (content, rating, timestamp, etc.)
        - Developer: Fields for developer app listings
        - Similar: Fields for similar/related apps
        - List: Fields for top chart apps (rankings, categories, etc.)
        
    Usage Pattern:
        Each category contains ElementSpec objects that define:
        - Navigation path through JSON data
        - Post-processing functions for data transformation
        - Fallback values for missing data
        - Asset sizing for images
        
    Example:
        >>> app_title = ElementSpecs.App['title'].extract_content(app_data)
        >>> search_results = [ElementSpecs.Search['title'].extract_content(item) for item in results]
    """
    # App Data Specifications - 65+ fields for complete app analysis
    App = {
        "title": ElementSpec("raw", [1, 2, 0, 0]),
        "description": ElementSpec(
            "raw",
            [1, 2],
            lambda s: (lambda desc_text: unescape_text(desc_text) if desc_text else None)(
                nested_lookup(s, [72, 0, 0]) or nested_lookup(s, [72, 0, 1])
            ),
        ),
        "summary": ElementSpec("raw", [1, 2, 73, 0, 1], unescape_text),
        "installs": ElementSpec("raw", [1, 2, 13, 0]),
        "minInstalls": ElementSpec("raw", [1, 2, 13, 1]),
        "realInstalls": ElementSpec("raw", [1, 2, 13, 2]),
        "score": ElementSpec("raw", [1, 2, 51, 0, 1]),
        "ratings": ElementSpec("raw", [1, 2, 51, 2, 1]),
        "reviews": ElementSpec("raw", [1, 2, 51, 3, 1]),
        "histogram": ElementSpec(
            "raw",
            [1, 2, 51, 1],
            lambda container: [
                container[1][1],
                container[2][1],
                container[3][1],
                container[4][1],
                container[5][1],
            ],
            [0, 0, 0, 0, 0], 
        ),
        "price": ElementSpec(
            "raw", [1, 2, 57, 0, 0, 0, 0, 1, 0, 0], 
            lambda price: (price / 1000000) or 0 
        ),
        "free": ElementSpec("raw", [1, 2, 57, 0, 0, 0, 0, 1, 0, 0], lambda s: s == 0), 
        "currency": ElementSpec("raw", [1, 2, 57, 0, 0, 0, 0, 1, 0, 1]),
        "sale": ElementSpec("raw", [1, 2, 57, 0, 0, 0, 0, 14, 0, 0], bool, False),
        "originalPrice": ElementSpec("raw", [1, 2, 57, 0, 0, 0, 0, 1, 1, 0], lambda price: (price / 1000000) if price else None),
        "offersIAP": ElementSpec("raw", [1, 2, 19, 0], bool, False),
        "inAppProductPrice": ElementSpec("raw", [1, 2, 19, 0]),
        "developer": ElementSpec("raw", [1, 2, 68, 0]),
        "developerId": ElementSpec("raw", [1, 2, 68, 1, 4, 2], lambda s: s.split("id=")[1] if s and "id=" in s else None),
        "developerEmail": ElementSpec("raw", [1, 2, 69, 1, 0]),
        "developerWebsite": ElementSpec("raw", [1, 2, 69, 0, 5, 2]),
        "developerAddress": ElementSpec("raw", [1, 2, 69, 4, 2, 0]),
        "developerPhone": ElementSpec("raw", [1, 2, 69, 4, 3]),
        "privacyPolicy": ElementSpec("raw", [1, 2, 99, 0, 5, 2]),
        "genre": ElementSpec("raw", [1, 2, 79, 0, 0, 0]),
        "genreId": ElementSpec("raw", [1, 2, 79, 0, 0, 2]),
        "categories": ElementSpec("raw", [1, 2, 79, 0, 0, 0], lambda cat: [cat] if cat else [], []),
        "icon": ElementSpec("raw", [1, 2, 95, 0, 3, 2]),
        "headerImage": ElementSpec("raw", [1, 2, 96, 0, 3, 2]),
        "screenshots": ElementSpec("raw", [1, 2, 78, 0], lambda container: [item[3][2] for item in container] if container else [], []),
        "video": ElementSpec("raw", [1, 2, 100, 0, 0, 3, 2]),
        "videoImage": ElementSpec("raw", [1, 2, 100, 1, 0, 3, 2]),
        "contentRating": ElementSpec("raw", [1, 2, 9, 0]),
        "contentRatingDescription": ElementSpec("raw", [1, 2, 9, 6, 1], fallback_value=ElementSpec("raw", [1, 2, 9, 2, 1], fallback_value=ElementSpec("raw", [1, 2, 9, 0]))),
        "appId": ElementSpec("raw", [1, 2, 1, 0, 0]),
        "adSupported": ElementSpec("raw", [1, 2, 48], bool),
        "containsAds": ElementSpec("raw", [1, 2, 48], bool, False),
        "released": ElementSpec("raw", [1, 2, 10, 0]),
        "updated": ElementSpec("raw", [1, 2, 145, 0, 1, 0], fallback_value=ElementSpec("raw", [1, 2, 103, "146", 0, 0], fallback_value=ElementSpec("raw", [1, 2, 145, 0, 0], fallback_value=ElementSpec("raw", [1, 2, 112, "146", 0, 0], fallback_value=ElementSpec("raw", [1, 2, 103, "146", 0, 1,0], fallback_value="Never updated"))))),
        "version": ElementSpec("raw", [1, 2, 140, 0, 0, 0], fallback_value=ElementSpec("raw", [1, 2, 103, "141", 0, 0, 0], fallback_value="Varies with device")),
        "androidVersion": ElementSpec("raw", [1, 2, 140, 1, 1, 0, 0, 1], fallback_value=ElementSpec("raw", [1, 2, 103, "155", 1, 2], fallback_value=ElementSpec("raw", [1, 2, 112, "141", 1, 1, 0, 0, 0], fallback_value="Varies with device"))),
        "permissions": ElementSpec("raw", [1, 2, 74], parse_permissions),
        "dataSafety": ElementSpec("raw", [1, 2, 136], lambda data: [item[1] for item in data[1] if item and len(item) > 1] if data and len(data) > 1 and data[1] else []),
        "appBundle": ElementSpec("raw", [1, 2, 77, 0]),
        "maxandroidapi": ElementSpec("raw", [1, 2, 140, 1, 0, 0, 0], fallback_value=ElementSpec("raw", [1, 2, 103, "141", 1, 0 , 0, 0], fallback_value=ElementSpec("raw", [1, 2, 112, "141", 1, 0, 0, 0], fallback_value="Varies with device"))),
        "minandroidapi": ElementSpec("raw", [1, 2, 140, 1, 1, 0, 0, 0], fallback_value=ElementSpec("raw", [1, 2, 103, "141", 1, 1, 0, 0, 0], fallback_value=ElementSpec("raw", [1, 2, 112, "141", 1, 1, 0, 0, 0], fallback_value="Varies with device"))),
        "whatsNew": ElementSpec("raw", [1, 2, 144, 1, 1], lambda x: [line.strip() for line in html.unescape(x).split('<br>') if line.strip()] if x else []),
        "available": ElementSpec("raw", [1, 2, 18, 0], bool, False),
        "url": ElementSpec("raw", [1, 2, 1, 0, 0], lambda app_id: f"https://play.google.com/store/apps/details?id={app_id}" if app_id else None),
    }
    
    # Search Results Specifications - Fields for app search results
    Search = {
        "title": ElementSpec("raw", [2]),
        "appId": ElementSpec("raw", [12, 0]),
        "icon": ElementSpec("raw", [1, 1, 0, 3, 2]),
        "developer": ElementSpec("raw", [4, 0, 0, 0]),
        "currency": ElementSpec("raw", [7, 0, 3, 2, 1, 0, 1]),
        "price": ElementSpec("raw", [7, 0, 3, 2, 1, 0, 0], lambda price: (price / 1000000) if price else 0),
        "free": ElementSpec("raw", [7, 0, 3, 2, 1, 0, 0], lambda s: s == 0),
        "summary": ElementSpec("raw", [4, 1, 1, 1, 1], unescape_text),
        "scoreText": ElementSpec("raw", [6, 0, 2, 1, 0]),
        "score": ElementSpec("raw", [6, 0, 2, 1, 1]),
        "url": ElementSpec("raw", [12, 0], lambda app_id: f"https://play.google.com/store/apps/details?id={app_id}" if app_id else None),
    }
    
    # Review Data Specifications - Fields for user reviews
    Review = {
        "reviewId": ElementSpec("raw", [0]), 
        "userName": ElementSpec("raw", [1, 0]), 
        "userImage": ElementSpec("raw", [1, 1, 3, 2]),
        "content": ElementSpec("raw", [4], unescape_text),
        "score": ElementSpec("raw", [2]),
        "thumbsUpCount": ElementSpec("raw", [6]),
        "at": ElementSpec("raw", [5, 0], lambda timestamp: datetime.fromtimestamp(timestamp).isoformat() if timestamp else None),
        "appVersion": ElementSpec("raw", [10]),
    }
    
    # Developer App Specifications - Fields for developer's app listings
    Developer = {
        "appId": ElementSpec("raw", [0, 0]),
        "title": ElementSpec("raw", [3]), 
        "icon": ElementSpec("raw", [1, 3, 2]),
        "developer": ElementSpec("raw", [14]),
        "description": ElementSpec("raw", [13, 1], unescape_text),
        "score": ElementSpec("raw", [4, 1]),
        "scoreText": ElementSpec("raw", [4, 0]),
        "price": ElementSpec("raw", [8, 1, 0, 0], lambda price: (price / 1000000) if price else 0),
        "currency": ElementSpec("raw", [8, 1, 0, 1]),
        "free": ElementSpec("raw", [8, 1, 0, 0], lambda s: s == 0),
        "url": ElementSpec("raw", [10, 4, 2], lambda path: f"https://play.google.com{path}" if path else None),
    }
    
    # Similar Apps Specifications - Fields for related/similar apps
    Similar = {
        "appId": ElementSpec("raw", [0, 0]), 
        "title": ElementSpec("raw", [3]),
        "icon": ElementSpec("raw", [1, 3, 2]),
        "developer": ElementSpec("raw", [14]),
        "description": ElementSpec("raw", [13, 1], unescape_text),
        "score": ElementSpec("raw", [4, 1]),
        "scoreText": ElementSpec("raw", [4, 0]),
        "price": ElementSpec("raw", [8, 1, 0, 0], lambda price: (price / 1000000) if price else 0),
        "currency": ElementSpec("raw", [8, 1, 0, 1]),
        "free": ElementSpec("raw", [8, 1, 0, 0], lambda s: s == 0),
        "url": ElementSpec("raw", [10, 4, 2], lambda path: f"https://play.google.com{path}" if path else None),
    }
    
    # Top Charts Specifications - Fields for ranked app lists
    List = {
        "title": ElementSpec("raw", [0, 3]),
        "appId": ElementSpec("raw", [0, 0, 0]), 
        "icon": ElementSpec("raw", [0, 1, 3, 2]),
        "screenshots": ElementSpec("raw", [0, 2], lambda container: [s[3][2] for s in container if s and len(s) > 3] if container else [], []),
        "developer": ElementSpec("raw", [0, 14]),
        "genre": ElementSpec("raw", [0, 5]),
        "installs": ElementSpec("raw", [0, 15]),
        "currency": ElementSpec("raw", [0, 8, 1, 0, 1]),
        "price": ElementSpec("raw", [0, 8, 1, 0, 0], lambda price: (price / 1000000) if price else 0),
        "free": ElementSpec("raw", [0, 8, 1, 0, 0], lambda s: s == 0),
        "description": ElementSpec("raw", [0, 13, 1], unescape_text),
        "scoreText": ElementSpec("raw", [0, 4, 0]),
        "score": ElementSpec("raw", [0, 4, 1]),
        "url": ElementSpec("raw", [0, 10, 4, 2], lambda path: f"https://play.google.com{path}" if path else None),
    }