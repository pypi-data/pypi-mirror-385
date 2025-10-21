from enum import Enum


class AuStpRegistrationModelAtoSupplierRole(str, Enum):
    EMPLOYER = "Employer"
    INTERMEDIARY = "Intermediary"
    REGISTEREDTAXAGENT = "RegisteredTaxAgent"

    def __str__(self) -> str:
        return str(self.value)
