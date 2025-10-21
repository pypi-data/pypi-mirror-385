from typing import Any, Dict
from .base import EmploymentHeroBase
from ..models import EmploymentAgreementModel

class EmploymentAgreement(EmploymentHeroBase):
    """EmploymentAgreement API Wrapper."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = EmploymentAgreementModel(**self.data)