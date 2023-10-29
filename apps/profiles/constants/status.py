from enum import Enum


class VerificationStatus(Enum):
    VERIFIED = "Verified"
    UNVERIFIED = "Unverified"
    VERIFICATION_PENDING = "Verification Pending"


class RequestStatus(Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class RequestAnswer(Enum):
    APPROVE = "Approve"
    REJECT = "Reject"
