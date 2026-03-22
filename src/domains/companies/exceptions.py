import uuid

from src.core.exceptions import BadRequestException, ConflictException, ForbiddenException, NotFoundException


class CompanyNotFoundException(NotFoundException):
    """Raised when a company is not found."""

    def __init__(self, company_id: uuid.UUID | None = None):
        if company_id:
            message = f"Company not found: {company_id}"
            details = {"company_id": str(company_id)}
        else:
            message = "Company not found"
            details = {}
        super().__init__(
            message=message,
            error_code="COMPANY_NOT_FOUND",
            details=details,
        )


class CompanyMersisConflictException(ConflictException):
    """Raised when a company with the same MERSIS number already exists."""

    def __init__(self, mersis_number: str):
        super().__init__(
            message=f"Company with MERSIS number {mersis_number} already exists",
            error_code="COMPANY_MERSIS_CONFLICT",
            details={"mersis_number": mersis_number},
        )


class CompanySectorConflictException(ConflictException):
    """Raised when a sector with the same NACE code already exists for the company."""

    def __init__(self, nace_code: str):
        super().__init__(
            message=f"Sector with NACE code '{nace_code}' already exists for this company.",
            error_code="COMPANY_SECTOR_CONFLICT",
            details={"nace_code": nace_code},
        )


class CompanySectorNotFoundException(NotFoundException):
    """Raised when a sector is not found or does not belong to the company."""

    def __init__(self, sector_id: uuid.UUID):
        super().__init__(
            message=f"Sector not found or does not belong to this company: {sector_id}",
            error_code="COMPANY_SECTOR_NOT_FOUND",
            details={"sector_id": str(sector_id)},
        )


class InvitationAlreadyExistsException(ConflictException):
    """Raised when a pending invitation already exists for this email+company."""

    def __init__(self, email: str):
        super().__init__(
            message=f"A pending invitation already exists for {email}",
            error_code="INVITATION_ALREADY_EXISTS",
            details={"email": email},
        )


class UserAlreadyMemberException(ConflictException):
    """Raised when the invited user is already a member of the company."""

    def __init__(self, email: str):
        super().__init__(
            message=f"{email} is already a member of this company",
            error_code="USER_ALREADY_MEMBER",
            details={"email": email},
        )


class InvalidInvitationException(BadRequestException):
    """Raised when an invitation token is invalid, expired, or already used."""

    def __init__(self, detail: str = "Invalid or expired invitation"):
        super().__init__(
            message=detail,
            error_code="INVALID_INVITATION",
            details={},
        )


class ConsultantRequiresAdminException(ForbiddenException):
    """Raised when trying to assign consultant role to a non-admin user."""

    def __init__(self):
        super().__init__(
            message="Consultant role can only be assigned to users with Admin system role",
            error_code="CONSULTANT_REQUIRES_ADMIN",
            details={},
        )


class InvalidInvitationRoleException(BadRequestException):
    """Raised when an invalid role is specified for invitation."""

    def __init__(self, role: str):
        super().__init__(
            message=f"Cannot invite users with role '{role}'",
            error_code="INVALID_INVITATION_ROLE",
            details={"role": role},
        )
