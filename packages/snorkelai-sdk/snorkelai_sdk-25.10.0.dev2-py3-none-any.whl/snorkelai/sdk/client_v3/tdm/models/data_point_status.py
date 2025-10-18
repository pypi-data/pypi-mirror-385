import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class DataPointStatus(StrEnum):
    ASSIGNED = "ASSIGNED"
    COMPLETED = "COMPLETED"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    UNASSIGNED = "UNASSIGNED"
