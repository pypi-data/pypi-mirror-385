import time
from typing import List, Optional, Union, Dict, Any
from .base import EmploymentHeroBase
from ..client import EmploymentHeroClient, EmploymentHeroAsyncClient
from ..models import AuBusinessExportModel

class Business(EmploymentHeroBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = AuBusinessExportModel(**self.data)

class BusinessManager:
    """
    Provides access to business endpoints.
    
    - When called with no argument, returns a coroutine that resolves to the list of available businesses.
    - When called with a business id, returns a coroutine that resolves to that specific business.
    
    The list of businesses is cached for a period (default TTL is 300 seconds) to avoid excess API calls.
    """
    def __init__(self, *, client: EmploymentHeroClient, cache_ttl: int = 300):
        self.client = client
        self._cache: Optional[Dict[Any, Business]] = None
        self._cache_timestamp: float = 0
        self.cache_ttl = cache_ttl
    
    @staticmethod
    def _handle_list_response(response: Dict[str, Any]) -> List[Dict[str, Any]]:
        return response if isinstance(response, list) else [response]

    def all(self, **params) -> Dict[Any, Business]:
        """Retrieve the list of available businesses, using cache if available."""
        current_time = time.time()
        if self._cache is not None and (current_time - self._cache_timestamp) < self.cache_ttl:
            return self._cache

        # The endpoint path for listing businesses is provided as "/api/v2/business"
        url = "/api/v2/business"
        response = self.client._request("GET", url, params=params)
        self._cache = {
            business.id: business
            for business in [
                Business(client=self.client, data=item, parent_path="/api/v2")
                for item in self._handle_list_response(response.json())
            ]
        }
        self._cache_timestamp = current_time
        return self._cache

    def get(self, business_id: Union[str, int]) -> Business:
        """Return the business with the given ID (from cache or fetched list)."""
        businesses = self.all()
        biz = businesses.get(business_id)
        if biz:
            return biz
        # Optionally, attempt a direct GET on /v2/business/{business_id} here.
        raise ValueError(f"Business with id '{business_id}' not found.")

    def __call__(self, business_id: Optional[Union[str, int]] = None):
        """
        When the BusinessManager is called:
          - With no argument, returns a coroutine that resolves to the list of businesses.
          - With a business id, returns a coroutine that resolves to that specific business.
          
        Usage:
            businesses = client.business()            # list all businesses (cached)
            biz = client.business("biz123")           # get a specific business
        """
        if business_id is None:
            return self.all()
        else:
            return self.get(business_id)


class AsyncBusinessManager:
    """
    Provides access to business endpoints.
    
    - When called with no argument, returns a coroutine that resolves to the list of available businesses.
    - When called with a business id, returns a coroutine that resolves to that specific business.
    
    The list of businesses is cached for a period (default TTL is 300 seconds) to avoid excess API calls.
    """
    def __init__(self, *, client: EmploymentHeroAsyncClient, cache_ttl: int = 300):
        self.client = client
        self._cache: Optional[Dict[Any, Business]] = None
        self._cache_timestamp: float = 0
        self.cache_ttl = cache_ttl

    @staticmethod
    def _handle_list_response(response: Dict[str, Any]) -> List[Dict[str, Any]]:
        return response if isinstance(response, list) else [response]

    async def all(self, **params) -> Dict[Any, Business]:
        """Retrieve the list of available businesses, using cache if available."""
        current_time = time.time()
        if self._cache is not None and (current_time - self._cache_timestamp) < self.cache_ttl:
            return self._cache

        # The endpoint path for listing businesses is provided as "/api/v2/business"
        url = "/api/v2/business"
        response = await self.client._request("GET", url, params=params)
        data = response.json()
        data_list = data if isinstance(data, list) else response.json().get("data", [])
        self._cache = {
            business.id: business
            for business in [
                Business(client=self.client, data=item, parent_path="/api/v2")
                for item in self._handle_list_response(response.json())
            ]
        }
        self._cache_timestamp = current_time
        return self._cache

    async def get(self, business_id: Union[str, int]) -> Business:
        """Return the business with the given ID (from cache or fetched list)."""
        businesses = await self.all()
        biz = businesses.get(business_id)
        if biz:
            return biz
        # Optionally, attempt a direct GET on /v2/business/{business_id} here.
        raise ValueError(f"Business with id '{business_id}' not found.")

    def __call__(self, business_id: Optional[Union[str, int]] = None):
        """
        When the BusinessManager is called:
          - With no argument, returns a coroutine that resolves to the list of businesses.
          - With a business id, returns a coroutine that resolves to that specific business.
          
        Usage:
            businesses = await client.business()            # list all businesses (cached)
            biz = await client.business("biz123")           # get a specific business
        """
        if business_id is None:
            return self.all()
        else:
            return self.get(business_id)
