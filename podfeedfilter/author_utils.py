"""Robust author information extraction utilities for RSS feeds.

This module handles various author field formats found in RSS feeds,
including simple strings, email formats, dictionary structures, and lists.
Provides backward compatibility while enabling future extensions.
"""
from __future__ import annotations
import logging
import re
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

AuthorDict = Dict[str, str]
AuthorList = List[AuthorDict]


def _parse_email_author_format(author_string: str) -> AuthorDict:
    """Parse RSS author string in 'email (name)' or 'email' format.
    
    Args:
        author_string: String like 'john@example.com (John Doe)' or 'john@example.com'
        
    Returns:
        Dictionary with 'name' and/or 'email' keys
    """
    # Pattern to match 'email (name)' format
    email_name_pattern = r'^([^@\s]+@[^@\s]+)\s*\(([^)]+)\)$'
    match = re.match(email_name_pattern, author_string.strip())
    
    if match:
        email, name = match.groups()
        return {
            'name': name.strip(),
            'email': email.strip()
        }
    
    # Check if it's just an email address
    email_pattern = r'^[^@\s]+@[^@\s]+$'
    if re.match(email_pattern, author_string.strip()):
        return {'email': author_string.strip()}
    
    # Otherwise, treat as plain name
    return {'name': author_string.strip()}


def _normalize_author_dict(author_data: Dict[str, Any]) -> Optional[AuthorDict]:
    """Normalize a dictionary-like author object to standard format.
    
    Args:
        author_data: Dictionary containing author information
        
    Returns:
        Normalized author dictionary or None if invalid
    """
    if not isinstance(author_data, dict):
        return None
    
    result = {}
    
    # Extract name from various possible keys
    name_keys = ['name', 'title', 'displayName', 'full_name', 'author_name']
    for key in name_keys:
        if key in author_data and author_data[key]:
            result['name'] = str(author_data[key]).strip()
            break
    
    # Extract email from various possible keys  
    email_keys = ['email', 'email_address', 'author_email', 'mail']
    for key in email_keys:
        if key in author_data and author_data[key]:
            email_str = str(author_data[key]).strip()
            if '@' in email_str:  # Basic email validation
                result['email'] = email_str
                break
    
    # Return None if no useful information found
    if not result:
        return None
        
    return result


def _extract_single_author(author_input: Any) -> Optional[AuthorDict]:
    """Extract author information from a single input value.
    
    Args:
        author_input: Single author value (string, dict, etc.)
        
    Returns:
        Normalized author dictionary or None if invalid
    """
    if author_input is None:
        return None
    
    # Handle string inputs (most common case)
    if isinstance(author_input, str):
        author_string = author_input.strip()
        if not author_string:
            return None
        return _parse_email_author_format(author_string)
    
    # Handle dictionary inputs
    if isinstance(author_input, dict):
        return _normalize_author_dict(author_input)
    
    # Handle other types by converting to string
    try:
        author_string = str(author_input).strip()
        # Filter out common non-useful string conversions
        if author_string and author_string not in ('None', '[]', '{}', '()', 'True', 'False'):
            return _parse_email_author_format(author_string)
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to convert author input to string: {e}")
        return None
    
    return None


def extract_authors(entry: Dict[str, Any]) -> AuthorList:
    """Extract all author information from a feedparser entry.
    
    This function provides robust handling of various author field formats
    found in RSS feeds, including:
    - Simple strings: "John Doe"
    - Email formats: "john@example.com (John Doe)" or "john@example.com"
    - Dictionary objects with name/email keys
    - Lists of any of the above formats
    - Alternative field names like 'authors' instead of 'author'
    
    Args:
        entry: feedparser.FeedParserDict or similar dictionary
        
    Returns:
        List of normalized author dictionaries with 'name' and/or 'email' keys.
        Returns empty list if no valid authors found.
        
    Example:
        >>> entry = {'author': 'john@example.com (John Doe)'}
        >>> extract_authors(entry)
        [{'name': 'John Doe', 'email': 'john@example.com'}]
        
        >>> entry = {'authors': [{'name': 'Jane'}, 'bob@example.com']}
        >>> extract_authors(entry)
        [{'name': 'Jane'}, {'email': 'bob@example.com'}]
    """
    authors: AuthorList = []
    
    # Check various author field names in priority order
    author_fields = ['author', 'authors', 'dc_creator', 'creator']
    
    for field_name in author_fields:
        if field_name not in entry:
            continue
            
        raw_authors = entry[field_name]
        
        # Handle list/tuple of authors
        if isinstance(raw_authors, (list, tuple)):
            for author_item in raw_authors:
                extracted = _extract_single_author(author_item)
                if extracted:
                    authors.append(extracted)
        else:
            # Handle single author
            extracted = _extract_single_author(raw_authors)
            if extracted:
                authors.append(extracted)
        
        # If we found authors in this field, don't check other fields
        if authors:
            break
    
    return authors


def get_primary_author(entry: Dict[str, Any]) -> Optional[AuthorDict]:
    """Get the primary (first) author from an entry.
    
    Convenience function that returns just the first author found,
    which maintains backward compatibility for code expecting a single author.
    
    Args:
        entry: feedparser.FeedParserDict or similar dictionary
        
    Returns:
        First author dictionary or None if no authors found
    """
    authors = extract_authors(entry)
    return authors[0] if authors else None


def format_author_for_display(author: AuthorDict) -> str:
    """Format an author dictionary for display purposes.
    
    Args:
        author: Author dictionary with 'name' and/or 'email' keys
        
    Returns:
        Human-readable author string
    """
    name = author.get('name', '')
    email = author.get('email', '')
    
    if name and email:
        return f"{name} <{email}>"
    elif name:
        return name
    elif email:
        return email
    else:
        return "Unknown Author"
