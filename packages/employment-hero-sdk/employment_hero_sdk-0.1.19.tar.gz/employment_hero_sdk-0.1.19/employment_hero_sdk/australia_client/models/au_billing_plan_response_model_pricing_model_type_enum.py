from enum import Enum


class AuBillingPlanResponseModelPricingModelTypeEnum(str, Enum):
    LICENSE = "License"
    PEREMPLOYEEPERMONTH = "PerEmployeePerMonth"
    PERHOURPAID = "PerHourPaid"

    def __str__(self) -> str:
        return str(self.value)
