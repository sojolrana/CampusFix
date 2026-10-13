from enum import StrEnum


class UserRole(StrEnum):
    STUDENT = "student"
    STAFF = "staff"
    ADMIN = "admin"