from typing import Any, Dict
from .base import EmploymentHeroBase
from ..models import TimesheetLineModel

class Timesheet(EmploymentHeroBase):
    """Timesheet API Wrapper."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = TimesheetLineModel(**self.data)