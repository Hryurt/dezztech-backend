from src.core.exceptions import BadRequestException, ForbiddenException


class CompanyLimitReachedException(ForbiddenException):
    """Raised when user has reached the maximum number of companies."""

    def __init__(self, max_companies: int):
        super().__init__(
            message=f"Company limit reached. Your plan allows {max_companies} companies.",
            error_code="COMPANY_LIMIT_REACHED",
            details={"max_companies": max_companies},
        )


class MemberLimitReachedException(ForbiddenException):
    """Raised when a company has reached the maximum number of members."""

    def __init__(self, max_members: int):
        super().__init__(
            message=f"Member limit reached. Your plan allows {max_members} members per company.",
            error_code="MEMBER_LIMIT_REACHED",
            details={"max_members": max_members},
        )


class FreemiumCannotCreateCompanyException(ForbiddenException):
    """Raised when a freemium user tries to create a company."""

    def __init__(self):
        super().__init__(
            message="Freemium plan cannot create companies. Please upgrade.",
            error_code="FREEMIUM_CANNOT_CREATE_COMPANY",
            details={},
        )


class SubscriptionNotFoundException(BadRequestException):
    """Raised when user has no subscription record."""

    def __init__(self):
        super().__init__(
            message="No active subscription found",
            error_code="SUBSCRIPTION_NOT_FOUND",
            details={},
        )
