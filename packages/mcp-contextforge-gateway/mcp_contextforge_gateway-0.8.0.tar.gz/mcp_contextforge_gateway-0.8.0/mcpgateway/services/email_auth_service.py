# -*- coding: utf-8 -*-
"""Location: ./mcpgateway/services/email_auth_service.py
Copyright 2025
SPDX-License-Identifier: Apache-2.0
Authors: Mihai Criveti

Email Authentication Service.
This module provides email-based user authentication services including
user creation, authentication, password management, and security features.

Examples:
    Basic usage (requires async context):
        from mcpgateway.services.email_auth_service import EmailAuthService
        from mcpgateway.db import SessionLocal

        with SessionLocal() as db:
            service = EmailAuthService(db)
            # Use in async context:
            # user = await service.create_user("test@example.com", "password123")
            # authenticated = await service.authenticate_user("test@example.com", "password123")
"""

# Standard
from datetime import datetime, timezone
import re
from typing import Optional

# Third-Party
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# First-Party
from mcpgateway.config import settings
from mcpgateway.db import EmailAuthEvent, EmailUser
from mcpgateway.services.argon2_service import Argon2PasswordService
from mcpgateway.services.logging_service import LoggingService

# Initialize logging
logging_service = LoggingService()
logger = logging_service.get_logger(__name__)


class EmailValidationError(Exception):
    """Raised when email format is invalid.

    Examples:
        >>> try:
        ...     raise EmailValidationError("Invalid email format")
        ... except EmailValidationError as e:
        ...     str(e)
        'Invalid email format'
    """


class PasswordValidationError(Exception):
    """Raised when password doesn't meet policy requirements.

    Examples:
        >>> try:
        ...     raise PasswordValidationError("Password too short")
        ... except PasswordValidationError as e:
        ...     str(e)
        'Password too short'
    """


class UserExistsError(Exception):
    """Raised when attempting to create a user that already exists.

    Examples:
        >>> try:
        ...     raise UserExistsError("User already exists")
        ... except UserExistsError as e:
        ...     str(e)
        'User already exists'
    """


class AuthenticationError(Exception):
    """Raised when authentication fails.

    Examples:
        >>> try:
        ...     raise AuthenticationError("Invalid credentials")
        ... except AuthenticationError as e:
        ...     str(e)
        'Invalid credentials'
    """


class EmailAuthService:
    """Service for email-based user authentication.

    This service handles user registration, authentication, password management,
    and security features like account lockout and failed attempt tracking.

    Attributes:
        db (Session): Database session
        password_service (Argon2PasswordService): Password hashing service

    Examples:
        >>> from mcpgateway.db import SessionLocal
        >>> with SessionLocal() as db:
        ...     service = EmailAuthService(db)
        ...     # Service is ready to use
    """

    def __init__(self, db: Session):
        """Initialize the email authentication service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.password_service = Argon2PasswordService()
        logger.debug("EmailAuthService initialized")

    def validate_email(self, email: str) -> bool:
        """Validate email address format.

        Args:
            email: Email address to validate

        Returns:
            bool: True if email is valid

        Raises:
            EmailValidationError: If email format is invalid

        Examples:
            >>> service = EmailAuthService(None)
            >>> service.validate_email("user@example.com")
            True
            >>> service.validate_email("test.user+tag@domain.co.uk")
            True
            >>> service.validate_email("user123@test-domain.com")
            True
            >>> try:
            ...     service.validate_email("invalid-email")
            ... except EmailValidationError as e:
            ...     "Invalid email format" in str(e)
            True
            >>> try:
            ...     service.validate_email("")
            ... except EmailValidationError as e:
            ...     "Email is required" in str(e)
            True
            >>> try:
            ...     service.validate_email("user@")
            ... except EmailValidationError as e:
            ...     "Invalid email format" in str(e)
            True
            >>> try:
            ...     service.validate_email("@domain.com")
            ... except EmailValidationError as e:
            ...     "Invalid email format" in str(e)
            True
            >>> try:
            ...     service.validate_email("user@domain")
            ... except EmailValidationError as e:
            ...     "Invalid email format" in str(e)
            True
            >>> try:
            ...     service.validate_email("a" * 250 + "@domain.com")
            ... except EmailValidationError as e:
            ...     "Email address too long" in str(e)
            True
            >>> try:
            ...     service.validate_email(None)
            ... except EmailValidationError as e:
            ...     "Email is required" in str(e)
            True
        """
        if not email or not isinstance(email, str):
            raise EmailValidationError("Email is required and must be a string")

        # Basic email regex pattern
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if not re.match(email_pattern, email):
            raise EmailValidationError("Invalid email format")

        if len(email) > 255:
            raise EmailValidationError("Email address too long (max 255 characters)")

        return True

    def validate_password(self, password: str) -> bool:
        """Validate password against policy requirements.

        Args:
            password: Password to validate

        Returns:
            bool: True if password meets policy

        Raises:
            PasswordValidationError: If password doesn't meet requirements

        Examples:
            >>> service = EmailAuthService(None)
            >>> service.validate_password("password123")
            True
            >>> service.validate_password("ValidPassword123!")
            True
            >>> service.validate_password("shortpass")  # 8+ chars to meet default min_length
            True
            >>> service.validate_password("verylongpasswordthatmeetsminimumrequirements")
            True
            >>> try:
            ...     service.validate_password("")
            ... except PasswordValidationError as e:
            ...     "Password is required" in str(e)
            True
            >>> try:
            ...     service.validate_password(None)
            ... except PasswordValidationError as e:
            ...     "Password is required" in str(e)
            True
            >>> try:
            ...     service.validate_password("short")  # Only 5 chars, should fail with default min_length=8
            ... except PasswordValidationError as e:
            ...     "characters long" in str(e)
            True
        """
        if not password:
            raise PasswordValidationError("Password is required")

        # Get password policy settings
        min_length = getattr(settings, "password_min_length", 8)
        require_uppercase = getattr(settings, "password_require_uppercase", False)
        require_lowercase = getattr(settings, "password_require_lowercase", False)
        require_numbers = getattr(settings, "password_require_numbers", False)
        require_special = getattr(settings, "password_require_special", False)

        if len(password) < min_length:
            raise PasswordValidationError(f"Password must be at least {min_length} characters long")

        if require_uppercase and not re.search(r"[A-Z]", password):
            raise PasswordValidationError("Password must contain at least one uppercase letter")

        if require_lowercase and not re.search(r"[a-z]", password):
            raise PasswordValidationError("Password must contain at least one lowercase letter")

        if require_numbers and not re.search(r"[0-9]", password):
            raise PasswordValidationError("Password must contain at least one number")

        if require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise PasswordValidationError("Password must contain at least one special character")

        return True

    async def get_user_by_email(self, email: str) -> Optional[EmailUser]:
        """Get user by email address.

        Args:
            email: Email address to look up

        Returns:
            EmailUser or None if not found

        Examples:
            # Assuming database has user "test@example.com"
            # user = await service.get_user_by_email("test@example.com")
            # user.email if user else None  # Returns: 'test@example.com'
        """
        try:
            stmt = select(EmailUser).where(EmailUser.email == email.lower())
            result = self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None

    async def create_user(self, email: str, password: str, full_name: Optional[str] = None, is_admin: bool = False, auth_provider: str = "local") -> EmailUser:
        """Create a new user with email authentication.

        Args:
            email: User's email address (primary key)
            password: Plain text password (will be hashed)
            full_name: Optional full name for display
            is_admin: Whether user has admin privileges
            auth_provider: Authentication provider ('local', 'github', etc.)

        Returns:
            EmailUser: The created user object

        Raises:
            EmailValidationError: If email format is invalid
            PasswordValidationError: If password doesn't meet policy
            UserExistsError: If user already exists

        Examples:
            # user = await service.create_user(
            #     email="new@example.com",
            #     password="secure123",
            #     full_name="New User"
            # )
            # user.email          # Returns: 'new@example.com'
            # user.full_name      # Returns: 'New User'
        """
        # Normalize email to lowercase
        email = email.lower().strip()

        # Validate inputs
        self.validate_email(email)
        self.validate_password(password)

        # Check if user already exists
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            raise UserExistsError(f"User with email {email} already exists")

        # Hash the password
        password_hash = self.password_service.hash_password(password)

        # Create new user
        user = EmailUser(email=email, password_hash=password_hash, full_name=full_name, is_admin=is_admin, auth_provider=auth_provider)

        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            logger.info(f"Created new user: {email}")

            # Create personal team if enabled
            if getattr(settings, "auto_create_personal_teams", True):
                try:
                    # Import here to avoid circular imports
                    # First-Party
                    from mcpgateway.services.personal_team_service import PersonalTeamService  # pylint: disable=import-outside-toplevel

                    personal_team_service = PersonalTeamService(self.db)
                    personal_team = await personal_team_service.create_personal_team(user)
                    logger.info(f"Created personal team '{personal_team.name}' for user {email}")
                except Exception as e:
                    logger.warning(f"Failed to create personal team for {email}: {e}")
                    # Don't fail user creation if personal team creation fails

            # Log registration event
            registration_event = EmailAuthEvent.create_registration_event(user_email=email, success=True)
            self.db.add(registration_event)
            self.db.commit()

            return user

        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Database error creating user {email}: {e}")
            raise UserExistsError(f"User with email {email} already exists") from e
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error creating user {email}: {e}")

            # Log failed registration
            registration_event = EmailAuthEvent.create_registration_event(user_email=email, success=False, failure_reason=str(e))
            self.db.add(registration_event)
            self.db.commit()

            raise

    async def authenticate_user(self, email: str, password: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Optional[EmailUser]:
        """Authenticate a user with email and password.

        Args:
            email: User's email address
            password: Plain text password
            ip_address: Client IP address for logging
            user_agent: Client user agent for logging

        Returns:
            EmailUser if authentication successful, None otherwise

        Examples:
            # user = await service.authenticate_user("user@example.com", "correct_password")
            # user.email if user else None  # Returns: 'user@example.com'
            # await service.authenticate_user("user@example.com", "wrong_password")  # Returns: None
        """
        email = email.lower().strip()

        # Get user from database
        user = await self.get_user_by_email(email)

        # Track authentication attempt
        auth_success = False
        failure_reason = None

        try:
            if not user:
                failure_reason = "User not found"
                logger.info(f"Authentication failed for {email}: user not found")
                return None

            if not user.is_active:
                failure_reason = "Account is disabled"
                logger.info(f"Authentication failed for {email}: account disabled")
                return None

            if user.is_account_locked():
                failure_reason = "Account is locked"
                logger.info(f"Authentication failed for {email}: account locked")
                return None

            # Verify password
            if not self.password_service.verify_password(password, user.password_hash):
                failure_reason = "Invalid password"

                # Increment failed attempts
                max_attempts = getattr(settings, "max_failed_login_attempts", 5)
                lockout_duration = getattr(settings, "account_lockout_duration_minutes", 30)

                is_locked = user.increment_failed_attempts(max_attempts, lockout_duration)

                if is_locked:
                    logger.warning(f"Account locked for {email} after {max_attempts} failed attempts")
                    failure_reason = "Account locked due to too many failed attempts"

                self.db.commit()
                logger.info(f"Authentication failed for {email}: invalid password")
                return None

            # Authentication successful
            user.reset_failed_attempts()
            self.db.commit()

            auth_success = True
            logger.info(f"Authentication successful for {email}")

            return user

        finally:
            # Log authentication event
            auth_event = EmailAuthEvent.create_login_attempt(user_email=email, success=auth_success, ip_address=ip_address, user_agent=user_agent, failure_reason=failure_reason)
            self.db.add(auth_event)
            self.db.commit()

    async def change_password(self, email: str, old_password: str, new_password: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> bool:
        """Change a user's password.

        Args:
            email: User's email address
            old_password: Current password for verification
            new_password: New password to set
            ip_address: Client IP address for logging
            user_agent: Client user agent for logging

        Returns:
            bool: True if password changed successfully

        Raises:
            AuthenticationError: If old password is incorrect
            PasswordValidationError: If new password doesn't meet policy
            Exception: If database operation fails

        Examples:
            # success = await service.change_password(
            #     "user@example.com",
            #     "old_password",
            #     "new_secure_password"
            # )
            # success              # Returns: True
        """
        # First authenticate with old password
        user = await self.authenticate_user(email, old_password, ip_address, user_agent)
        if not user:
            raise AuthenticationError("Current password is incorrect")

        # Validate new password
        self.validate_password(new_password)

        # Check if new password is same as old (optional policy)
        if self.password_service.verify_password(new_password, user.password_hash):
            raise PasswordValidationError("New password must be different from current password")

        success = False
        try:
            # Hash new password and update
            new_password_hash = self.password_service.hash_password(new_password)
            user.password_hash = new_password_hash

            self.db.commit()
            success = True

            logger.info(f"Password changed successfully for {email}")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error changing password for {email}: {e}")
            raise
        finally:
            # Log password change event
            password_event = EmailAuthEvent.create_password_change_event(user_email=email, success=success, ip_address=ip_address, user_agent=user_agent)
            self.db.add(password_event)
            self.db.commit()

        return success

    async def create_platform_admin(self, email: str, password: str, full_name: Optional[str] = None) -> EmailUser:
        """Create or update the platform administrator user.

        This method is used during system bootstrap to create the initial
        admin user from environment variables.

        Args:
            email: Admin email address
            password: Admin password
            full_name: Admin full name

        Returns:
            EmailUser: The admin user

        Examples:
            # admin = await service.create_platform_admin(
            #     "admin@example.com",
            #     "admin_password",
            #     "Platform Administrator"
            # )
            # admin.is_admin       # Returns: True
        """
        # Check if admin user already exists
        existing_admin = await self.get_user_by_email(email)

        if existing_admin:
            # Update existing admin if password or name changed
            if full_name and existing_admin.full_name != full_name:
                existing_admin.full_name = full_name

            # Check if password needs update (verify current password first)
            if not self.password_service.verify_password(password, existing_admin.password_hash):
                existing_admin.password_hash = self.password_service.hash_password(password)

            # Ensure admin status
            existing_admin.is_admin = True
            existing_admin.is_active = True

            self.db.commit()
            logger.info(f"Updated platform admin user: {email}")
            return existing_admin

        # Create new admin user
        admin_user = await self.create_user(email=email, password=password, full_name=full_name, is_admin=True, auth_provider="local")

        logger.info(f"Created platform admin user: {email}")
        return admin_user

    async def update_last_login(self, email: str) -> None:
        """Update the last login timestamp for a user.

        Args:
            email: User's email address
        """
        user = await self.get_user_by_email(email)
        if user:
            user.reset_failed_attempts()  # This also updates last_login
            self.db.commit()

    async def list_users(self, limit: int = 100, offset: int = 0) -> list[EmailUser]:
        """List all users with pagination.

        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip

        Returns:
            List of EmailUser objects

        Examples:
            # users = await service.list_users(limit=10)
            # len(users) <= 10     # Returns: True
        """
        try:
            stmt = select(EmailUser).offset(offset).limit(limit)
            result = self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return []

    async def get_all_users(self) -> list[EmailUser]:
        """Get all users without pagination.

        Returns:
            List of all EmailUser objects

        Examples:
            # users = await service.get_all_users()
            # isinstance(users, list)  # Returns: True
        """
        return await self.list_users(limit=10000)  # Large limit to get all users

    async def count_users(self) -> int:
        """Count total number of users.

        Returns:
            int: Total user count
        """
        try:
            stmt = select(EmailUser)
            result = self.db.execute(stmt)
            return len(list(result.scalars().all()))
        except Exception as e:
            logger.error(f"Error counting users: {e}")
            return 0

    async def get_auth_events(self, email: Optional[str] = None, limit: int = 100, offset: int = 0) -> list[EmailAuthEvent]:
        """Get authentication events for auditing.

        Args:
            email: Filter by specific user email (optional)
            limit: Maximum number of events to return
            offset: Number of events to skip

        Returns:
            List of EmailAuthEvent objects
        """
        try:
            stmt = select(EmailAuthEvent)
            if email:
                stmt = stmt.where(EmailAuthEvent.user_email == email)
            stmt = stmt.order_by(EmailAuthEvent.timestamp.desc()).offset(offset).limit(limit)

            result = self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting auth events: {e}")
            return []

    async def update_user(self, email: str, full_name: Optional[str] = None, is_admin: Optional[bool] = None, password: Optional[str] = None) -> EmailUser:
        """Update user information.

        Args:
            email: User's email address (primary key)
            full_name: New full name (optional)
            is_admin: New admin status (optional)
            password: New password (optional, will be hashed)

        Returns:
            EmailUser: Updated user object

        Raises:
            ValueError: If user doesn't exist
            PasswordValidationError: If password doesn't meet policy
        """
        try:
            # Get existing user
            stmt = select(EmailUser).where(EmailUser.email == email)
            result = self.db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                raise ValueError(f"User {email} not found")

            # Update fields if provided
            if full_name is not None:
                user.full_name = full_name

            if is_admin is not None:
                user.is_admin = is_admin

            if password is not None:
                if not self.validate_password(password):
                    raise ValueError("Password does not meet security requirements")
                user.password_hash = self.password_service.hash_password(password)

            user.updated_at = datetime.now(timezone.utc)

            self.db.commit()
            return user

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating user {email}: {e}")
            raise

    async def activate_user(self, email: str) -> EmailUser:
        """Activate a user account.

        Args:
            email: User's email address

        Returns:
            EmailUser: Updated user object

        Raises:
            ValueError: If user doesn't exist
        """
        try:
            stmt = select(EmailUser).where(EmailUser.email == email)
            result = self.db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                raise ValueError(f"User {email} not found")

            user.is_active = True
            user.updated_at = datetime.now(timezone.utc)

            self.db.commit()
            logger.info(f"User {email} activated")
            return user

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error activating user {email}: {e}")
            raise

    async def deactivate_user(self, email: str) -> EmailUser:
        """Deactivate a user account.

        Args:
            email: User's email address

        Returns:
            EmailUser: Updated user object

        Raises:
            ValueError: If user doesn't exist
        """
        try:
            stmt = select(EmailUser).where(EmailUser.email == email)
            result = self.db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                raise ValueError(f"User {email} not found")

            user.is_active = False
            user.updated_at = datetime.now(timezone.utc)

            self.db.commit()
            logger.info(f"User {email} deactivated")
            return user

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deactivating user {email}: {e}")
            raise

    async def delete_user(self, email: str) -> bool:
        """Delete a user account permanently.

        Args:
            email: User's email address

        Returns:
            bool: True if user was deleted

        Raises:
            ValueError: If user doesn't exist
            ValueError: If user owns teams that cannot be transferred
        """
        try:
            stmt = select(EmailUser).where(EmailUser.email == email)
            result = self.db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                raise ValueError(f"User {email} not found")

            # Check if user owns any teams
            # First-Party
            from mcpgateway.db import EmailTeam, EmailTeamMember  # pylint: disable=import-outside-toplevel

            teams_owned_stmt = select(EmailTeam).where(EmailTeam.created_by == email)
            teams_owned = self.db.execute(teams_owned_stmt).scalars().all()

            if teams_owned:
                # For each team, try to transfer ownership to another owner
                for team in teams_owned:
                    # Find other team owners who can take ownership
                    potential_owners_stmt = (
                        select(EmailTeamMember).where(EmailTeamMember.team_id == team.id, EmailTeamMember.user_email != email, EmailTeamMember.role == "owner").order_by(EmailTeamMember.role.desc())
                    )

                    potential_owners = self.db.execute(potential_owners_stmt).scalars().all()

                    if potential_owners:
                        # Transfer ownership to the first available owner
                        new_owner = potential_owners[0]
                        team.created_by = new_owner.user_email
                        logger.info(f"Transferred team '{team.name}' ownership from {email} to {new_owner.user_email}")
                    else:
                        # No other owners available - check if it's a single-user team
                        all_members_stmt = select(EmailTeamMember).where(EmailTeamMember.team_id == team.id)
                        all_members = self.db.execute(all_members_stmt).scalars().all()

                        if len(all_members) == 1 and all_members[0].user_email == email:
                            # This is a single-user personal team - cascade delete it
                            logger.info(f"Deleting personal team '{team.name}' (single member: {email})")
                            # Delete team members first (should be just the owner)
                            delete_team_members_stmt = delete(EmailTeamMember).where(EmailTeamMember.team_id == team.id)
                            self.db.execute(delete_team_members_stmt)
                            # Delete the team
                            self.db.delete(team)
                        else:
                            # Multi-member team with no other owners - cannot delete user
                            raise ValueError(f"Cannot delete user {email}: owns team '{team.name}' with {len(all_members)} members but no other owners to transfer ownership to")

            # Delete related auth events first
            auth_events_stmt = delete(EmailAuthEvent).where(EmailAuthEvent.user_email == email)
            self.db.execute(auth_events_stmt)

            # Remove user from all team memberships
            team_members_stmt = delete(EmailTeamMember).where(EmailTeamMember.user_email == email)
            self.db.execute(team_members_stmt)

            # Delete the user
            self.db.delete(user)
            self.db.commit()

            logger.info(f"User {email} deleted permanently")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting user {email}: {e}")
            raise

    async def count_active_admin_users(self) -> int:
        """Count the number of active admin users.

        Returns:
            int: Number of active admin users
        """
        stmt = select(func.count(EmailUser.email)).where(EmailUser.is_admin.is_(True), EmailUser.is_active.is_(True))  # pylint: disable=not-callable
        result = self.db.execute(stmt)
        return result.scalar() or 0

    async def is_last_active_admin(self, email: str) -> bool:
        """Check if the given user is the last active admin.

        Args:
            email: User's email address

        Returns:
            bool: True if this user is the last active admin
        """
        # First check if the user is an active admin
        stmt = select(EmailUser).where(EmailUser.email == email)
        result = self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not user.is_admin or not user.is_active:
            return False

        # Count total active admins
        admin_count = await self.count_active_admin_users()
        return admin_count == 1
