"""Multi-Factor Authentication API endpoints using Keycloak native MFA."""

import logging
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status

from authflow.core.provider import AuthProvider
from authflow.models.schemas import User
from authflow.api.dependencies import AuthFlowDependencies

logger = logging.getLogger(__name__)


def create_mfa_router(
    provider: AuthProvider,
    dependencies: AuthFlowDependencies,
) -> APIRouter:
    """Create MFA router using Keycloak's native OTP/MFA capabilities.

    Args:
        provider: Authentication provider (Keycloak)
        dependencies: AuthFlow dependencies

    Returns:
        Configured APIRouter
    """
    router = APIRouter(prefix="/mfa", tags=["mfa"])

    @router.get("/status")
    async def get_mfa_status(
        current_user: User = Depends(dependencies.get_current_user),
    ) -> Dict[str, Any]:
        """Get MFA status for current user from Keycloak.

        Args:
            current_user: Current authenticated user

        Returns:
            MFA status including configured credentials
        """
        try:
            logger.info(f"MFA status requested for user: {current_user.username}")

            # Get user credentials from Keycloak
            from authflow.providers.keycloak import KeycloakProvider

            if not isinstance(provider, KeycloakProvider):
                raise HTTPException(
                    status_code=status.HTTP_501_NOT_IMPLEMENTED,
                    detail="MFA only supported with Keycloak provider"
                )

            admin = provider.admin._get_admin()

            # Get user's configured credentials
            credentials = admin.get_credentials(current_user.id)

            # Check for OTP credential
            otp_configured = any(
                cred.get("type") == "otp"
                for cred in credentials
            )

            # Get required actions
            user_data = await provider.admin.get_user(current_user.id)
            required_actions = user_data.get("requiredActions", [])
            otp_required = "CONFIGURE_TOTP" in required_actions

            return {
                "enabled": otp_configured,
                "methods": ["totp"] if otp_configured else [],
                "otp_required": otp_required,
                "credentials": [
                    {
                        "id": cred.get("id"),
                        "type": cred.get("type"),
                        "user_label": cred.get("userLabel"),
                        "created_date": cred.get("createdDate"),
                    }
                    for cred in credentials
                ]
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting MFA status: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve MFA status: {str(e)}",
            )

    @router.post("/require-setup")
    async def require_mfa_setup(
        current_user: User = Depends(dependencies.get_current_user),
    ) -> Dict[str, str]:
        """Require MFA setup for the current user (adds CONFIGURE_TOTP required action).

        This will force the user to set up OTP on their next login.

        Args:
            current_user: Current authenticated user

        Returns:
            Success message
        """
        try:
            logger.info(f"Requiring MFA setup for user: {current_user.username}")

            from authflow.providers.keycloak import KeycloakProvider

            if not isinstance(provider, KeycloakProvider):
                raise HTTPException(
                    status_code=status.HTTP_501_NOT_IMPLEMENTED,
                    detail="MFA only supported with Keycloak provider"
                )

            admin = provider.admin._get_admin()

            # Add CONFIGURE_TOTP required action
            user_data = await provider.admin.get_user(current_user.id)
            required_actions = user_data.get("requiredActions", [])

            if "CONFIGURE_TOTP" not in required_actions:
                required_actions.append("CONFIGURE_TOTP")

                # Update user with required action
                admin.update_user(current_user.id, {
                    "requiredActions": required_actions
                })

                logger.info(f"Added CONFIGURE_TOTP required action for user: {current_user.username}")
                return {
                    "message": "MFA setup required. You will be prompted to configure your authenticator app on next login.",
                    "setup_url": f"{provider.config.url}/realms/{provider.config.realm}/account"
                }
            else:
                return {
                    "message": "MFA setup is already required",
                    "setup_url": f"{provider.config.url}/realms/{provider.config.realm}/account"
                }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error requiring MFA setup: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to require MFA setup: {str(e)}",
            )

    @router.delete("/credential/{credential_id}")
    async def remove_mfa_credential(
        credential_id: str,
        current_user: User = Depends(dependencies.get_current_user),
    ) -> Dict[str, str]:
        """Remove a specific MFA credential.

        Args:
            credential_id: Credential ID to remove
            current_user: Current authenticated user

        Returns:
            Success message
        """
        try:
            logger.info(f"Removing MFA credential {credential_id} for user: {current_user.username}")

            from authflow.providers.keycloak import KeycloakProvider

            if not isinstance(provider, KeycloakProvider):
                raise HTTPException(
                    status_code=status.HTTP_501_NOT_IMPLEMENTED,
                    detail="MFA only supported with Keycloak provider"
                )

            admin = provider.admin._get_admin()

            # Verify credential belongs to current user
            credentials = admin.get_credentials(current_user.id)
            credential_exists = any(cred.get("id") == credential_id for cred in credentials)

            if not credential_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Credential not found"
                )

            # Remove credential
            admin.delete_credential(current_user.id, credential_id)

            logger.info(f"Removed credential {credential_id} for user: {current_user.username}")
            return {"message": "MFA credential removed successfully"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error removing MFA credential: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to remove MFA credential: {str(e)}",
            )

    @router.get("/account-url")
    async def get_account_management_url(
        current_user: User = Depends(dependencies.get_current_user),
    ) -> Dict[str, str]:
        """Get Keycloak account management URL where users can configure MFA.

        Args:
            current_user: Current authenticated user

        Returns:
            Account management URL
        """
        try:
            from authflow.providers.keycloak import KeycloakProvider

            if not isinstance(provider, KeycloakProvider):
                raise HTTPException(
                    status_code=status.HTTP_501_NOT_IMPLEMENTED,
                    detail="MFA only supported with Keycloak provider"
                )

            account_url = f"{provider.config.url}/realms/{provider.config.realm}/account"

            return {
                "account_url": account_url,
                "message": "Visit this URL to configure your MFA settings in Keycloak Account Console"
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting account URL: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get account URL: {str(e)}",
            )

    return router
