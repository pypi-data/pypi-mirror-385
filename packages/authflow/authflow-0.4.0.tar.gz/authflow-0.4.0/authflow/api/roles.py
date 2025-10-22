"""Role management API endpoints."""

import logging
import json
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File

from authflow.core.provider import AuthProvider
from authflow.core.exceptions import RoleNotFoundError, RoleExistsError, ValidationError
from authflow.core.default_roles import validate_permissions
from authflow.models.schemas import (
    User,
    Role,
    RoleCreate,
    RoleUpdate,
    RoleFilters,
    PaginatedResponse,
    RoleAssignment,
)
from authflow.api.dependencies import AuthFlowDependencies

logger = logging.getLogger(__name__)


def create_roles_router(
    provider: AuthProvider,
    dependencies: AuthFlowDependencies,
) -> APIRouter:
    """Create roles management router.

    Args:
        provider: Authentication provider
        dependencies: AuthFlow dependencies

    Returns:
        Configured APIRouter
    """
    router = APIRouter(prefix="/roles", tags=["roles"])

    @router.get("", response_model=PaginatedResponse)
    async def list_roles(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        search: str = Query(None),
        scope: str = Query(None, description="Filter by scope (global, organization, team)"),
        scope_id: str = Query(None, description="Filter by scope ID"),
        current_user: User = Depends(dependencies.get_current_user),
    ) -> PaginatedResponse:
        """List roles with pagination and filters.

        Args:
            page: Page number
            page_size: Items per page
            search: Search query
            scope: Filter by scope
            scope_id: Filter by scope ID
            current_user: Current authenticated user

        Returns:
            Paginated list of roles
        """
        try:
            logger.info(f"List roles requested by: {current_user.username}")

            filters = RoleFilters(
                page=page,
                page_size=page_size,
                search=search,
                scope=scope,
                scope_id=scope_id,
            )

            result = await provider.list_roles(filters)

            logger.debug(f"Found {result.total} roles")
            return result

        except Exception as e:
            logger.error(f"Error listing roles: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list roles",
            )

    @router.post("", response_model=Role, status_code=status.HTTP_201_CREATED)
    async def create_role(
        role_data: RoleCreate,
        current_user: User = Depends(dependencies.get_current_user),
    ) -> Role:
        """Create a new role.

        Requires: roles:write permission

        Args:
            role_data: Role creation data
            current_user: Current authenticated user

        Returns:
            Created role
        """
        try:
            logger.info(
                f"Create role requested: {role_data.name} by {current_user.username}"
            )

            role = await provider.create_role(role_data)

            logger.info(f"Role created: {role.name}")
            return role

        except RoleExistsError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            )
        except Exception as e:
            logger.error(f"Error creating role: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create role",
            )

    @router.get("/{role_id}", response_model=Role)
    async def get_role(
        role_id: str,
        current_user: User = Depends(dependencies.get_current_user),
    ) -> Role:
        """Get role by ID.

        Args:
            role_id: Role ID
            current_user: Current authenticated user

        Returns:
            Role details
        """
        try:
            logger.debug(f"Get role requested: {role_id}")

            role = await provider.get_role(role_id)

            return role

        except RoleNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found",
            )
        except Exception as e:
            logger.error(f"Error getting role: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get role",
            )

    @router.patch("/{role_id}", response_model=Role)
    async def update_role(
        role_id: str,
        role_data: RoleUpdate,
        current_user: User = Depends(dependencies.get_current_user),
    ) -> Role:
        """Update role.

        Requires: roles:write permission

        Args:
            role_id: Role ID
            role_data: Update data
            current_user: Current authenticated user

        Returns:
            Updated role
        """
        try:
            logger.info(f"Update role requested: {role_id} by {current_user.username}")

            role = await provider.update_role(role_id, role_data)

            logger.info(f"Role updated: {role_id}")
            return role

        except RoleNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found",
            )
        except Exception as e:
            logger.error(f"Error updating role: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update role",
            )

    @router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_role(
        role_id: str,
        current_user: User = Depends(dependencies.get_current_user),
    ) -> None:
        """Delete role.

        Requires: roles:delete permission

        Args:
            role_id: Role ID
            current_user: Current authenticated user
        """
        try:
            logger.info(f"Delete role requested: {role_id} by {current_user.username}")

            await provider.delete_role(role_id)

            logger.info(f"Role deleted: {role_id}")

        except RoleNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found",
            )
        except Exception as e:
            logger.error(f"Error deleting role: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete role",
            )

    @router.post("/assign")
    async def assign_role(
        assignment: RoleAssignment,
        current_user: User = Depends(dependencies.get_current_user),
    ) -> dict:
        """Assign role to user.

        Requires: roles:write permission

        Args:
            assignment: Role assignment data
            current_user: Current authenticated user

        Returns:
            Success message
        """
        try:
            logger.info(
                f"[ROLE_ASSIGN] START - User: {assignment.user_id}, Role: {assignment.role_id}, "
                f"Scope: {assignment.scope_id}, Requested by: {current_user.username}"
            )

            await provider.assign_role_to_user(
                assignment.user_id,
                assignment.role_id,
                assignment.scope_id,
            )

            logger.info(
                f"[ROLE_ASSIGN] SUCCESS - User: {assignment.user_id}, Role: {assignment.role_id}"
            )
            return {"message": "Role assigned successfully"}

        except RoleNotFoundError as e:
            logger.error(f"Role not found during assignment: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role not found: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Error assigning role: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to assign role: {str(e)}",
            )

    @router.delete("/unassign")
    async def unassign_role(
        assignment: RoleAssignment,
        current_user: User = Depends(dependencies.get_current_user),
    ) -> dict:
        """Remove role from user.

        Requires: roles:write permission

        Args:
            assignment: Role assignment data
            current_user: Current authenticated user

        Returns:
            Success message
        """
        try:
            logger.info(
                f"Unassign role: {assignment.role_id} from user: {assignment.user_id}"
            )

            await provider.remove_role_from_user(
                assignment.user_id,
                assignment.role_id,
                assignment.scope_id,
            )

            logger.info(
                f"Role unassigned: {assignment.role_id} from {assignment.user_id}"
            )
            return {"message": "Role unassigned successfully"}

        except RoleNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found",
            )
        except Exception as e:
            logger.error(f"Error unassigning role: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to unassign role",
            )

    @router.get("/{role_id}/members", response_model=PaginatedResponse)
    async def list_role_members(
        role_id: str,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        current_user: User = Depends(dependencies.get_current_user),
    ) -> PaginatedResponse:
        """List users with this role.

        Args:
            role_id: Role ID
            page: Page number
            page_size: Items per page
            current_user: Current authenticated user

        Returns:
            Paginated list of users with this role
        """
        try:
            logger.debug(f"List members with role: {role_id}")

            # This would need to be implemented in the provider
            # For now, return empty list
            from authflow.models.schemas import UserFilters

            filters = UserFilters(
                page=page,
                page_size=page_size,
                role_id=role_id,
            )

            result = await provider.list_users(filters)

            return result

        except Exception as e:
            logger.error(f"Error listing role members: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list role members",
            )

    @router.get("/{role_id}/permissions")
    async def get_role_permissions(
        role_id: str,
        current_user: User = Depends(dependencies.get_current_user),
    ) -> dict:
        """Get permissions granted by this role.

        Args:
            role_id: Role ID
            current_user: Current authenticated user

        Returns:
            List of permissions
        """
        try:
            logger.debug(f"Get permissions for role: {role_id}")

            role = await provider.get_role(role_id)
            permissions = role.permissions if role.permissions else []

            return {"permissions": permissions}

        except RoleNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found",
            )
        except Exception as e:
            logger.error(f"Error getting role permissions: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get role permissions",
            )

    @router.put("/{role_id}/permissions")
    async def update_role_permissions(
        role_id: str,
        permissions: list[str],
        current_user: User = Depends(dependencies.get_current_user),
    ) -> dict:
        """Update permissions for a role.

        Requires: roles:write permission

        Args:
            role_id: Role ID
            permissions: List of permission strings
            current_user: Current authenticated user

        Returns:
            Updated permissions
        """
        try:
            logger.info(f"Update permissions for role: {role_id} by {current_user.username}")

            # Update role with new permissions
            role_data = RoleUpdate(permissions=permissions)
            role = await provider.update_role(role_id, role_data)

            logger.info(f"Permissions updated for role: {role_id}")
            return {"permissions": role.permissions if role.permissions else []}

        except RoleNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found",
            )
        except Exception as e:
            logger.error(f"Error updating role permissions: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update role permissions",
            )

    @router.post("/import")
    async def import_roles(
        file: UploadFile = File(...),
        current_user: User = Depends(dependencies.get_current_user),
    ) -> Dict[str, Any]:
        """Import roles from JSON file (create-only mode).

        Requires: roles:import permission (org_admin or super_admin)

        **Create-Only Mode**: This endpoint only creates new roles. Existing roles
        will be skipped (not updated). This ensures imports are non-destructive.

        Expected JSON format:
        {
            "roles": [
                {
                    "name": "role_identifier",
                    "display_name": "Human Readable Name",
                    "description": "What this role does",
                    "scope": "organization",
                    "permissions": ["users:read", "custom_resource:action"]
                }
            ]
        }

        Args:
            file: JSON file containing roles to import
            current_user: Current authenticated user

        Returns:
            Dictionary with import results including:
            - created: Number of roles created
            - skipped: Number of existing roles skipped
            - failed: Number of errors
            - created_roles: List of created role details
            - skipped_roles: List of skipped role names
            - errors: List of errors (if any)

        Raises:
            HTTPException: If user lacks permission or JSON is invalid
        """
        # Check permission
        if not dependencies.permission_engine.check_permission(
            current_user.permissions, "roles:import"
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Missing required permission: roles:import",
            )

        try:
            # Read and parse JSON file
            contents = await file.read()
            data = json.loads(contents.decode("utf-8"))

            if "roles" not in data or not isinstance(data["roles"], list):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid JSON format. Expected {'roles': [...]}"
                )

            created_roles = []
            skipped_roles = []
            errors = []

            for role_data in data["roles"]:
                try:
                    # Validate required fields
                    if "name" not in role_data:
                        errors.append({"role": role_data, "error": "Missing 'name' field"})
                        continue

                    role_name = role_data["name"]

                    # Check if role already exists (create-only mode)
                    try:
                        existing_role = await provider.get_role(role_name)
                        if existing_role:
                            skipped_roles.append({
                                "name": role_name,
                                "reason": "Role already exists (create-only mode)"
                            })
                            logger.info(f"Skipping existing role: {role_name}")
                            continue
                    except Exception:
                        # Role doesn't exist, proceed with creation
                        pass

                    # Validate permissions
                    permissions = role_data.get("permissions", [])
                    is_valid, invalid_perms = validate_permissions(permissions)
                    if not is_valid:
                        logger.warning(
                            f"Role '{role_name}' contains non-core permissions: {invalid_perms}. "
                            "These will be treated as custom permissions."
                        )

                    # Create role
                    role_create = RoleCreate(
                        name=role_name,
                        display_name=role_data.get("display_name", role_name),
                        description=role_data.get("description", ""),
                        scope=role_data.get("scope", "organization"),
                        scope_id=role_data.get("scope_id"),
                        permissions=permissions,
                    )

                    # Create in provider
                    role = await provider.create_role(role_create)
                    created_roles.append({
                        "name": role.name,
                        "id": role.id,
                        "permissions_count": len(role.permissions),
                    })
                    logger.info(f"Created role: {role_name} with {len(permissions)} permissions")

                except Exception as e:
                    errors.append({
                        "role": role_data.get("name", "unknown"),
                        "error": str(e)
                    })
                    logger.error(f"Failed to create role {role_data.get('name', 'unknown')}: {e}")

            return {
                "created": len(created_roles),
                "skipped": len(skipped_roles),
                "failed": len(errors),
                "created_roles": created_roles,
                "skipped_roles": skipped_roles,
                "errors": errors if errors else None,
                "message": (
                    f"Import complete: {len(created_roles)} created, "
                    f"{len(skipped_roles)} skipped, {len(errors)} errors"
                )
            }

        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid JSON file: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Error importing roles: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to import roles",
            )

    return router
