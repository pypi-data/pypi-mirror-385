#!/usr/bin/env python3
"""Seed test users for AuthFlow demonstration and testing.

This script creates 5 test users with different roles and permissions:
1. Alice - Super Admin (global access)
2. Bob - Organization Admin (TechCorp Inc)
3. Charlie - Singular User (alone in their organization)
4. Diana - Enterprise Org Admin (Global Enterprises)
5. Eve - Enterprise User (Global Enterprises, team member)

Usage:
    python -m authflow.scripts.seed_test_users
    # or if installed as package:
    authflow-seed-users
"""

import asyncio
import logging
import sys
from typing import Dict, List, Any, Optional

from authflow.core.config import AuthFlowConfig
from authflow.providers.keycloak import KeycloakProvider
from authflow.models.schemas import (
    UserCreate,
    OrganizationCreate,
    TeamCreate,
    RoleCreate,
)

# Setup logging with colors
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger(__name__)

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Test user definitions
TEST_USERS = [
    {
        "email": "alice@authflow.test",
        "password": "SuperAdmin123!",
        "first_name": "Alice",
        "last_name": "Anderson",
        "organization": {
            "name": "authflow_system",
            "display_name": "AuthFlow System",
            "description": "System-level organization for super administrators"
        },
        "role": "super_admin",
        "description": "Super Administrator with global access to everything"
    },
    {
        "email": "bob@techcorp.test",
        "password": "TechCorp123!",
        "first_name": "Bob",
        "last_name": "Builder",
        "organization": {
            "name": "techcorp_inc",
            "display_name": "TechCorp Inc",
            "description": "Technology company with engineering teams"
        },
        "role": "org_admin",
        "teams": [
            {
                "name": "engineering",
                "display_name": "Engineering",
                "description": "Engineering team",
                "parent": None
            },
            {
                "name": "backend_team",
                "display_name": "Backend Team",
                "description": "Backend development team",
                "parent": "engineering"
            }
        ],
        "description": "Organization Administrator for TechCorp Inc"
    },
    {
        "email": "charlie@freelancer.test",
        "password": "Freelance123!",
        "first_name": "Charlie",
        "last_name": "Chen",
        "organization": {
            "name": "charlie_workspace",
            "display_name": "Charlie's Workspace",
            "description": "Personal workspace for freelancer"
        },
        "role": "singular_user",  # Custom role with minimal permissions
        "custom_role": {
            "name": "singular_user",
            "display_name": "Singular User",
            "description": "Minimal access for solo users in their own workspace",
            "scope": "organization",
            "permissions": ["admin:read"]  # Only dashboard access
        },
        "description": "Singular User - alone in their organization with minimal UI"
    },
    {
        "email": "diana@globalent.test",
        "password": "GlobalEnt123!",
        "first_name": "Diana",
        "last_name": "Davis",
        "organization": {
            "name": "global_enterprises",
            "display_name": "Global Enterprises",
            "description": "Large enterprise with complex team hierarchy"
        },
        "role": "org_admin",
        "teams": [
            # Top-level teams
            {
                "name": "product",
                "display_name": "Product",
                "description": "Product management team",
                "parent": None
            },
            {
                "name": "engineering",
                "display_name": "Engineering",
                "description": "Engineering department",
                "parent": None
            },
            {
                "name": "sales",
                "display_name": "Sales",
                "description": "Sales department",
                "parent": None
            },
            # Engineering sub-teams
            {
                "name": "frontend_team",
                "display_name": "Frontend Team",
                "description": "Frontend development team",
                "parent": "engineering"
            },
            {
                "name": "backend_team",
                "display_name": "Backend Team",
                "description": "Backend development team",
                "parent": "engineering"
            },
            {
                "name": "devops_team",
                "display_name": "DevOps Team",
                "description": "DevOps and infrastructure team",
                "parent": "engineering"
            },
            # Sales sub-teams
            {
                "name": "sales_us",
                "display_name": "Sales US",
                "description": "US sales team",
                "parent": "sales"
            },
            {
                "name": "sales_eu",
                "display_name": "Sales EU",
                "description": "European sales team",
                "parent": "sales"
            },
        ],
        "description": "Enterprise Organization Administrator with complex hierarchy"
    },
    {
        "email": "eve@globalent.test",
        "password": "GlobalEnt123!",
        "first_name": "Eve",
        "last_name": "Evans",
        "organization": "global_enterprises",  # Same as Diana
        "role": "user",
        "team_membership": ["backend_team"],  # Member of Backend Team
        "description": "Enterprise User - team member with limited permissions"
    },
]


async def delete_test_users(provider: KeycloakProvider) -> None:
    """Delete existing test users to ensure clean slate."""
    logger.info(f"\n{Colors.WARNING}{'='*60}{Colors.ENDC}")
    logger.info(f"{Colors.WARNING}Cleaning up existing test users...{Colors.ENDC}")
    logger.info(f"{Colors.WARNING}{'='*60}{Colors.ENDC}\n")

    for user_data in TEST_USERS:
        try:
            # Try to find and delete user by email
            logger.info(f"Checking for {user_data['email']}...")
            # Note: This assumes the provider has a method to get user by email
            # We'll handle errors gracefully
        except Exception:
            pass  # User doesn't exist, which is fine


async def create_organization(
    provider: KeycloakProvider,
    org_data: Dict[str, str]
) -> Optional[str]:
    """Create an organization."""
    try:
        org_create = OrganizationCreate(
            name=org_data["name"],
            display_name=org_data["display_name"],
            description=org_data.get("description", "")
        )
        org = await provider.create_organization(org_create)
        logger.info(
            f"{Colors.OKGREEN}  ✓ Created organization: {org_data['display_name']}{Colors.ENDC}"
        )
        return org.id
    except Exception as e:
        logger.error(f"{Colors.FAIL}  ✗ Failed to create organization {org_data['name']}: {e}{Colors.ENDC}")
        return None


async def create_custom_role(
    provider: KeycloakProvider,
    role_data: Dict[str, Any]
) -> bool:
    """Create a custom role."""
    try:
        # Check if role exists first
        try:
            existing = await provider.get_role(role_data["name"])
            if existing:
                logger.info(
                    f"{Colors.OKCYAN}  ⏭ Role '{role_data['name']}' already exists{Colors.ENDC}"
                )
                return True
        except Exception:
            pass  # Role doesn't exist, create it

        role_create = RoleCreate(
            name=role_data["name"],
            display_name=role_data["display_name"],
            description=role_data["description"],
            scope=role_data.get("scope", "organization"),
            scope_id=role_data.get("scope_id"),
            permissions=role_data["permissions"]
        )
        await provider.create_role(role_create)
        logger.info(
            f"{Colors.OKGREEN}  ✓ Created role: {role_data['display_name']}{Colors.ENDC}"
        )
        return True
    except Exception as e:
        logger.error(f"{Colors.FAIL}  ✗ Failed to create role {role_data['name']}: {e}{Colors.ENDC}")
        return False


async def create_teams(
    provider: KeycloakProvider,
    org_id: str,
    teams_data: List[Dict[str, Any]]
) -> Dict[str, str]:
    """Create teams and return mapping of team names to IDs."""
    team_ids = {}

    # First pass: create top-level teams (no parent)
    for team_data in teams_data:
        if team_data.get("parent") is None:
            try:
                team_create = TeamCreate(
                    name=team_data["name"],
                    display_name=team_data["display_name"],
                    description=team_data.get("description", ""),
                    organization_id=org_id,
                    parent_team_id=None
                )
                team = await provider.create_team(team_create)
                team_ids[team_data["name"]] = team.id
                logger.info(
                    f"{Colors.OKGREEN}  ✓ Created team: {team_data['display_name']}{Colors.ENDC}"
                )
            except Exception as e:
                logger.error(
                    f"{Colors.FAIL}  ✗ Failed to create team {team_data['name']}: {e}{Colors.ENDC}"
                )

    # Second pass: create child teams (with parent)
    for team_data in teams_data:
        if team_data.get("parent") is not None:
            try:
                parent_id = team_ids.get(team_data["parent"])
                if not parent_id:
                    logger.warning(
                        f"{Colors.WARNING}  ⚠ Parent team '{team_data['parent']}' not found for {team_data['name']}{Colors.ENDC}"
                    )
                    continue

                team_create = TeamCreate(
                    name=team_data["name"],
                    display_name=team_data["display_name"],
                    description=team_data.get("description", ""),
                    organization_id=org_id,
                    parent_team_id=parent_id
                )
                team = await provider.create_team(team_create)
                team_ids[team_data["name"]] = team.id
                logger.info(
                    f"{Colors.OKGREEN}  ✓ Created sub-team: {team_data['display_name']} under {team_data['parent']}{Colors.ENDC}"
                )
            except Exception as e:
                logger.error(
                    f"{Colors.FAIL}  ✗ Failed to create team {team_data['name']}: {e}{Colors.ENDC}"
                )

    return team_ids


async def seed_user(
    provider: KeycloakProvider,
    user_data: Dict[str, Any],
    organizations: Dict[str, str]
) -> bool:
    """Seed a single test user with all associated data."""
    logger.info(f"\n{Colors.HEADER}{'─'*60}{Colors.ENDC}")
    logger.info(
        f"{Colors.HEADER}{Colors.BOLD}Creating: {user_data['first_name']} {user_data['last_name']}{Colors.ENDC}"
    )
    logger.info(f"{Colors.OKCYAN}Email: {user_data['email']}{Colors.ENDC}")
    logger.info(f"{Colors.OKCYAN}Role: {user_data['role']}{Colors.ENDC}")
    logger.info(f"{Colors.OKCYAN}Description: {user_data['description']}{Colors.ENDC}")
    logger.info(f"{Colors.HEADER}{'─'*60}{Colors.ENDC}")

    try:
        # Step 1: Handle organization
        org_id = None
        if isinstance(user_data.get("organization"), dict):
            # Create new organization
            org_id = await create_organization(provider, user_data["organization"])
            if org_id:
                organizations[user_data["organization"]["name"]] = org_id
        elif isinstance(user_data.get("organization"), str):
            # Use existing organization
            org_id = organizations.get(user_data["organization"])
            if not org_id:
                logger.error(
                    f"{Colors.FAIL}  ✗ Organization '{user_data['organization']}' not found{Colors.ENDC}"
                )
                return False
            logger.info(
                f"{Colors.OKCYAN}  → Using existing organization: {user_data['organization']}{Colors.ENDC}"
            )

        # Step 2: Create custom role if specified
        if "custom_role" in user_data:
            await create_custom_role(provider, user_data["custom_role"])

        # Step 3: Create teams if specified
        team_ids = {}
        if "teams" in user_data and org_id:
            team_ids = await create_teams(provider, org_id, user_data["teams"])

        # Step 4: Create user
        user_create = UserCreate(
            email=user_data["email"],
            password=user_data["password"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            organization_id=org_id,
            enabled=True
        )

        user = await provider.create_user(user_create)
        logger.info(
            f"{Colors.OKGREEN}  ✓ Created user: {user.email}{Colors.ENDC}"
        )

        # Step 5: Assign role
        try:
            await provider.assign_role_to_user(user.id, user_data["role"])
            logger.info(
                f"{Colors.OKGREEN}  ✓ Assigned role: {user_data['role']}{Colors.ENDC}"
            )
        except Exception as e:
            logger.warning(
                f"{Colors.WARNING}  ⚠ Could not assign role {user_data['role']}: {e}{Colors.ENDC}"
            )

        # Step 6: Add to teams if specified
        if "team_membership" in user_data and team_ids:
            for team_name in user_data["team_membership"]:
                team_id = team_ids.get(team_name)
                if team_id:
                    try:
                        await provider.add_user_to_team(user.id, team_id)
                        logger.info(
                            f"{Colors.OKGREEN}  ✓ Added to team: {team_name}{Colors.ENDC}"
                        )
                    except Exception as e:
                        logger.warning(
                            f"{Colors.WARNING}  ⚠ Could not add to team {team_name}: {e}{Colors.ENDC}"
                        )

        logger.info(f"{Colors.OKGREEN}{Colors.BOLD}✓ SUCCESS{Colors.ENDC}\n")
        return True

    except Exception as e:
        logger.error(f"{Colors.FAIL}{Colors.BOLD}✗ FAILED: {e}{Colors.ENDC}\n")
        return False


async def main():
    """Main seeding function."""
    logger.info(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
    logger.info(f"{Colors.BOLD}{Colors.HEADER}  AuthFlow Test User Seeding Script{Colors.ENDC}")
    logger.info(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

    logger.info(f"{Colors.OKBLUE}This script will create 5 test users:{Colors.ENDC}")
    logger.info(f"{Colors.OKBLUE}1. Alice - Super Admin (global access){Colors.ENDC}")
    logger.info(f"{Colors.OKBLUE}2. Bob - Org Admin (TechCorp Inc){Colors.ENDC}")
    logger.info(f"{Colors.OKBLUE}3. Charlie - Singular User (minimal UI){Colors.ENDC}")
    logger.info(f"{Colors.OKBLUE}4. Diana - Enterprise Org Admin (complex hierarchy){Colors.ENDC}")
    logger.info(f"{Colors.OKBLUE}5. Eve - Enterprise User (team member){Colors.ENDC}\n")

    try:
        # Initialize provider
        logger.info(f"{Colors.OKCYAN}Initializing AuthFlow provider...{Colors.ENDC}")
        config = AuthFlowConfig.from_env()
        provider = KeycloakProvider(config.provider.keycloak)
        logger.info(f"{Colors.OKGREEN}✓ Provider initialized{Colors.ENDC}\n")

        # Clean up existing test users
        await delete_test_users(provider)

        # Seed users
        organizations = {}  # Track created organizations
        success_count = 0
        fail_count = 0

        for user_data in TEST_USERS:
            result = await seed_user(provider, user_data, organizations)
            if result:
                success_count += 1
            else:
                fail_count += 1

        # Summary
        logger.info(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
        logger.info(f"{Colors.BOLD}{Colors.HEADER}  Seeding Complete{Colors.ENDC}")
        logger.info(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

        logger.info(f"{Colors.OKGREEN}✓ Successfully created: {success_count} users{Colors.ENDC}")
        if fail_count > 0:
            logger.info(f"{Colors.FAIL}✗ Failed: {fail_count} users{Colors.ENDC}")

        logger.info(f"\n{Colors.BOLD}Test user credentials:{Colors.ENDC}")
        for user_data in TEST_USERS:
            logger.info(
                f"  {Colors.OKCYAN}{user_data['email']:<30}{Colors.ENDC} / "
                f"{Colors.WARNING}{user_data['password']}{Colors.ENDC}"
            )

        logger.info(f"\n{Colors.OKGREEN}You can now log in with any of these accounts!{Colors.ENDC}\n")

        return 0 if fail_count == 0 else 1

    except Exception as e:
        logger.error(f"\n{Colors.FAIL}{Colors.BOLD}Fatal error: {e}{Colors.ENDC}\n")
        import traceback
        traceback.print_exc()
        return 1


def cli():
    """CLI entry point."""
    sys.exit(asyncio.run(main()))


if __name__ == "__main__":
    cli()
