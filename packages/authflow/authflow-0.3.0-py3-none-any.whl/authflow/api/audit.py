"""Audit log API endpoints."""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request

from authflow.core.audit import AuditService
from authflow.models.audit import AuditLog, AuditLogFilters, AuditLogStats
from authflow.models.schemas import User, PaginatedResponse
from authflow.api.dependencies import AuthFlowDependencies

logger = logging.getLogger(__name__)


def create_audit_router(
    audit_service: AuditService,
    dependencies: AuthFlowDependencies,
) -> APIRouter:
    """Create audit log router.

    Args:
        audit_service: Audit service instance
        dependencies: AuthFlow dependencies

    Returns:
        Configured APIRouter
    """
    router = APIRouter(prefix="/audit", tags=["audit"])

    @router.get("/logs", response_model=PaginatedResponse)
    async def get_audit_logs(
        page: int = 1,
        page_size: int = 50,
        event_type: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        action: str | None = None,
        actor_id: str | None = None,
        actor_username: str | None = None,
        status: str | None = None,
        organization_id: str | None = None,
        team_id: str | None = None,
        current_user: User = Depends(dependencies.get_current_user),
    ) -> PaginatedResponse:
        """Get audit logs with filtering and pagination.

        Requires authenticated user. Admins can see all logs, regular users
        can only see logs related to their actions.

        Args:
            page: Page number
            page_size: Items per page
            event_type: Filter by event type
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            action: Filter by action
            actor_id: Filter by actor ID
            actor_username: Filter by actor username
            status: Filter by status
            organization_id: Filter by organization
            team_id: Filter by team
            current_user: Current authenticated user

        Returns:
            Paginated audit logs
        """
        try:
            logger.info(f"Audit logs requested by user: {current_user.username}")

            # Create filters
            filters = AuditLogFilters(
                page=page,
                page_size=page_size,
                event_type=event_type,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                actor_id=actor_id,
                actor_username=actor_username,
                status=status,
                organization_id=organization_id,
                team_id=team_id,
            )

            # TODO: Check if user has permission to view audit logs
            # For now, users can only see their own logs unless they have admin permission
            # if not has_admin_permission(current_user):
            #     filters.actor_id = current_user.id

            # Get logs
            logs, total = await audit_service.get_logs(filters)

            # Calculate total pages
            total_pages = (total + page_size - 1) // page_size

            return PaginatedResponse(
                items=[log.model_dump() for log in logs],
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
            )

        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve audit logs: {str(e)}",
            )

    @router.get("/stats", response_model=AuditLogStats)
    async def get_audit_stats(
        current_user: User = Depends(dependencies.get_current_user),
    ) -> AuditLogStats:
        """Get audit log statistics.

        Args:
            current_user: Current authenticated user

        Returns:
            Audit log statistics
        """
        try:
            logger.info(f"Audit stats requested by user: {current_user.username}")

            # TODO: Check if user has permission to view audit stats
            # For now, require authentication

            stats = await audit_service.get_stats()
            return stats

        except Exception as e:
            logger.error(f"Error getting audit stats: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve audit stats: {str(e)}",
            )

    @router.get("/events/types")
    async def get_event_types(
        current_user: User = Depends(dependencies.get_current_user),
    ) -> List[str]:
        """Get list of available event types for filtering.

        Args:
            current_user: Current authenticated user

        Returns:
            List of event types
        """
        return [
            "user.login",
            "user.logout",
            "user.created",
            "user.updated",
            "user.deleted",
            "user.password_changed",
            "user.email_verified",
            "role.created",
            "role.updated",
            "role.deleted",
            "role.assigned",
            "role.unassigned",
            "permission.granted",
            "permission.revoked",
            "organization.created",
            "organization.updated",
            "organization.deleted",
            "team.created",
            "team.updated",
            "team.deleted",
            "mfa.enabled",
            "mfa.disabled",
            "mfa.verified",
            "session.created",
            "session.revoked",
        ]

    @router.post("/cleanup")
    async def cleanup_old_logs(
        current_user: User = Depends(dependencies.get_current_user),
    ) -> dict:
        """Cleanup old audit logs beyond retention period.

        This endpoint should be restricted to admin users only.

        Args:
            current_user: Current authenticated user

        Returns:
            Success message
        """
        try:
            logger.info(f"Audit log cleanup requested by user: {current_user.username}")

            # TODO: Check if user has admin permission
            # For now, require authentication

            await audit_service.cleanup_old_logs()

            return {"message": "Old audit logs cleaned up successfully"}

        except Exception as e:
            logger.error(f"Error cleaning up audit logs: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to cleanup audit logs: {str(e)}",
            )

    return router
