#!/usr/bin/env python3
"""
Result Sanitizer - Mask sensitive data and apply limits.
"""

import re
from typing import Any, Dict, List, Optional


class Sanitizer:
    """Sanitizes results to prevent data leakage."""

    # Patterns for sensitive data
    PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b\d{10,}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\b',
        'token_bearer': r'(Bearer|bearer)\s+[A-Za-z0-9\-._~+/]+=*',
        'token_jwt': r'eyJ[A-Za-z0-9\-_]+\.eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+',
    }

    @staticmethod
    def mask_tokens(text: str) -> str:
        """Mask authentication tokens in text."""
        if not isinstance(text, str):
            return text

        # Mask Bearer tokens
        text = re.sub(
            Sanitizer.PATTERNS['token_bearer'],
            r'\1 ***MASKED***',
            text
        )

        # Mask JWT tokens
        text = re.sub(
            Sanitizer.PATTERNS['token_jwt'],
            '***MASKED_JWT***',
            text
        )

        # Mask access_token fields in JSON
        text = re.sub(
            r'"access_token"\s*:\s*"[^"]*"',
            '"access_token": "***MASKED***"',
            text
        )

        # Mask refresh_token fields
        text = re.sub(
            r'"refresh_token"\s*:\s*"[^"]*"',
            '"refresh_token": "***MASKED***"',
            text
        )

        return text

    @staticmethod
    def truncate_results(data: List[Dict], max_rows: int, operation: str = "query") -> List[Dict]:
        """Truncate result set to max_rows."""
        if max_rows is None or len(data) <= max_rows:
            return data

        print(f"\n[INFO] Results truncated to {max_rows} rows (total: {len(data)} rows)")
        print(f"[INFO] Truncation applied for security policy compliance")
        return data[:max_rows]

    @staticmethod
    def sanitize_error_message(error_msg: str) -> str:
        """Remove sensitive information from error messages."""
        # Mask tokens in errors
        error_msg = Sanitizer.mask_tokens(error_msg)

        # Mask connection strings
        error_msg = re.sub(
            r'(Server|Host|Database|User|Password|PWD|UID)\s*=\s*[^;]+',
            r'\1=***MASKED***',
            error_msg,
            flags=re.IGNORECASE
        )

        return error_msg


def mask_tokens_in_output(text: str) -> str:
    """Convenience function to mask tokens."""
    return Sanitizer.mask_tokens(text)


def apply_row_limit(data: List[Dict], max_rows: Optional[int], operation: str = "query") -> List[Dict]:
    """Apply row limit if configured."""
    if max_rows is None:
        return data

    return Sanitizer.truncate_results(data, max_rows, operation)
