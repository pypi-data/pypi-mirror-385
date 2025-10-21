from enum import Enum


class JournalExportResultJournalExportStatus(str, Enum):
    FAILUREACCOUNTPERIODCLOSED = "FailureAccountPeriodClosed"
    FAILUREACCOUNTSNOTCONFIGURED = "FailureAccountsNotConfigured"
    FAILUREALREADYEXPORTED = "FailureAlreadyExported"
    FAILUREAPIERROR = "FailureAPIError"
    FAILURECANNOTUSEACCOUNTSPAYABLEACCOUNT = "FailureCannotUseAccountsPayableAccount"
    FAILUREFUNCTIONDISABLED = "FailureFunctionDisabled"
    FAILUREGSTSETUP = "FailureGSTSetup"
    FAILUREINTERCOMPANYLOANACCOUNTSNOTCONFIGURED = "FailureIntercompanyLoanAccountsNotConfigured"
    FAILUREITEMSDELETED = "FailureItemsDeleted"
    FAILUREKNOWNERROR = "FailureKnownError"
    FAILUREMISSINGTAXINFO = "FailureMissingTaxInfo"
    FAILURENOJOURNALID = "FailureNoJournalId"
    FAILURENOPROVIDERFOUND = "FailureNoProviderFound"
    FAILURENOTAUTHENTICATED = "FailureNotAuthenticated"
    FAILURERECORDINGJOURNALREFERENCE = "FailureRecordingJournalReference"
    FAILURESTENANTNOTSUPPLIED = "FailuresTenantNotSupplied"
    FAILUREUNKNOWNERROR = "FailureUnknownError"
    FAILUREUSINGMANUALLYENTEREDDIMENSION = "FailureUsingManuallyEnteredDimension"
    FAILUREVENDORMESSAGE = "FailureVendorMessage"
    NOTEXPORTED = "NotExported"
    RESULTUNKNOWN = "ResultUnknown"
    SUCCESS = "Success"

    def __str__(self) -> str:
        return str(self.value)
