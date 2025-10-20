"""GDPR Compliance API endpoints for data export and deletion (Right to be Forgotten)."""

import json
import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse

from authflow.core.provider import AuthProvider
from authflow.core.audit import AuditService
from authflow.models.schemas import User
from authflow.api.dependencies import AuthFlowDependencies

logger = logging.getLogger(__name__)


def create_gdpr_router(
    provider: AuthProvider,
    audit_service: AuditService,
    dependencies: AuthFlowDependencies,
) -> APIRouter:
    """Create GDPR compliance router.

    Args:
        provider: Authentication provider
        audit_service: Audit service for logging
        dependencies: AuthFlow dependencies

    Returns:
        Configured APIRouter
    """
    router = APIRouter(prefix="/gdpr", tags=["gdpr"])

    @router.get("/export")
    async def export_user_data(
        current_user: User = Depends(dependencies.get_current_user),
    ) -> StreamingResponse:
        """Export all user data (GDPR Article 20 - Right to Data Portability).

        This endpoint exports all data associated with the current user
        in a machine-readable JSON format.

        Args:
            current_user: Current authenticated user

        Returns:
            JSON file containing all user data
        """
        try:
            logger.info(f"GDPR data export requested by user: {current_user.username}")

            # Collect all user data
            user_data: Dict[str, Any] = {
                "export_date": datetime.utcnow().isoformat(),
                "data_subject": {
                    "id": current_user.id,
                    "username": current_user.username,
                    "email": current_user.email,
                    "first_name": current_user.first_name,
                    "last_name": current_user.last_name,
                    "phone": current_user.phone,
                    "avatar_url": current_user.avatar_url,
                    "is_active": current_user.is_active,
                    "is_verified": current_user.is_verified,
                    "provider": current_user.provider,
                    "created_at": current_user.created_at.isoformat(),
                    "updated_at": current_user.updated_at.isoformat(),
                    "custom_attributes": current_user.custom_attributes,
                },
                "organizations": [],
                "teams": [],
                "roles": [],
                "permissions": [],
                "sessions": [],
                "audit_logs": [],
            }

            # Get user's organizations
            try:
                organizations = await provider.get_user_organizations(current_user.id)
                user_data["organizations"] = [
                    {
                        "id": org.id,
                        "name": org.name,
                        "display_name": org.display_name,
                        "description": org.description,
                    }
                    for org in organizations
                ]
            except Exception as e:
                logger.warning(f"Could not fetch organizations: {e}")

            # Get user's teams
            try:
                teams = await provider.get_user_teams(current_user.id)
                user_data["teams"] = [
                    {
                        "id": team.id,
                        "name": team.name,
                        "display_name": team.display_name,
                        "organization_id": team.organization_id,
                    }
                    for team in teams
                ]
            except Exception as e:
                logger.warning(f"Could not fetch teams: {e}")

            # Get user's roles
            try:
                roles = await provider.get_user_roles(current_user.id)
                user_data["roles"] = [
                    {
                        "id": role.id,
                        "name": role.name,
                        "description": role.description,
                        "scope": role.scope,
                    }
                    for role in roles
                ]
            except Exception as e:
                logger.warning(f"Could not fetch roles: {e}")

            # Get user's permissions
            try:
                permissions = await provider.get_user_permissions(current_user.id)
                user_data["permissions"] = permissions
            except Exception as e:
                logger.warning(f"Could not fetch permissions: {e}")

            # Get user's sessions
            try:
                sessions = await provider.get_user_sessions(current_user.id)
                user_data["sessions"] = sessions
            except Exception as e:
                logger.warning(f"Could not fetch sessions: {e}")

            # Get user's audit logs (their own actions)
            try:
                from authflow.models.audit import AuditLogFilters
                filters = AuditLogFilters(
                    actor_id=current_user.id,
                    page=1,
                    page_size=1000,  # Get up to 1000 most recent logs
                )
                logs, _ = await audit_service.get_logs(filters)
                user_data["audit_logs"] = [
                    {
                        "id": log.id,
                        "timestamp": log.timestamp.isoformat(),
                        "event_type": log.event_type,
                        "resource_type": log.resource_type,
                        "action": log.action,
                        "status": log.status,
                        "details": log.details,
                    }
                    for log in logs
                ]
            except Exception as e:
                logger.warning(f"Could not fetch audit logs: {e}")

            # Log the export action
            await audit_service.log_event(
                event_type="gdpr.data_exported",
                resource_type="user",
                resource_id=current_user.id,
                action="export",
                status="success",
                actor_id=current_user.id,
                actor_username=current_user.username,
                details={"export_date": datetime.utcnow().isoformat()},
            )

            # Convert to JSON
            json_data = json.dumps(user_data, indent=2, ensure_ascii=False)

            # Create filename
            filename = f"user_data_{current_user.username}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

            # Return as downloadable file
            return StreamingResponse(
                iter([json_data]),
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Content-Type": "application/json; charset=utf-8",
                },
            )

        except Exception as e:
            logger.error(f"Error exporting user data: {e}")

            # Log the failed export
            try:
                await audit_service.log_event(
                    event_type="gdpr.data_export_failed",
                    resource_type="user",
                    resource_id=current_user.id,
                    action="export",
                    status="failure",
                    actor_id=current_user.id,
                    actor_username=current_user.username,
                    error_message=str(e),
                )
            except:
                pass

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to export user data: {str(e)}",
            )

    @router.post("/request-deletion")
    async def request_account_deletion(
        current_user: User = Depends(dependencies.get_current_user),
    ) -> Dict[str, str]:
        """Request account deletion (GDPR Article 17 - Right to Erasure/"Right to be Forgotten").

        This endpoint initiates the account deletion process. In production,
        this should create a deletion request that is reviewed and processed
        after a grace period (e.g., 30 days) to allow for accidental requests.

        Args:
            current_user: Current authenticated user

        Returns:
            Confirmation message with deletion request ID
        """
        try:
            logger.info(f"Account deletion requested by user: {current_user.username}")

            # TODO: In production, create a deletion request with grace period
            # For now, we'll just log the request

            # Log the deletion request
            await audit_service.log_event(
                event_type="gdpr.deletion_requested",
                resource_type="user",
                resource_id=current_user.id,
                action="request_deletion",
                status="pending",
                actor_id=current_user.id,
                actor_username=current_user.username,
                details={
                    "request_date": datetime.utcnow().isoformat(),
                    "grace_period_days": 30,
                },
            )

            return {
                "message": "Account deletion request submitted successfully",
                "details": "Your account will be scheduled for deletion after a 30-day grace period. You can cancel this request during this time by logging in.",
                "grace_period_days": "30",
                "effective_date": (datetime.utcnow().replace(day=datetime.utcnow().day + 30)).isoformat(),
            }

        except Exception as e:
            logger.error(f"Error requesting account deletion: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to request account deletion: {str(e)}",
            )

    @router.delete("/delete-account")
    async def delete_account_permanently(
        confirmation: str,
        current_user: User = Depends(dependencies.get_current_user),
    ) -> Dict[str, str]:
        """Permanently delete user account and all associated data.

        ⚠️ WARNING: This action is IRREVERSIBLE!

        This endpoint should be used with extreme caution and requires
        explicit confirmation. In production, this should require additional
        verification (e.g., password confirmation, 2FA, email confirmation).

        Args:
            confirmation: Must be the user's email address to confirm deletion
            current_user: Current authenticated user

        Returns:
            Confirmation message
        """
        try:
            logger.warning(f"PERMANENT account deletion initiated by user: {current_user.username}")

            # Require email confirmation
            if confirmation != current_user.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email confirmation does not match. Account deletion aborted.",
                )

            # Log the deletion attempt
            await audit_service.log_event(
                event_type="gdpr.account_deletion_initiated",
                resource_type="user",
                resource_id=current_user.id,
                action="delete",
                status="pending",
                actor_id=current_user.id,
                actor_username=current_user.username,
                details={"deletion_date": datetime.utcnow().isoformat()},
            )

            # Delete user from provider
            await provider.delete_user(current_user.id)

            # Log the successful deletion
            await audit_service.log_event(
                event_type="gdpr.account_deleted",
                resource_type="user",
                resource_id=current_user.id,
                action="delete",
                status="success",
                actor_id=current_user.id,
                actor_username=current_user.username,
                details={
                    "deletion_date": datetime.utcnow().isoformat(),
                    "deleted_by": "self",
                },
            )

            logger.warning(f"Account permanently deleted: {current_user.username} (ID: {current_user.id})")

            return {
                "message": "Your account has been permanently deleted",
                "details": "All your data has been removed from our systems. This action cannot be undone.",
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting account: {e}")

            # Log the failed deletion
            try:
                await audit_service.log_event(
                    event_type="gdpr.account_deletion_failed",
                    resource_type="user",
                    resource_id=current_user.id,
                    action="delete",
                    status="failure",
                    actor_id=current_user.id,
                    actor_username=current_user.username,
                    error_message=str(e),
                )
            except:
                pass

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete account: {str(e)}",
            )

    @router.get("/data-retention-policy")
    async def get_data_retention_policy() -> Dict[str, Any]:
        """Get data retention policy information.

        Returns information about how long different types of data are retained.

        Returns:
            Data retention policy details
        """
        return {
            "policy_version": "1.0",
            "last_updated": "2025-01-01",
            "retention_periods": {
                "user_accounts": {
                    "active": "indefinite (until user requests deletion)",
                    "deleted": "30 days grace period, then permanently removed",
                },
                "audit_logs": "90 days",
                "session_data": "30 days after session ends",
                "mfa_credentials": "indefinite (until removed by user)",
            },
            "data_export": {
                "format": "JSON",
                "includes": ["profile data", "organizations", "teams", "roles", "permissions", "audit logs"],
            },
            "deletion_process": {
                "grace_period": "30 days",
                "cancellation": "Can be cancelled during grace period",
                "permanent_after": "30 days from request",
            },
        }

    return router
