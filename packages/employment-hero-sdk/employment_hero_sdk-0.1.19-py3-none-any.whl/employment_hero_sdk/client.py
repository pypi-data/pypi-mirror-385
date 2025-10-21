# pyright: reportIncompatibleMethodOverride = none

import asyncio
import logging
import time
import httpx

from redis import Redis
from httpx import BasicAuth
from typing import Optional
from importlib import import_module

from leakybucket import LeakyBucket, AsyncLeakyBucket
from leakybucket.persistence import InMemoryLeakyBucketStorage, RedisLeakyBucketStorage

from .exceptions import EmploymentHeroAPIError
from .utils import snake_to_pascal_case, pascal_to_snake_case

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = 'https://api.yourpayroll.com.au/'

class EmploymentHeroClient:
    """
    Client for interacting with the Employment Hero API.
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        redis_url: Optional[str] = None,
        throttler_leak_rate: float = 3.5,
        throttler_period: float = 1.0,
    ):
        if not api_key:
            raise ValueError("API key is required")

        self.api_key = api_key
        self.base_url = base_url

        # Create persistent httpx clients (sync and async)
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=60,
            auth=BasicAuth(self.api_key, '')
        )
        
        if redis_url:
            self.storage = RedisLeakyBucketStorage(
                Redis(redis_url),
                redis_key="eh-api-throttler",
                max_rate=throttler_leak_rate,
                time_period=throttler_period
            )
        else:
            self.storage = InMemoryLeakyBucketStorage(
                max_rate=throttler_leak_rate, 
                time_period=throttler_period
            )
        
        self.throttler = LeakyBucket(self.storage)

        self._business_manager = None
        
    @property
    def headers(self) -> dict:
        return {"Content-Type": "application/json", "Accept": "application/json"}

    def _prepare_request(self, **kwargs) -> dict:
        """Merge default headers and allow caller overrides."""
        headers = kwargs.pop('headers', {})
        kwargs['headers'] = {**self.headers, **headers}
        return kwargs
    
    def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """
        Make a synchronous HTTP request.
        """
        retries = 5
        kwargs = self._prepare_request(**kwargs)
        while True:
            with self.throttler:
                response = self._client.request(method, url, **kwargs)
                
            if 200 <= response.status_code < 300:
                return response

            # Handle rate limiting if a Retry-After header is sent
            retry_after = str(response.headers.get('Retry-After'))
            if retry_after and retry_after.isdigit():
                wait_time = int(retry_after)
                logger.info(f"Rate limited, sleeping for {wait_time} seconds")
                time.sleep(wait_time)
                continue

            # Retry on server errors (HTTP 5xx)
            if response.status_code >= 500 and retries > 0:
                retries -= 1
                logger.warning(f"Server error ({response.status_code}), retrying {retries} more time(s)...")
                time.sleep(3)
                continue

            raise EmploymentHeroAPIError(
                status_code=response.status_code,
                response=response,
                method=method,
                url=url,
                kwargs=kwargs
            )

    def __getattr__(self, item: str):
        """
        Dynamically load an API wrapper from the `api` subpackage.
        For example, accessing `client.employee` will load the Employee API wrapper.
        For multi-word API classes, use snake_case (e.g. `client.pay_run` -> PayRun).
        """
        try:
            base_package = self.__class__.__module__.split(".")[0]
            module = import_module(f"{base_package}.api.{item.lower()}")
            # Expect the API class to have the same name but capitalized.
            api_class = getattr(module, snake_to_pascal_case(item))
            return api_class(client=self)
        except (ModuleNotFoundError, AttributeError):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

    @property
    def business(self):
        """
        Access the BusinessManager, which is callable.
        • Calling client.business() (with no arguments) lets you call list() to fetch all businesses.
        • Calling client.business(business_id) enters a specific business context.
        """
        if not self._business_manager:
            from .api.business import BusinessManager
            self._business_manager = BusinessManager(client=self)
        return self._business_manager


class EmploymentHeroAsyncClient(EmploymentHeroClient):
    """
    Async client for interacting with the Employment Hero API.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=60,
            auth=BasicAuth(self.api_key, '')
        )
        
        self.throttler = AsyncLeakyBucket(self.storage)
        
    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """
        Make an asynchronous HTTP request with basic retry logic and throttling.
        """
        retries = 5
        kwargs = self._prepare_request(**kwargs)
        while True:
            async with self.throttler:
                async with self._client as client:
                    response = await client.request(method, url, **kwargs)
                
            if 200 <= response.status_code < 300:
                return response

            # Handle rate limiting if a Retry-After header is sent
            retry_after = str(response.headers.get('Retry-After'))
            if retry_after and retry_after.isdigit():
                wait_time = int(retry_after)
                logger.info(f"Rate limited, sleeping for {wait_time} seconds")
                await asyncio.sleep(wait_time)
                continue

            # Retry on server errors (HTTP 5xx)
            if response.status_code >= 500 and retries > 0:
                retries -= 1
                logger.warning(f"Server error ({response.status_code}), retrying {retries} more time(s)...")
                await asyncio.sleep(3)
                continue

            raise EmploymentHeroAPIError(
                status_code=response.status_code,
                response=response,
                method=method,
                url=url,
                kwargs=kwargs
            )
            
    @property
    def business(self):
        """
        Access the BusinessManager, which is callable.
        • Calling client.business() (with no arguments) lets you call list() to fetch all businesses.
        • Calling client.business(business_id) enters a specific business context.
        """
        if not self._business_manager:
            from .api.business import AsyncBusinessManager
            self._business_manager = AsyncBusinessManager(client=self)
        return self._business_manager