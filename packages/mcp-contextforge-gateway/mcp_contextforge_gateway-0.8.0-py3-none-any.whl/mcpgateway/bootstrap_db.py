# -*- coding: utf-8 -*-
"""Location: ./mcpgateway/bootstrap_db.py
Copyright 2025
SPDX-License-Identifier: Apache-2.0
Authors: Madhav Kandukuri

Database bootstrap/upgrade entry-point for MCP Gateway.
The script:

1. Creates a synchronous SQLAlchemy ``Engine`` from ``settings.database_url``.
2. Looks for an *alembic.ini* two levels up from this file to drive migrations.
3. Applies Alembic migrations (``alembic upgrade head``) to create or update the schema.
4. Runs post-upgrade normalization tasks and bootstraps admin/roles as configured.
5. Logs a **"Database ready"** message on success.

It is intended to be invoked via ``python3 -m mcpgateway.bootstrap_db`` or
directly with ``python3 mcpgateway/bootstrap_db.py``.

Examples:
    >>> from mcpgateway.bootstrap_db import logging_service, logger
    >>> logging_service is not None
    True
    >>> logger is not None
    True
    >>> hasattr(logger, 'info')
    True
    >>> from mcpgateway.bootstrap_db import Base
    >>> hasattr(Base, 'metadata')
    True
"""

# Standard
import asyncio
from importlib.resources import files
from typing import Any, cast

# Third-Party
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

# First-Party
from mcpgateway.config import settings
from mcpgateway.db import A2AAgent, Base, EmailTeam, EmailUser, Gateway, Prompt, Resource, Server, SessionLocal, Tool
from mcpgateway.services.logging_service import LoggingService

# Initialize logging service first
logging_service = LoggingService()
logger = logging_service.get_logger(__name__)


async def bootstrap_admin_user() -> None:
    """
    Bootstrap the platform admin user from environment variables.

    Creates the admin user if email authentication is enabled and the user doesn't exist.
    Also creates a personal team for the admin user if auto-creation is enabled.
    """
    if not settings.email_auth_enabled:
        logger.info("Email authentication disabled - skipping admin user bootstrap")
        return

    try:
        # Import services here to avoid circular imports
        # First-Party
        from mcpgateway.services.email_auth_service import EmailAuthService  # pylint: disable=import-outside-toplevel

        with cast(Any, SessionLocal)() as db:
            auth_service = EmailAuthService(db)

            # Check if admin user already exists
            existing_user = await auth_service.get_user_by_email(settings.platform_admin_email)
            if existing_user:
                logger.info(f"Admin user {settings.platform_admin_email} already exists - skipping creation")
                return

            # Create admin user
            logger.info(f"Creating platform admin user: {settings.platform_admin_email}")
            admin_user = await auth_service.create_user(
                email=settings.platform_admin_email,
                password=settings.platform_admin_password,
                full_name=settings.platform_admin_full_name,
                is_admin=True,
            )

            # Mark admin user as email verified
            # First-Party
            from mcpgateway.db import utc_now  # pylint: disable=import-outside-toplevel

            admin_user.email_verified_at = utc_now()
            db.commit()

            # Personal team is automatically created during user creation if enabled
            if settings.auto_create_personal_teams:
                logger.info("Personal team automatically created for admin user")

            db.commit()
            logger.info(f"Platform admin user created successfully: {settings.platform_admin_email}")

    except Exception as e:
        logger.error(f"Failed to bootstrap admin user: {e}")
        # Don't fail the entire bootstrap process if admin user creation fails
        return


async def bootstrap_default_roles() -> None:
    """Bootstrap default system roles and assign them to admin user.

    Creates essential RBAC roles and assigns administrative privileges
    to the platform admin user.
    """
    if not settings.email_auth_enabled:
        logger.info("Email authentication disabled - skipping default roles bootstrap")
        return

    try:
        # First-Party
        from mcpgateway.db import get_db  # pylint: disable=import-outside-toplevel
        from mcpgateway.services.email_auth_service import EmailAuthService  # pylint: disable=import-outside-toplevel
        from mcpgateway.services.role_service import RoleService  # pylint: disable=import-outside-toplevel

        # Get database session
        db_gen = get_db()
        db = next(db_gen)

        try:
            role_service = RoleService(db)
            auth_service = EmailAuthService(db)

            # Check if admin user exists
            admin_user = await auth_service.get_user_by_email(settings.platform_admin_email)
            if not admin_user:
                logger.info("Admin user not found - skipping role assignment")
                return

            # Default system roles to create
            default_roles = [
                {"name": "platform_admin", "description": "Platform administrator with all permissions", "scope": "global", "permissions": ["*"], "is_system_role": True},  # All permissions
                {
                    "name": "team_admin",
                    "description": "Team administrator with team management permissions",
                    "scope": "team",
                    "permissions": ["teams.read", "teams.update", "teams.join", "teams.manage_members", "tools.read", "tools.execute", "resources.read", "prompts.read"],
                    "is_system_role": True,
                },
                {
                    "name": "developer",
                    "description": "Developer with tool and resource access",
                    "scope": "team",
                    "permissions": ["teams.join", "tools.read", "tools.execute", "resources.read", "prompts.read"],
                    "is_system_role": True,
                },
                {
                    "name": "viewer",
                    "description": "Read-only access to resources",
                    "scope": "team",
                    "permissions": ["teams.join", "tools.read", "resources.read", "prompts.read"],
                    "is_system_role": True,
                },
            ]

            # Create default roles
            created_roles = []
            for role_def in default_roles:
                try:
                    # Check if role already exists
                    existing_role = await role_service.get_role_by_name(str(role_def["name"]), str(role_def["scope"]))
                    if existing_role:
                        logger.info(f"System role {role_def['name']} already exists - skipping")
                        created_roles.append(existing_role)
                        continue

                    # Create the role
                    role = await role_service.create_role(
                        name=str(role_def["name"]),
                        description=str(role_def["description"]),
                        scope=str(role_def["scope"]),
                        permissions=cast(list[str], role_def["permissions"]),
                        created_by=settings.platform_admin_email,
                        is_system_role=bool(role_def["is_system_role"]),
                    )
                    created_roles.append(role)
                    logger.info(f"Created system role: {role.name}")

                except Exception as e:
                    logger.error(f"Failed to create role {role_def['name']}: {e}")
                    continue

            # Assign platform_admin role to admin user
            platform_admin_role = next((r for r in created_roles if r.name == "platform_admin"), None)
            if platform_admin_role:
                try:
                    # Check if assignment already exists
                    existing_assignment = await role_service.get_user_role_assignment(user_email=admin_user.email, role_id=platform_admin_role.id, scope="global", scope_id=None)

                    if not existing_assignment or not existing_assignment.is_active:
                        await role_service.assign_role_to_user(user_email=admin_user.email, role_id=platform_admin_role.id, scope="global", scope_id=None, granted_by=admin_user.email)
                        logger.info(f"Assigned platform_admin role to {admin_user.email}")
                    else:
                        logger.info("Admin user already has platform_admin role")

                except Exception as e:
                    logger.error(f"Failed to assign platform_admin role: {e}")

            logger.info("Default RBAC roles bootstrap completed successfully")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Failed to bootstrap default roles: {e}")
        # Don't fail the entire bootstrap process if role creation fails
        return


def normalize_team_visibility() -> int:
    """Normalize team visibility values to the supported set {private, public}.

    Any team with an unsupported visibility (e.g., 'team') is set to 'private'.

    Returns:
        int: Number of teams updated
    """
    try:
        with cast(Any, SessionLocal)() as db:
            # Find teams with invalid visibility
            invalid = db.query(EmailTeam).filter(EmailTeam.visibility.notin_(["private", "public"]))
            count = 0
            for team in invalid.all():
                old = team.visibility
                team.visibility = "private"
                count += 1
                logger.info(f"Normalized team visibility: id={team.id} {old} -> private")
            if count:
                db.commit()
            return count
    except Exception as e:
        logger.error(f"Failed to normalize team visibility: {e}")
        return 0


async def main() -> None:
    """
    Bootstrap or upgrade the database schema, then log readiness.

    Runs `create_all()` + `alembic stamp head` on an empty DB, otherwise just
    executes `alembic upgrade head`, leaving application data intact.
    Also creates the platform admin user if email authentication is enabled.

    Args:
        None
    """
    engine = create_engine(settings.database_url)
    ini_path = files("mcpgateway").joinpath("alembic.ini")
    cfg = Config(str(ini_path))  # path in container
    cfg.attributes["configure_logger"] = True

    with engine.begin() as conn:
        cfg.attributes["connection"] = conn
        cfg.set_main_option("sqlalchemy.url", settings.database_url)

        insp = inspect(conn)

        if "gateways" not in insp.get_table_names():
            logger.info("Empty DB detected - creating baseline schema")
            Base.metadata.create_all(bind=conn)
            command.stamp(cfg, "head")
        else:
            logger.info("Running Alembic migrations to ensure schema is up to date")
            command.upgrade(cfg, "head")

    # Post-upgrade normalization passes
    updated = normalize_team_visibility()
    if updated:
        logger.info(f"Normalized {updated} team record(s) to supported visibility values")

    logger.info("Database ready")

    # Bootstrap admin user after database is ready
    await bootstrap_admin_user()

    # Bootstrap default RBAC roles after admin user is created
    await bootstrap_default_roles()

    # Assign orphaned resources to admin personal team after all setup is complete
    await bootstrap_resource_assignments()


async def bootstrap_resource_assignments() -> None:
    """Assign orphaned resources to the platform admin's personal team.

    This ensures existing resources (from pre-multitenancy versions) are
    visible in the new team-based UI by assigning them to the admin's
    personal team with public visibility.
    """
    if not settings.email_auth_enabled:
        logger.info("Email authentication disabled - skipping resource assignment")
        return

    try:
        with SessionLocal() as db:
            # Find admin user and their personal team
            admin_user = db.query(EmailUser).filter(EmailUser.email == settings.platform_admin_email, EmailUser.is_admin.is_(True)).first()

            if not admin_user:
                logger.warning("Admin user not found - skipping resource assignment")
                return

            personal_team = admin_user.get_personal_team()
            if not personal_team:
                logger.warning("Admin personal team not found - skipping resource assignment")
                return

            logger.info(f"Assigning orphaned resources to admin team: {personal_team.name}")

            # Resource types to process
            resource_types = [("servers", Server), ("tools", Tool), ("resources", Resource), ("prompts", Prompt), ("gateways", Gateway), ("a2a_agents", A2AAgent)]

            total_assigned = 0

            for resource_name, resource_model in resource_types:
                try:
                    # Find unassigned resources
                    unassigned = db.query(resource_model).filter((resource_model.team_id.is_(None)) | (resource_model.owner_email.is_(None)) | (resource_model.visibility.is_(None))).all()

                    if unassigned:
                        logger.info(f"Assigning {len(unassigned)} orphaned {resource_name} to admin team")

                        for resource in unassigned:
                            resource.team_id = personal_team.id
                            resource.owner_email = admin_user.email
                            resource.visibility = "public"  # Make visible to all users
                            if hasattr(resource, "federation_source") and not resource.federation_source:
                                resource.federation_source = "mcpgateway-0.7.0-migration"

                        db.commit()
                        total_assigned += len(unassigned)

                except Exception as e:
                    logger.error(f"Failed to assign {resource_name}: {e}")
                    continue

            if total_assigned > 0:
                logger.info(f"Successfully assigned {total_assigned} orphaned resources to admin team")
            else:
                logger.info("No orphaned resources found - all resources have team assignments")

    except Exception as e:
        logger.error(f"Failed to bootstrap resource assignments: {e}")


if __name__ == "__main__":
    asyncio.run(main())
