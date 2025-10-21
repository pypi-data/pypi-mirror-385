from typing import Any, Dict
from .base import EmploymentHeroBase
from ..models import AuSingleLocationModel

class Location(EmploymentHeroBase):
    """Location API Wrapper."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = AuSingleLocationModel(**self.data)