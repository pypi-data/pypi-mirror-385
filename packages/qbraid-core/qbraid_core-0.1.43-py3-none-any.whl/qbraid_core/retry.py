# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

"""
Module containing custom ``urllib3.Retry`` class

"""

import logging

from urllib3.util.retry import Retry

STATUS_FORCELIST = (
    500,  # General server error
    502,  # Bad Gateway
    503,  # Service Unavailable
    504,  # Gateway Timeout
    520,  # Cloudflare general error
    522,  # Cloudflare connection timeout
    524,  # Cloudflare Timeout
)

logger = logging.getLogger(__name__)


class PostForcelistRetry(Retry):
    """Custom :py:class:`urllib3.Retry` class that performs retry on ``POST`` errors in the
    force list. Retrying of ``POST`` requests are allowed *only* when the status code returned
    is on the :py:const:`~qbraid_core.retry.STATUS_FORCELIST`. While ``POST`` requests are
    recommended not to be retried due to not being idempotent, retrying on specific 5xx errors
    through the qBraid API is safe.
    """

    def increment(  # type: ignore[no-untyped-def]
        self,
        method=None,
        url=None,
        response=None,
        error=None,
        _pool=None,
        _stacktrace=None,
    ):
        """Overwrites parent class increment method for logging."""
        if logger.getEffectiveLevel() is logging.DEBUG:
            # coverage: ignore
            status = data = headers = None
            if response:
                status = response.status
                data = response.data
                headers = response.headers
            logger.debug(
                "Retrying method=%s, url=%s, status=%s, error=%s, data=%s, headers=%s",
                method,
                url,
                status,
                error,
                data,
                headers,
            )
        return super().increment(
            method=method,
            url=url,
            response=response,
            error=error,
            _pool=_pool,
            _stacktrace=_stacktrace,
        )

    def is_retry(self, method: str, status_code: int, has_retry_after: bool = False) -> bool:
        """Indicate whether the request should be retried.

        Args:
            method: Request method.
            status_code: Status code.
            has_retry_after: Whether retry has been done before.

        Returns:
            ``True`` if the request should be retried, ``False`` otherwise.
        """
        if method.upper() == "POST" and status_code in self.status_forcelist:
            return True

        return super().is_retry(method, status_code, has_retry_after)
