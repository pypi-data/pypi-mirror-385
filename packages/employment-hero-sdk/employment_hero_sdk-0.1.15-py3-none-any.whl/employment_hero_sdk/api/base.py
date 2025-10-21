import pandas as pd
from typing import (
    Any, 
    Dict, 
    List, 
    Optional, 
    Type, 
    TypeVar,
    Union,
    Coroutine,
    Generator,
    AsyncGenerator
)
from ..utils import serialize, deserialize, snake_to_pascal_case
from ..client import EmploymentHeroClient, EmploymentHeroAsyncClient

T = TypeVar("T", bound="EmploymentHeroBase")

class EmploymentHeroBase:
    """
    Base class for endpoints that require a business parent context.
    
    Child API classes (for example, Employee) should set their own `endpoint`
    attribute (or rely on the default, which is the class name in lowercase).

    This class implements standard CRUD methods as well as pagination.
    It also provides generator methods so that data can be fetched one item at a time.

    The __call__ method behaves as follows:
      - If a resource_id is provided, it returns a single instance (via fetch);
      - Otherwise, it returns a generator that yields resources one by one.
        For sync clients, a Generator[T, None, None] is returned.
        For async clients, a coroutine yielding an AsyncGenerator[T, None] is returned.
    """
    endpoint: str = ""

    def __init__(
        self,
        *,
        client: Union[EmploymentHeroClient, EmploymentHeroAsyncClient],
        data: Optional[Dict[str, Any]] = None,
        parent: Optional["EmploymentHeroBase"] = None,
        parent_path: Optional[str] = None  # e.g. "/api/v2/business/{business_id}",
    ) -> None:
        self.client = client
        self.data: Dict[str, Any] = data or {}
        self.model = None
        self.parent: Optional["EmploymentHeroBase"] = parent
        self.parent_path: Optional[str] = parent_path

    def __getattr__(self, item: str) -> Any:
        # if the attribute exists in the model's data, return it.
        if item in self.data:
            return self.data[item]

        if not getattr(self, 'id', None):
            raise AttributeError(f"No such attribute '{item}' in {self.__class__.__name__} context.")
            
        from importlib import import_module
        base_package = self.client.__class__.__module__.split(".")[0]

        # try to load an API module for this attribute.
        try:
            module = import_module(f"{base_package}.api.{item.lower()}")
            # we define modules in pascal case, but refer to them as attributes in snake case.
            api_class = getattr(module, snake_to_pascal_case(item))
            return api_class(client=self.client, parent=self, parent_path=self._build_url(self.id))
        except (ModuleNotFoundError, AttributeError):
            # split snake case item into a path e.g. report_birthday -> report/birthday
            item = "/".join(item.split("_"))
            
            # If no module exists for this attribute and model has an id, then assume the attribute
            # is a valid endpoint suffix. Return a callable that makes a GET request.
            # If it isn't valid, it'll just return a 404.
            def dynamic_endpoint(*args, dataframe: bool = False, **kwargs):
                """:param dataframe: If True, return a DataFrame instead of a list of dictionaries."""
                url = self._build_url(resource_id=self.id, suffix=item)
                if isinstance(self.client, EmploymentHeroClient):
                    response = self.client._request("GET", url, params=kwargs)
                    data = self._parse_response_data(response.json())
                    if dataframe:
                        return pd.DataFrame(data)
                    return data
                else:
                    async def async_endpoint():
                        response = await self.client._request("GET", url, params=kwargs)
                        data = self._parse_response_data(response.json())
                        return data
                    return async_endpoint()
            return dynamic_endpoint

    def __repr__(self) -> str:
        identifier = self.data.get("id", "unknown")
        return f"<{self.__class__.__name__} id={identifier}>"

    def __call__(self: T, resource_id: Optional[Any] = None, **kwargs: Any) -> Union[
        T,
        Generator[T, None, None],
        Coroutine[Any, Any, AsyncGenerator[T, None]]
    ]:
        """
        If a resource_id is provided, fetch and return a single instance;
        otherwise, return a generator that yields resources one by one.

        For sync clients, returns a Generator[T, None, None].
        For async clients, returns a coroutine that yields an AsyncGenerator[T, None].
        """
        if resource_id is not None:
            if isinstance(self.client, EmploymentHeroClient):
                return self.fetch(resource_id)
            else:
                return self.fetch_async(resource_id)
        else:
            if isinstance(self.client, EmploymentHeroClient):
                return self.paginate_generator(**kwargs)
            else:
                return self.paginate_async_generator(**kwargs)
        
    @classmethod
    def get_endpoint(cls) -> str:
        return cls.endpoint if cls.endpoint else cls.__name__.lower()

    @staticmethod
    def _parse_response_data(
        response: Union[List[Any], Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        responses = response if isinstance(response, list) else [response]
        return responses
        # return [deserialize(item) for item in responses]
    
    @property
    def base_path(self) -> str:
        if self.parent_path:
            return f"{self.parent_path}/{self.get_endpoint()}"
        return f"/{self.get_endpoint()}"

    def _build_url(self, resource_id: Optional[Any] = None, suffix: str = "") -> str:
        if not self.parent_path:
            raise ValueError("Parent path is not defined for a chained endpoint.")
        url = f"{self.parent_path}/{self.get_endpoint()}"
        if resource_id is not None:
            url = f"{url}/{resource_id}"
        if suffix:
            url = f"{url}/{suffix}"
        return url
    
    def show(self, indent: int = 0, indent_step: int = 2) -> str:
        """
        Return a nicely formatted string representation of this model and its data.

        This method recursively prints nested EmploymentHeroBase instances
        and lists of such instances with indentation.

        Args:
            indent (int): The current indent level in spaces (default is 0).
            indent_step (int): The number of spaces to add for each nested level (default is 2).

        Returns:
            A formatted string showing the model's class name and its key/value data.
        """
        pad = " " * indent
        lines = [f"{pad}{self.__class__.__name__}:"]
        for key, value in self.data.items():
            if isinstance(value, EmploymentHeroBase):
                lines.append(f"{pad}{' ' * indent_step}{key}:")
                lines.append(value.show(indent + indent_step, indent_step))
            elif isinstance(value, list):
                lines.append(f"{pad}{' ' * indent_step}{key}: [")
                for item in value:
                    if isinstance(item, EmploymentHeroBase):
                        lines.append(item.show(indent + indent_step, indent_step))
                    else:
                        lines.append(f"{pad}{' ' * (indent_step * 2)}{item}")
                lines.append(f"{pad}{' ' * indent_step}]")
            else:
                lines.append(f"{pad}{' ' * indent_step}{key}: {value}")
        return "\n".join(lines)

    def fetch(self: T, resource_id: Any) -> T:
        """Fetch a single resource synchronously by ID."""
        if not isinstance(self.client, EmploymentHeroClient):
            raise ValueError("This method requires a sync client.")
        url = self._build_url(resource_id)
        response = self.client._request("GET", url)
        data = self._parse_response_data(response.json())
        # If the returned data is a list, take the first item.
        if isinstance(data, list):
            data = data[0] if data else {}
        return self.__class__(client=self.client, data=data, parent_path=self.parent_path)  # type: ignore

    async def fetch_async(self: T, resource_id: Any) -> T:
        """Fetch a single resource asynchronously by ID."""
        if not isinstance(self.client, EmploymentHeroAsyncClient):
            raise ValueError("This method requires an async client.")
        url = self._build_url(resource_id)
        response = await self.client._request("GET", url)
        data = self._parse_response_data(response.json())
        if isinstance(data, list):
            data = data[0] if data else {}
        return self.__class__(client=self.client, data=data, parent_path=self.parent_path)  # type: ignore

    def list(self: T, **params: Any) -> List[T]:
        """List (or paginate synchronously) through resources using provided filters."""
        if not isinstance(self.client, EmploymentHeroClient):
            raise ValueError("This method requires a sync client.")
        url = self._build_url()
        response = self.client._request("GET", url, params=params)
        data_list = self._parse_response_data(response.json())
        return [self.__class__(client=self.client, data=item, parent_path=self.parent_path) for item in data_list]  # type: ignore

    async def list_async(self: T, **params: Any) -> List[T]:
        """List (or paginate asynchronously) through resources using provided filters."""
        if not isinstance(self.client, EmploymentHeroAsyncClient):
            raise ValueError("This method requires an async client.")
        url = self._build_url()
        response = await self.client._request("GET", url, params=params)
        data_list = self._parse_response_data(response.json())
        return [self.__class__(client=self.client, data=item, parent_path=self.parent_path) for item in data_list]  # type: ignore

    def create(self: T, payload: Dict[str, Any]) -> T:
        """Create a new resource synchronously."""
        if not isinstance(self.client, EmploymentHeroClient):
            raise ValueError("This method requires a sync client.")
        url = self._build_url()
        response = self.client._request("POST", url, json=serialize(payload))
        data = self._parse_response_data(response.json())
        data = data[0] if data else {}
        return self.__class__(client=self.client, data=data, parent_path=self.parent_path)  # type: ignore

    async def create_async(self: T, payload: Dict[str, Any]) -> T:
        """Create a new resource asynchronously."""
        if not isinstance(self.client, EmploymentHeroAsyncClient):
            raise ValueError("This method requires an async client.")
        url = self._build_url()
        response = await self.client._request("POST", url, json=serialize(payload))
        data = self._parse_response_data(response.json())
        data = data[0] if data else {}
        return self.__class__(client=self.client, data=data, parent_path=self.parent_path)  # type: ignore

    def update(self: T, resource_id: Any, payload: Dict[str, Any]) -> T:
        """Update an existing resource synchronously."""
        if not isinstance(self.client, EmploymentHeroClient):
            raise ValueError("This method requires a sync client.")
        url = self._build_url(resource_id)
        response = self.client._request("PUT", url, json=serialize(payload))
        data = self._parse_response_data(response.json())
        data = data[0] if data else {}
        return self.__class__(client=self.client, data=data, parent_path=self.parent_path)  # type: ignore

    async def update_async(self: T, resource_id: Any, payload: Dict[str, Any]) -> T:
        """Update an existing resource asynchronously."""
        if not isinstance(self.client, EmploymentHeroAsyncClient):
            raise ValueError("This method requires an async client.")
        url = self._build_url(resource_id)
        response = await self.client._request("PUT", url, json=serialize(payload))
        data = self._parse_response_data(response.json())
        data = data[0] if data else {}
        return self.__class__(client=self.client, data=data, parent_path=self.parent_path)  # type: ignore

    def delete(self, resource_id: Any) -> None:
        """Delete a resource synchronously."""
        if not isinstance(self.client, EmploymentHeroClient):
            raise ValueError("This method requires a sync client.")
        url = self._build_url(resource_id)
        self.client._request("DELETE", url)

    async def delete_async(self, resource_id: Any) -> None:
        """Delete a resource asynchronously."""
        if not isinstance(self.client, EmploymentHeroAsyncClient):
            raise ValueError("This method requires an async client.")
        url = self._build_url(resource_id)
        await self.client._request("DELETE", url)

    def paginate(self: T, **params: Any) -> List[T]:
        """Synchronously paginate through all pages of data."""
        if not isinstance(self.client, EmploymentHeroClient):
            raise ValueError("This method requires a sync client.")
        top = params.get("$top", 100)
        skip = params.get("$skip", 0)
        all_items: List[Dict[str, Any]] = []
        while True:
            params["$top"] = top
            params["$skip"] = skip
            url = self._build_url()
            response = self.client._request("GET", url, params=params)
            page_data = self._parse_response_data(response.json())
            if not page_data:
                break
            all_items.extend(page_data)
            skip += top
        return [self.__class__(client=self.client, data=item, parent_path=self.parent_path) for item in all_items]  # type: ignore

    async def paginate_async(self: T, **params: Any) -> List[T]:
        """Asynchronously paginate through all pages of data."""
        if not isinstance(self.client, EmploymentHeroAsyncClient):
            raise ValueError("This method requires an async client.")
        top = params.get("$top", 100)
        skip = params.get("$skip", 0)
        all_items: List[Dict[str, Any]] = []
        while True:
            params["$top"] = top
            params["$skip"] = skip
            url = self._build_url()
            response = await self.client._request("GET", url, params=params)
            page_data = self._parse_response_data(response.json())
            if not page_data:
                break
            all_items.extend(page_data)
            skip += top
        return [self.__class__(client=self.client, data=item, parent_path=self.parent_path) for item in all_items]  # type: ignore
    
    def paginate_generator(self, **params: Any) -> Generator["EmploymentHeroBase", None, None]:
        """
        Synchronously paginate through all pages of data, yielding one resource at a time.
        Assumes the API supports $top and $skip parameters.
        """
        if not isinstance(self.client, EmploymentHeroClient):
            raise ValueError("This method requires a sync client.")
        top = params.get("$top", 100)
        skip = params.get("$skip", 0)
        while True:
            params["$top"] = top
            params["$skip"] = skip
            url = self._build_url()
            response = self.client._request("GET", url, params=params)
            page_data = self._parse_response_data(response.json())
            if not page_data:
                break
            for item in page_data:
                yield self.__class__(client=self.client, data=item, parent_path=self.parent_path)
            skip += top

    async def paginate_async_generator(self, **params: Any) -> AsyncGenerator["EmploymentHeroBase", None]:
        """
        Asynchronously paginate through all pages of data, yielding one resource at a time.
        Assumes the API supports $top and $skip parameters.
        """
        if not isinstance(self.client, EmploymentHeroAsyncClient):
            raise ValueError("This method requires an async client.")
        top = params.get("$top", 100)
        skip = params.get("$skip", 0)
        while True:
            params["$top"] = top
            params["$skip"] = skip
            url = self._build_url()
            response = await self.client._request("GET", url, params=params)
            page_data = self._parse_response_data(response.json())
            if not page_data:
                break
            for item in page_data:
                yield self.__class__(client=self.client, data=item, parent_path=self.parent_path)
            skip += top