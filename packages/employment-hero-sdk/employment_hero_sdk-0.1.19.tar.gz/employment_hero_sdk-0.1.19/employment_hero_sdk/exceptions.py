import httpx
from typing import Optional

class EmploymentHeroAPIError(Exception):
    """
    Exception raised for API errors.
    """
    def __init__(self, *, 
                 status_code: Optional[int]=None, 
                 response: Optional[httpx.Response]=None, 
                 method: Optional[str]=None, 
                 url: Optional[str]=None, 
                 kwargs: Optional[dict]=None
                 ):
        self.status_code = status_code
        self.response = response
        self.method = method
        self.url = url
        self.kwargs = kwargs
        message = (
            f"API Error {status_code} on {method} {url}"
            f"\nRequest kwargs: {kwargs}"
            f"\nResponse: {response}"
        )
        
        if response:
            try:
                message += (
                    f"\nResponse JSON: {response.json()}"
                    f"\nRequest URL: {response.request.url}"
                )
            except Exception:
                message += (
                    f"\nResponse content: {response.content}"
                    f"\nRequest URL: {response.request.url}"
                )
        super().__init__(message)