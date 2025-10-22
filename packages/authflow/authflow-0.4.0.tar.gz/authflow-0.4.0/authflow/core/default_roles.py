"""Default roles and permissions for AuthFlow.

This module defines the core roles that come with AuthFlow.
Applications can extend these roles by importing custom roles via JSON.
"""

from typing import Dict, List, Any

# Core permissions required for AuthFlow to function
CORE_PERMISSIONS = {
    # Admin permissions
    "admin:read": "Access admin panel",

    # User permissions
    "users:read": "View users",
    "users:write": "Create and edit users",
    "users:delete": "Delete users",

    # Organization permissions
    "organizations:read": "View organizations",
    "organizations:write": "Create and edit organizations",
    "organizations:delete": "Delete organizations",
    "organizations:manage": "Switch between organizations (super admin only)",

    # Team permissions
    "teams:read": "View teams",
    "teams:write": "Create and edit teams",
    "teams:delete": "Delete teams",
    "teams:manage_members": "Add and remove team members",

    # Role permissions
    "roles:read": "View roles",
    "roles:write": "Create and edit roles",
    "roles:delete": "Delete roles",
    "roles:assign": "Assign roles to users",
    "roles:import": "Import roles from JSON file",

    # Audit permissions
    "audit:read": "View audit logs",

    # MFA permissions
    "mfa:manage": "Manage MFA settings",

    # GDPR permissions
    "gdpr:export": "Export user data",
    "gdpr:delete": "Delete user data",
}


# Default roles provided by AuthFlow
DEFAULT_ROLES: Dict[str, Dict[str, Any]] = {
    "super_admin": {
        "display_name": "Super Administrator",
        "description": "Full system access across all organizations. Can switch between organizations and manage the entire system.",
        "scope": "global",
        "permissions": ["*"],  # All permissions
    },

    "org_admin": {
        "display_name": "Organization Administrator",
        "description": "Full access within their organization. Can manage users, teams, roles, and import custom roles.",
        "scope": "organization",
        "permissions": [
            # User management
            "users:read",
            "users:write",
            "users:delete",

            # Team management
            "teams:read",
            "teams:write",
            "teams:delete",
            "teams:manage_members",

            # Role management
            "roles:read",
            "roles:write",
            "roles:delete",
            "roles:assign",
            "roles:import",  # Can import custom roles

            # Organization (read only their own)
            "organizations:read",

            # Admin panel access
            "admin:read",

            # Audit
            "audit:read",
        ],
    },

    "user": {
        "display_name": "User",
        "description": "Standard user with basic access within their organization.",
        "scope": "organization",
        "permissions": [
            "users:read",  # Can view other users in their org
        ],
    },
}


def get_role_permissions(role_name: str) -> List[str]:
    """Get permissions for a given role.

    Args:
        role_name: Name of the role

    Returns:
        List of permission strings

    Raises:
        KeyError: If role doesn't exist
    """
    if role_name not in DEFAULT_ROLES:
        raise KeyError(f"Unknown role: {role_name}")

    return DEFAULT_ROLES[role_name]["permissions"]


def get_all_permissions() -> Dict[str, str]:
    """Get all core permissions with their descriptions.

    Returns:
        Dictionary mapping permission strings to descriptions
    """
    return CORE_PERMISSIONS.copy()


def validate_permissions(permissions: List[str]) -> tuple[bool, List[str]]:
    """Validate a list of permissions against core permissions.

    Args:
        permissions: List of permission strings to validate

    Returns:
        Tuple of (is_valid, invalid_permissions)
        - is_valid: True if all permissions are valid or use wildcards
        - invalid_permissions: List of permissions that are not recognized
    """
    invalid = []

    for perm in permissions:
        # Wildcard permissions are always valid
        if perm == "*" or perm.endswith(":*") or perm.startswith("*:"):
            continue

        # Check against core permissions
        if perm not in CORE_PERMISSIONS:
            # Check if it's a custom permission (contains :)
            if ":" not in perm:
                invalid.append(perm)

    return (len(invalid) == 0, invalid)
