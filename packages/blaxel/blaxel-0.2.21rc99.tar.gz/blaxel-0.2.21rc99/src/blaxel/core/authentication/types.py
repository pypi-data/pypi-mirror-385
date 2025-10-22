"""Contains types for authentication credentials"""

from typing import Dict

from httpx import Auth
from pydantic import BaseModel, Field


class CredentialsType(BaseModel):
    """Represents authentication credentials for the API"""

    api_key: str | None = Field(default=None, description="The API key")
    client_credentials: str | None = Field(default=None, description="The client credentials")
    refresh_token: str | None = Field(default=None, description="The refresh token")
    access_token: str | None = Field(default=None, description="The access token")
    device_code: str | None = Field(default=None, description="The device code")
    expires_in: int | None = Field(default=None, description="The expiration time")
    workspace: str | None = Field(default=None, description="The workspace")

class BlaxelAuth(Auth):
    def __init__(self, credentials: CredentialsType, workspace_name: str, base_url: str):
        """
        Initializes the BlaxelAuth with the given credentials, workspace name, and base URL.

        Parameters:
            credentials: Credentials containing the Bearer token and refresh token.
            workspace_name (str): The name of the workspace.
            base_url (str): The base URL for authentication.
        """
        self.credentials = credentials
        self.workspace_name = workspace_name
        self.base_url = base_url

    def get_headers(self) -> Dict[str, str]:
        return {}

    @property
    def token(self):
        raise NotImplementedError("Subclasses must implement the token property")
