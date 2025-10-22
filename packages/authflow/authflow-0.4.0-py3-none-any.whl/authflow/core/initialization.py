"""Auto-initialization module for AuthFlow.

This module handles automatic initialization of default roles and system setup
when the AuthFlow backend starts up.
"""

import logging
from typing import Dict, List, Any

from authflow.core.provider import AuthProvider
from authflow.core.default_roles import DEFAULT_ROLES
from authflow.models.schemas import RoleCreate

logger = logging.getLogger(__name__)


async def initialize_default_roles(provider: AuthProvider) -> Dict[str, Any]:
    """Initialize default roles in Keycloak on startup.

    This function is idempotent - it's safe to run multiple times.
    Existing roles will be skipped, only missing roles will be created.

    Args:
        provider: The auth provider instance (KeycloakProvider)

    Returns:
        Dictionary with initialization results:
        {
            "created": List[str],   # Roles that were created
            "skipped": List[str],   # Roles that already existed
            "errors": List[Dict]    # Errors that occurred
        }
    """
    results = {
        "created": [],
        "skipped": [],
        "errors": []
    }

    logger.info("Starting default roles initialization...")

    for role_name, role_data in DEFAULT_ROLES.items():
        try:
            # Check if role already exists
            try:
                existing_role = await provider.get_role(role_name)
                if existing_role:
                    results["skipped"].append(role_name)
                    logger.info(f"Role '{role_name}' already exists, skipping...")
                    continue
            except Exception:
                # Role doesn't exist, proceed with creation
                pass

            # Create the role
            role_create = RoleCreate(
                name=role_name,
                display_name=role_data["display_name"],
                description=role_data.get("description", ""),
                scope=role_data.get("scope", "global"),
                scope_id=None,
                permissions=role_data["permissions"]
            )

            await provider.create_role(role_create)
            results["created"].append(role_name)
            logger.info(
                f"✓ Created role '{role_name}' with {len(role_data['permissions'])} "
                f"permission(s)"
            )

        except Exception as e:
            error_msg = f"Failed to create role '{role_name}': {str(e)}"
            logger.error(error_msg)
            results["errors"].append({
                "role": role_name,
                "error": str(e)
            })

    # Log summary
    logger.info(
        f"Default roles initialization complete: "
        f"{len(results['created'])} created, "
        f"{len(results['skipped'])} skipped, "
        f"{len(results['errors'])} errors"
    )

    return results


async def initialize_system(provider: AuthProvider) -> Dict[str, Any]:
    """Initialize the entire AuthFlow system.

    This is the main initialization function that runs on startup.
    Currently it only initializes roles, but can be extended to
    initialize other system components.

    Args:
        provider: The auth provider instance

    Returns:
        Dictionary with all initialization results
    """
    logger.info("=" * 60)
    logger.info("AuthFlow System Initialization Starting...")
    logger.info("=" * 60)

    results = {
        "roles": {},
        "success": True,
        "message": ""
    }

    try:
        # Initialize default roles
        role_results = await initialize_default_roles(provider)
        results["roles"] = role_results

        # Check if there were any errors
        if role_results["errors"]:
            results["success"] = False
            results["message"] = (
                f"Initialization completed with {len(role_results['errors'])} error(s). "
                f"See logs for details."
            )
        else:
            results["message"] = (
                f"Initialization successful. "
                f"Created {len(role_results['created'])} role(s), "
                f"skipped {len(role_results['skipped'])} existing role(s)."
            )

        logger.info("=" * 60)
        logger.info(f"Initialization Result: {results['message']}")
        logger.info("=" * 60)

    except Exception as e:
        error_msg = f"System initialization failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        results["success"] = False
        results["message"] = error_msg

    return results
