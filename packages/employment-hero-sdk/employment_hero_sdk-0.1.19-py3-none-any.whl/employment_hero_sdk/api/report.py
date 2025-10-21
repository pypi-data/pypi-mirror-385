import pandas as pd
from typing import Any, Dict
from .base import EmploymentHeroBase

class Report(EmploymentHeroBase):
    """Report API Wrapper."""

    def birthday(self, **kwargs):
        return pd.DataFrame(
            self._parse_response_data(
                self.client._request("GET", self._build_url(suffix="birthday"), params=kwargs).json()
            )
        )