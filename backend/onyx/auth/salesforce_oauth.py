"""Salesforce OAuth2 client implementation."""
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from httpx_oauth.oauth2 import BaseOAuth2


class SalesforceOAuth2(BaseOAuth2[Dict[str, Any]]):
    """OAuth2 client for Salesforce authentication."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        instance_url: str = "https://login.salesforce.com",
        scopes: Optional[List[str]] = None,
        name: str = "salesforce",
    ):
        """
        Initialize Salesforce OAuth2 client.

        Args:
            client_id: Salesforce Connected App Consumer Key
            client_secret: Salesforce Connected App Consumer Secret
            instance_url: Salesforce instance URL (login.salesforce.com or test.salesforce.com)
            scopes: OAuth scopes to request. Defaults to ["openid", "email", "profile", "refresh_token"]
            name: Name of the OAuth provider
        """
        if scopes is None:
            scopes = [
                "openid",
                "email",
                "profile",
                "refresh_token",  # Required for offline access
            ]

        # Salesforce OAuth endpoints
        authorize_endpoint = f"{instance_url}/services/oauth2/authorize"
        access_token_endpoint = f"{instance_url}/services/oauth2/token"
        # Salesforce uses the UserInfo endpoint for profile information
        profile_endpoint = f"{instance_url}/services/oauth2/userinfo"

        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            authorize_endpoint=authorize_endpoint,
            access_token_endpoint=access_token_endpoint,
            refresh_token_endpoint=access_token_endpoint,
            revoke_token_endpoint=f"{instance_url}/services/oauth2/revoke",
            name=name,
            base_scopes=scopes,
        )

        self.profile_endpoint = profile_endpoint

    async def get_id_email(self, token: str) -> Tuple[str, str]:
        """
        Get user ID and email from Salesforce using the access token.

        Args:
            token: OAuth access token

        Returns:
            Tuple of (user_id, email)
        """
        async with self.get_httpx_client() as client:
            response = await client.get(
                self.profile_endpoint,
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()

            profile_data = response.json()

            # Salesforce returns user_id and email in the userinfo response
            # The 'sub' field contains the unique user ID
            # Format is typically: https://login.salesforce.com/id/{org_id}/{user_id}
            user_id = profile_data.get("user_id") or profile_data.get("sub", "")
            email = profile_data.get("email", "")

            if not user_id or not email:
                raise ValueError(
                    f"Unable to get user ID or email from Salesforce profile: {profile_data}"
                )

            return user_id, email
