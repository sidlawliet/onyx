from typing import Any
from fastapi import HTTPException, status


class DomainException(HTTPException):
    def __init__(self, status_code: int, code: str, message: str, details: Any = None):
        super().__init__(
            status_code=status_code,
            detail={"code": code, "message": message, "details": details or {}},
        )


class UnauthorizedException(DomainException):
    def __init__(self, message: str = "Authentication credentials were invalid or expired."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="UNAUTHORIZED",
            message=message,
        )


class PermissionDeniedException(DomainException):
    def __init__(self, message: str = "You do not have permission to perform this action."):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="PERMISSION_DENIED",
            message=message,
        )


class NotFoundException(DomainException):
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            message=f"{resource} with identifier '{identifier}' was not found.",
        )


class WorkflowTransitionException(DomainException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code="INVALID_WORKFLOW_TRANSITION",
            message=message,
        )


class ApprovalRequiredException(DomainException):
    def __init__(self, message: str = "Execution requires an approved recommendation artifact manifest."):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="APPROVAL_REQUIRED",
            message=message,
        )


class ArtifactHashMismatchException(DomainException):
    def __init__(self, message: str = "The provided artifact hash does not match the canonical manifest hash."):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code="ARTIFACT_HASH_MISMATCH",
            message=message,
        )


class ValidationFailedException(DomainException):
    def __init__(self, message: str, details: Any = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="VALIDATION_FAILED",
            message=message,
            details=details,
        )


class DuplicateCommandException(DomainException):
    def __init__(self, idempotency_key: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code="DUPLICATE_COMMAND",
            message=f"A command with idempotency key '{idempotency_key}' has already been processed.",
        )
