#!/usr/bin/env python3
"""
Retry Handler - Intelligent retry logic for Fabric API calls
Handles transient errors with exponential backoff
"""

import time
import urllib.error
import json


class RetryHandler:
    """
    Handles retries for transient errors with exponential backoff.

    Retries automatically for:
    - 429 Too Many Requests (rate limiting)
    - 500 Internal Server Error
    - 503 Service Unavailable
    - Network timeouts
    """

    def __init__(self, max_retries=3, initial_delay=1.0, max_delay=30.0, verbose=False):
        """
        Initialize retry handler.

        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds before first retry
            max_delay: Maximum delay in seconds between retries
            verbose: Enable debug logging
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.verbose = verbose

    def log(self, message):
        """Log message if verbose mode enabled"""
        if self.verbose:
            print(f"[RETRY] {message}")

    def should_retry(self, error):
        """
        Determine if an error should be retried.

        Args:
            error: Exception that occurred

        Returns:
            tuple: (should_retry, retry_after_seconds)
        """
        # HTTP errors
        if isinstance(error, urllib.error.HTTPError):
            # Rate limiting - check Retry-After header
            if error.code == 429:
                retry_after = error.headers.get('Retry-After')
                if retry_after:
                    try:
                        wait_time = int(retry_after)
                        self.log(f"Rate limited, Retry-After: {wait_time}s")
                        return True, wait_time
                    except:
                        pass
                return True, None

            # Server errors - these are often transient
            if error.code in [500, 502, 503, 504]:
                self.log(f"Server error {error.code}, will retry")
                return True, None

            # Token expired - should refresh token, not retry
            if error.code == 401:
                self.log("401 Unauthorized - token refresh needed, not retrying")
                return False, None

            # Client errors - don't retry
            if 400 <= error.code < 500:
                self.log(f"Client error {error.code}, not retrying")
                return False, None

        # URL errors (connection issues)
        if isinstance(error, urllib.error.URLError):
            self.log("Network error, will retry")
            return True, None

        # Timeout errors
        if isinstance(error, TimeoutError):
            self.log("Timeout, will retry")
            return True, None

        # Default: don't retry
        return False, None

    def execute_with_retry(self, func, *args, **kwargs):
        """
        Execute a function with automatic retry on transient errors.

        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result of func() if successful

        Raises:
            Last exception if all retries exhausted

        Example:
            retry = RetryHandler(max_retries=3)
            result = retry.execute_with_retry(my_api_call, workspace_id, param1)
        """
        attempt = 0
        delay = self.initial_delay

        while True:
            try:
                # Execute the function
                result = func(*args, **kwargs)
                if attempt > 0:
                    self.log(f"Success after {attempt} retries")
                return result

            except Exception as e:
                attempt += 1

                # Check if we should retry
                should_retry, retry_after = self.should_retry(e)

                if not should_retry:
                    # Not a retryable error, re-raise immediately
                    raise

                if attempt > self.max_retries:
                    # Max retries exhausted
                    self.log(f"Max retries ({self.max_retries}) exhausted")
                    raise

                # Calculate wait time
                if retry_after is not None:
                    wait_time = min(retry_after, self.max_delay)
                else:
                    # Exponential backoff: 1s, 2s, 4s, 8s, ...
                    wait_time = min(delay * (2 ** (attempt - 1)), self.max_delay)

                self.log(f"Attempt {attempt}/{self.max_retries} failed, waiting {wait_time:.1f}s...")

                # Show user-friendly message for longer waits
                if wait_time > 5:
                    print(f"[INFO] API rate limited, waiting {wait_time:.0f}s before retry...")

                time.sleep(wait_time)


def with_retry(max_retries=3, initial_delay=1.0, max_delay=30.0, verbose=False):
    """
    Decorator to add retry logic to a function.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        verbose: Enable debug logging

    Example:
        @with_retry(max_retries=3, verbose=True)
        def fetch_workspace(workspace_id):
            # ... API call ...
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            handler = RetryHandler(
                max_retries=max_retries,
                initial_delay=initial_delay,
                max_delay=max_delay,
                verbose=verbose
            )
            return handler.execute_with_retry(func, *args, **kwargs)
        return wrapper
    return decorator


# Convenience function for one-off retries
def retry_on_transient_error(func, *args, max_retries=3, verbose=False, **kwargs):
    """
    Execute a function with retry on transient errors.

    Args:
        func: Function to execute
        *args: Positional arguments for func
        max_retries: Maximum retry attempts
        verbose: Enable debug logging
        **kwargs: Keyword arguments for func

    Returns:
        Result of func() if successful

    Example:
        result = retry_on_transient_error(
            my_api_call,
            workspace_id,
            param1,
            max_retries=5,
            verbose=True
        )
    """
    handler = RetryHandler(max_retries=max_retries, verbose=verbose)
    return handler.execute_with_retry(func, *args, **kwargs)
