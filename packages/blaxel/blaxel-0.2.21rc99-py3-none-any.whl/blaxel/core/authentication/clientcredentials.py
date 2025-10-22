"""
This module provides the ClientCredentials class, which handles client credentials-based
authentication for Blaxel. It manages token refreshing and authentication flows using
client credentials and refresh tokens.
"""

import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Generator

import requests
from httpx import Request, Response

from .types import BlaxelAuth


@dataclass
class DeviceLoginFinalizeResponse:
    access_token: str
    expires_in: int
    refresh_token: str
    token_type: str


class ClientCredentials(BlaxelAuth):
    """
    ClientCredentials auth that authenticates requests using client credentials.
    """

    expires_at: datetime | None = None

    def get_headers(self):
        """
        Retrieves the authentication headers after ensuring tokens are valid.

        Returns:
            dict: A dictionary of headers with Bearer token and workspace.

        Raises:
            Exception: If token refresh fails.
        """
        err = self.get_token()
        if err:
            raise err
        return {
            "X-Blaxel-Authorization": f"Bearer {self.credentials.access_token}",
            "X-Blaxel-Workspace": self.workspace_name,
        }

    def _request_token(self, remaining_retries: int = 3) -> Exception | None:
        """
        Makes the token request with recursive retry logic.

        Args:
            remaining_retries (int): Number of retry attempts remaining.

        Returns:
            Exception | None: An exception if refreshing fails after all retries, otherwise None.
        """
        try:
            headers = {
                "Authorization": f"Basic {self.credentials.client_credentials}",
                "Content-Type": "application/json",
            }
            body = {"grant_type": "client_credentials"}
            response = requests.post(f"{self.base_url}/oauth/token", headers=headers, json=body)
            response.raise_for_status()
            creds = response.json()
            self.credentials.access_token = creds["access_token"]
            self.credentials.refresh_token = creds["refresh_token"]
            self.credentials.expires_in = creds["expires_in"]
            self.expires_at = datetime.now() + timedelta(seconds=self.credentials.expires_in)
            return None
        except Exception as e:
            if remaining_retries > 0:
                time.sleep(1)
                return self._request_token(remaining_retries - 1)
            return e

    def get_token(self) -> Exception | None:
        """
        Checks if the access token needs to be refreshed and performs the refresh if necessary.
        Uses recursive retry logic for up to 3 attempts.

        Returns:
            Exception | None: An exception if refreshing fails after all retries, otherwise None.
        """
        if self.need_token():
            return self._request_token()
        return None

    def need_token(self):
        if not self.expires_at:
            return True
        return datetime.now() > self.expires_at - timedelta(minutes=10)

    def auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        """
        Processes the authentication flow by ensuring tokens are valid and adding necessary headers.

        Parameters:
            request (Request): The HTTP request to authenticate.

        Yields:
            Request: The authenticated request.

        Raises:
            Exception: If token refresh fails.
        """
        self.get_token()
        request.headers["X-Blaxel-Authorization"] = f"Bearer {self.credentials.access_token}"
        request.headers["X-Blaxel-Workspace"] = self.workspace_name
        yield request

    @property
    def token(self):
        if not self.credentials.access_token:
            self.get_token()
        return self.credentials.access_token
