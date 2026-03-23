import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.companies.constants import (
    COMPANY_CONSULTANT_ROLE,
    COMPANY_OWNER_ROLE,
    INVITABLE_ROLES,
)
from src.domains.companies.exceptions import (
    CompanyMersisConflictException,
    CompanyNotFoundException,
    CompanySectorConflictException,
    CompanySectorNotFoundException,
    ConsultantRequiresAdminException,
    InvalidInvitationException,
    InvalidInvitationRoleException,
    InvitationAlreadyExistsException,
    UserAlreadyMemberException,
)
from src.domains.companies.models import (
    Company,
    CompanyInvitation,
    CompanySector,
)
from src.domains.companies.repository import CompanyRepository
from src.domains.companies.schemas import (
    CompanyCreateRequest,
    CompanyMemberListItem,
    CompanySectorCreateRequest,
    CompanyUpdateRequest,
    InvitationResponse,
    MyCompanyListItem,
)
from src.domains.companies.utils import normalize_iban, normalize_pagination, normalize_search
from src.domains.users.models import User, UserRole
from src.domains.users.repository import UserRepository
from src.core.logger import get_logger

logger = get_logger(__name__)


class CompanyService:
    """Service for company operations."""

    def __init__(self, db: AsyncSession):
        """Initialize CompanyService with database session.

        Args:
            db: Database session
        """
        self.db = db
        self.repo = CompanyRepository(db)

    async def _ensure_user_membership(
        self,
        *,
        user_id: uuid.UUID,
        company_id: uuid.UUID,
    ) -> None:
        """Ensure the user is a member of the company."""
        exists = await self.repo.membership_exists(
            user_id=user_id,
            company_id=company_id,
        )
        if not exists:
            raise CompanyNotFoundException(company_id=company_id)

    async def create_company(
        self,
        *,
        user_id: uuid.UUID,
        data: CompanyCreateRequest,
    ) -> Company:
        """Create a new company and assign the creating user as owner.

        Args:
            user_id: ID of the user creating the company (becomes owner)
            data: Company creation data

        Returns:
            Created company

        Raises:
            CompanyMersisConflictException: If MERSIS number already exists
        """
        # Enforce subscription limits
        from src.domains.subscriptions.service import SubscriptionService

        sub_service = SubscriptionService(self.db)
        await sub_service.enforce_company_creation_limit(user_id)

        if await self.repo.exists_by_mersis(data.mersis_number):
            raise CompanyMersisConflictException(mersis_number=data.mersis_number)

        iban_try = normalize_iban(data.iban_try) if data.iban_try else None

        company = await self.repo.create(
            name=data.name,
            mersis_number=data.mersis_number,
            tax_number=data.tax_number,
            tax_office=data.tax_office,
            employee_count=data.employee_count,
        )

        company.foundation_date = data.foundation_date
        company.headquarters_address = data.headquarters_address
        company.iban_try = iban_try
        company.nace_code = data.nace_code
        company.activity_sector = data.activity_sector
        company.exporter_union = data.exporter_union
        company.hib_member_no = data.hib_member_no
        company.contact_full_name = data.contact_full_name
        company.contact_phone = data.contact_phone
        company.email = data.email
        company.phone = data.phone
        company.website = data.website
        company.kep_address = data.kep_address

        owner_role = await self.repo.get_role_by_name(COMPANY_OWNER_ROLE)
        if owner_role is None:
            raise RuntimeError(
                f"Company role '{COMPANY_OWNER_ROLE}' not found. Seed roles via migration."
            )

        await self.repo.create_membership(
            user_id=user_id,
            company_id=company.id,
            role_id=owner_role.id,
        )

        await self.db.commit()
        await self.db.refresh(company)

        logger.info(
            "Company created",
            extra={"company_id": str(company.id), "company_name": company.name},
        )
        return company

    async def get_company_by_id(
        self, company_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> Company:
        """Get a company by ID.

        Args:
            company_id: Company ID
            user_id: Optional user ID for membership verification

        Returns:
            Company

        Raises:
            CompanyNotFoundException: If company not found
        """
        if user_id is not None:
            await self._ensure_user_membership(
                user_id=user_id,
                company_id=company_id,
            )
        company = await self.repo.get_by_id(company_id)

        if not company:
            raise CompanyNotFoundException(company_id=company_id)

        return company

    async def update_company(
        self,
        company_id: uuid.UUID,
        data: CompanyUpdateRequest,
        user_id: uuid.UUID | None = None,
    ) -> Company:
        """Update company fields. Only active companies can be updated.

        Args:
            company_id: Company ID
            data: Update data (partial)
            user_id: Optional user ID for membership verification

        Returns:
            Updated company

        Raises:
            CompanyNotFoundException: If company not found or not active
        """
        if user_id is not None:
            await self._ensure_user_membership(
                user_id=user_id,
                company_id=company_id,
            )
        company = await self.repo.get_active_by_id(company_id)
        if not company:
            raise CompanyNotFoundException(company_id=company_id)

        update_data = data.model_dump(exclude_unset=True)
        iban = update_data.get("iban_try")
        if iban:
            update_data["iban_try"] = normalize_iban(iban)
        company.update_from_dict(update_data)

        await self.db.commit()
        await self.db.refresh(company)

        logger.info(
            "Company updated",
            extra={
                "company_id": str(company.id),
                "company_name": company.name,
            },
        )
        return company

    async def deactivate_company(
        self, company_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> Company:
        """Deactivate a company. Only active companies can be deactivated.

        Args:
            company_id: Company ID
            user_id: Optional user ID for membership verification

        Returns:
            Deactivated company

        Raises:
            CompanyNotFoundException: If company not found or not active
        """
        if user_id is not None:
            await self._ensure_user_membership(
                user_id=user_id,
                company_id=company_id,
            )
        company = await self.repo.get_active_by_id(company_id)

        if not company:
            raise CompanyNotFoundException(company_id=company_id)

        company.deactivate()

        await self.db.commit()
        await self.db.refresh(company)

        logger.info(
            "Company deactivated",
            extra={"company_id": str(company.id), "company_name": company.name},
        )
        return company

    async def activate_company(
        self, company_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> Company:
        """Activate a company. Only inactive companies can be activated.

        Args:
            company_id: Company ID
            user_id: Optional user ID for membership verification

        Returns:
            Activated company

        Raises:
            CompanyNotFoundException: If company not found
        """
        if user_id is not None:
            await self._ensure_user_membership(
                user_id=user_id,
                company_id=company_id,
            )
        company = await self.repo.get_by_id(company_id)

        if not company or company.is_active:
            raise CompanyNotFoundException(company_id=company_id)

        company.activate()

        await self.db.commit()
        await self.db.refresh(company)

        logger.info(
            "Company activated",
            extra={"company_id": str(company.id), "company_name": company.name},
        )
        return company

    async def delete_company(self, company_id: uuid.UUID) -> None:
        """Hard delete a company. Only callable by owner.

        Args:
            company_id: Company ID

        Raises:
            CompanyNotFoundException: If company not found
        """
        company = await self.repo.get_by_id(company_id)
        if not company:
            raise CompanyNotFoundException(company_id=company_id)

        company_name = company.name
        await self.repo.delete(company)
        await self.db.commit()

        logger.info(
            "Company deleted",
            extra={"company_id": str(company_id), "company_name": company_name},
        )

    async def list_my_companies(
        self,
        user: User,
        page: int,
        limit: int,
        search: str | None,
    ) -> tuple[list[MyCompanyListItem], int]:
        """List companies where the user is an active member.
Companies may be active or inactive.

        Args:
            user: Authenticated user
            page: Page number (1-based)
            limit: Page size
            search: Optional search term for company name

        Returns:
            Tuple of (items, total_count)
        """
        page, limit = normalize_pagination(page, limit)
        search = normalize_search(search)

        rows, total = await self.repo.list_active_companies_for_user_with_role(
            user_id=user.id,
            search=search,
            page=page,
            limit=limit,
        )

        items = [
            MyCompanyListItem(
                id=company.id,
                name=company.name,
                is_active=company.is_active,
                role=role_name,
            )
            for company, role_name in rows
        ]
        return items, total

    async def list_company_members(
        self, company_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> list[CompanyMemberListItem]:
        """List members of a company including both active and inactive memberships.

        Args:
            company_id: Company ID
            user_id: Optional user ID for membership verification

        Returns:
            List of company members
        """
        if user_id is not None:
            await self._ensure_user_membership(
                user_id=user_id,
                company_id=company_id,
            )
        company = await self.repo.get_by_id(company_id)
        if not company:
            raise CompanyNotFoundException(company_id=company_id)

        rows = await self.repo.list_members_for_company(company_id)

        return [
            CompanyMemberListItem(
                user_id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=role_name,
                is_active=membership_is_active,
                joined_at=joined_at,
            )
            for user, role_name, membership_is_active, joined_at in rows
        ]

    async def create_company_sector(
        self,
        company_id: uuid.UUID,
        data: CompanySectorCreateRequest,
        user_id: uuid.UUID | None = None,
    ) -> CompanySector:
        """Create a new company sector.

        Args:
            company_id: Company ID
            data: Sector creation data
            user_id: Optional user ID for membership verification

        Returns:
            Created company sector

        Raises:
            CompanyNotFoundException: If company not found or not active
            CompanySectorConflictException: If sector with same NACE code already exists
        """
        if user_id is not None:
            await self._ensure_user_membership(
                user_id=user_id,
                company_id=company_id,
            )
        company = await self.repo.get_active_by_id(company_id)
        if not company:
            raise CompanyNotFoundException(company_id=company_id)

        if await self.repo.sector_exists_for_company(company_id, data.nace_code):
            raise CompanySectorConflictException(nace_code=data.nace_code)

        sector = await self.repo.create_sector(
            company_id=company_id,
            nace_code=data.nace_code,
            nace_name=data.nace_name,
            brand_name=data.brand_name,
        )

        await self.db.commit()
        await self.db.refresh(sector)

        logger.info(
            "Company sector created",
            extra={
                "sector_nace_code": sector.nace_code,
                "company_id": str(company_id),
                "company_name": company.name,
            },
        )
        return sector

    async def list_company_sectors(
        self, company_id: uuid.UUID
    ) -> list[CompanySector]:
        """List sectors for a company.

        Args:
            company_id: Company ID

        Returns:
            List of company sectors ordered by created_at asc

        Raises:
            CompanyNotFoundException: If company not found
        """
        company = await self.repo.get_by_id(company_id)
        if not company:
            raise CompanyNotFoundException(company_id=company_id)

        return await self.repo.list_sectors_for_company(company_id)

    async def delete_company_sector(
        self,
        company_id: uuid.UUID,
        sector_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
    ) -> None:
        """Delete a company sector.

        Args:
            company_id: Company ID
            sector_id: Sector ID
            user_id: Optional user ID for membership verification

        Raises:
            CompanyNotFoundException: If company not found or not active
            CompanySectorNotFoundException: If sector not found or not belonging to company
        """
        if user_id is not None:
            await self._ensure_user_membership(
                user_id=user_id,
                company_id=company_id,
            )
        company = await self.repo.get_active_by_id(company_id)
        if not company:
            raise CompanyNotFoundException(company_id=company_id)

        deleted_id = await self.repo.delete_sector_for_company(
            sector_id=sector_id,
            company_id=company_id,
        )

        if deleted_id is None:
            raise CompanySectorNotFoundException(sector_id=sector_id)

        await self.db.commit()

        logger.info(
            "Company sector deleted",
            extra={
                "sector_id": str(sector_id),
                "company_id": str(company_id),
            },
        )

    async def update_company_sector_brand(
        self,
        company_id: uuid.UUID,
        sector_id: uuid.UUID,
        brand_name: str | None,
        user_id: uuid.UUID | None = None,
    ) -> CompanySector:
        """Update a company sector's brand name.

        Args:
            company_id: Company ID
            sector_id: Sector ID
            brand_name: New brand name
            user_id: Optional user ID for membership verification

        Returns:
            Updated sector

        Raises:
            CompanyNotFoundException: If company not found or not active
            CompanySectorNotFoundException: If sector not found or not belonging to company
        """
        if user_id is not None:
            await self._ensure_user_membership(
                user_id=user_id,
                company_id=company_id,
            )
        company = await self.repo.get_active_by_id(company_id)
        if not company:
            raise CompanyNotFoundException(company_id=company_id)

        sector = await self.repo.get_sector_for_company(sector_id, company_id)
        if not sector:
            raise CompanySectorNotFoundException(sector_id=sector_id)

        sector.update_brand_name(brand_name)

        await self.db.commit()
        await self.db.refresh(sector)

        logger.info(
            "Company sector brand updated",
            extra={
                "sector_id": str(sector_id),
                "company_id": str(company_id),
                "company_name": company.name,
            },
        )
        return sector

    # ── Invitation ──

    async def invite_user(
        self,
        *,
        company_id: uuid.UUID,
        email: str,
        role_name: str,
        inviter: User,
    ) -> InvitationResponse:
        """Invite a user to join a company with a specific role.

        Args:
            company_id: Company ID
            email: Email of the user to invite
            role_name: Role to assign (admin, accountant, viewer, consultant)
            inviter: The user sending the invitation

        Returns:
            InvitationResponse

        Raises:
            CompanyNotFoundException: If company not found
            InvalidInvitationRoleException: If role is not invitable
            ConsultantRequiresAdminException: If consultant role for non-admin
            UserAlreadyMemberException: If user is already a member
            InvitationAlreadyExistsException: If pending invite exists
        """
        if role_name not in INVITABLE_ROLES:
            raise InvalidInvitationRoleException(role=role_name)

        company = await self.repo.get_active_by_id(company_id)
        if not company:
            raise CompanyNotFoundException(company_id=company_id)

        # Enforce member limit based on company owner's subscription
        from src.domains.subscriptions.repository import SubscriptionRepository

        sub_repo = SubscriptionRepository(self.db)
        owner_id = await sub_repo.get_company_owner_id(company_id)
        if owner_id:
            from src.domains.subscriptions.service import SubscriptionService

            sub_service = SubscriptionService(self.db)
            await sub_service.enforce_member_limit(owner_id, company_id)

        role = await self.repo.get_role_by_name(role_name)
        if role is None:
            raise InvalidInvitationRoleException(role=role_name)

        user_repo = UserRepository(self.db)

        # Consultant role requires the invitee to be a system Admin
        if role_name == COMPANY_CONSULTANT_ROLE:
            invitee = await user_repo.get_by_email(email)
            if invitee is None or invitee.role != UserRole.ADMIN:
                raise ConsultantRequiresAdminException()

        # Check if user is already a member
        existing_user = await user_repo.get_by_email(email)
        if existing_user and await self.repo.membership_exists(
            user_id=existing_user.id, company_id=company_id
        ):
            raise UserAlreadyMemberException(email=email)

        # Check for existing pending invitation
        existing_invite = await self.repo.get_pending_invitation(company_id, email)
        if existing_invite:
            raise InvitationAlreadyExistsException(email=email)

        # Create invitation
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=CompanyInvitation.INVITATION_VALIDITY_DAYS
        )

        invitation = await self.repo.create_invitation(
            company_id=company_id,
            email=email,
            role_id=role.id,
            invited_by=inviter.id,
            token=token,
            expires_at=expires_at,
        )
        await self.db.commit()
        await self.db.refresh(invitation)

        # Send email
        from src.core.email.service import send_company_invitation_email

        await send_company_invitation_email(
            to_email=email,
            company_name=company.name,
            inviter_name=inviter.full_name or inviter.email,
            role=role_name,
            invite_token=token,
        )

        logger.info(
            "User invited to company",
            extra={
                "email": email,
                "company_id": str(company_id),
                "role": role_name,
            },
        )

        return InvitationResponse(
            id=invitation.id,
            company_id=invitation.company_id,
            email=invitation.email,
            role=role_name,
            is_accepted=invitation.is_accepted,
            expires_at=invitation.expires_at,
            created_at=invitation.created_at,
        )

    async def accept_invitation(
        self,
        *,
        token: str,
        password: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> dict:
        """Accept a company invitation.

        If the user is registered, adds them to the company.
        If not, creates a new account and adds them.

        Args:
            token: Invitation token
            password: Password for new user registration (optional)
            first_name: First name for new user (required if not registered)
            last_name: Last name for new user (required if not registered)

        Returns:
            Dict with accepted: True, company_id, is_new_user
        """
        invitation = await self.repo.get_invitation_by_token(token)

        if invitation is None:
            raise InvalidInvitationException()

        if invitation.is_accepted:
            raise InvalidInvitationException(detail="Invitation already accepted")

        if invitation.is_expired():
            raise InvalidInvitationException(detail="Invitation has expired")

        user_repo = UserRepository(self.db)
        user = await user_repo.get_by_email(invitation.email)
        is_new_user = False

        if user is None:
            if not first_name or not last_name:
                raise InvalidInvitationException(
                    detail="First name and last name are required for new users"
                )
            user = await user_repo.create_oauth_user(
                email=invitation.email,
                first_name=first_name,
                last_name=last_name,
            )
            if password:
                user.set_password(password)
            user.email_verified_at = datetime.now(timezone.utc)
            await self.db.flush()

            # Assign freemium subscription to new user
            from src.domains.subscriptions.service import SubscriptionService

            sub_service = SubscriptionService(self.db)
            await sub_service.create_freemium(user.id)

            is_new_user = True

        # Check if already a member
        if await self.repo.membership_exists(
            user_id=user.id, company_id=invitation.company_id
        ):
            invitation.accept()
            await self.db.commit()
            raise UserAlreadyMemberException(email=invitation.email)

        await self.repo.create_membership(
            user_id=user.id,
            company_id=invitation.company_id,
            role_id=invitation.role_id,
        )
        invitation.accept()
        await self.db.commit()

        logger.info(
            "Invitation accepted",
            extra={
                "email": invitation.email,
                "company_id": str(invitation.company_id),
                "is_new_user": is_new_user,
            },
        )

        return {
            "accepted": True,
            "company_id": str(invitation.company_id),
            "is_new_user": is_new_user,
        }
