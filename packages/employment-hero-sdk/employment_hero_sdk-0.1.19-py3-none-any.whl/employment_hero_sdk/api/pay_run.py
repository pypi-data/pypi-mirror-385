from typing import Any, Dict
from .base import EmploymentHeroBase
from ..models import PayRunModel

class PayRun(EmploymentHeroBase):
    """Payrun API Wrapper."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = PayRunModel(**self.data)