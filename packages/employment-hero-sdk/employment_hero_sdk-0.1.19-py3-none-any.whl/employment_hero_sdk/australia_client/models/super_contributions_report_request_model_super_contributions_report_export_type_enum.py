from enum import Enum


class SuperContributionsReportRequestModelSuperContributionsReportExportTypeEnum(str, Enum):
    ACCRUALSEXCEL = "AccrualsExcel"
    PAYMENTSEXCEL = "PaymentsExcel"

    def __str__(self) -> str:
        return str(self.value)
