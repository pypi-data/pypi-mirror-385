from typing import Any, Dict
from .base import EmploymentHeroBase
from ..models import AuUnstructuredEmployeeModel

class Employee(EmploymentHeroBase):
    """
    Employee API Wrapper.
    With a business parent, its URL becomes:
      {parent_path}/employee
    For example: /v2/business/{business_id}/employee
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = AuUnstructuredEmployeeModel(**self.data)

    @property
    def full_name(self) -> str:
        return f"{self.model.firstName} {self.model.surname}".strip()

    async def grant_access(self, email: str, name: str) -> Dict[str, Any]:
        """Example method to grant access to an employee."""
        url = self._build_url(resource_id=self.data.get("id"), suffix="access")
        payload = {
            "email": email,
            "name": name,
            "suppressNotificationEmails": False
        }
        response = await self.client._request("POST", url, json=payload)
        return response.json()