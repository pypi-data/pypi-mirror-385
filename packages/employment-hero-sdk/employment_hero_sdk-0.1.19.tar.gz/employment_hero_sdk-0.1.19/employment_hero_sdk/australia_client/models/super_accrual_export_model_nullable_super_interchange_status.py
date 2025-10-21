from enum import Enum


class SuperAccrualExportModelNullableSuperInterchangeStatus(str, Enum):
    AWAITINGCLEARANCE = "AwaitingClearance"
    AWAITINGPAYMENT = "AwaitingPayment"
    CANCELLED = "Cancelled"
    CANCELLING = "Cancelling"
    NEW = "New"
    PAID = "Paid"
    PAYMENTFAILED = "PaymentFailed"
    RECONCILED = "Reconciled"
    REFUNDED = "Refunded"
    SENTTOFUND = "SentToFund"
    SENTTOFUNDWITHREFUND = "SentToFundWithRefund"
    SENTTOFUNDWITHRESPONSE = "SentToFundWithResponse"
    SUBMISSIONFAILED = "SubmissionFailed"
    SUBMISSIONPAID = "SubmissionPaid"
    SUBMISSIONPROCESSED = "SubmissionProcessed"
    SUBMISSIONQUEUEDFORPAYMENT = "SubmissionQueuedForPayment"
    SUBMITTED = "Submitted"
    SUBMITTEDFORPROCESSING = "SubmittedForProcessing"

    def __str__(self) -> str:
        return str(self.value)
