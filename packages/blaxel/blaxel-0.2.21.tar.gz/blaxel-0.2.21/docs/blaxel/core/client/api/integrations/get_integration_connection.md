Module blaxel.core.client.api.integrations.get_integration_connection
=====================================================================

Functions
---------

`asyncio(connection_name: str, *, client: blaxel.core.client.client.Client) ‑> blaxel.core.client.models.integration_connection.IntegrationConnection | None`
:   Get integration
    
     Returns an integration connection by integration name and connection name.
    
    Args:
        connection_name (str):
    
    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.
    
    Returns:
        IntegrationConnection

`asyncio_detailed(connection_name: str, *, client: blaxel.core.client.client.Client) ‑> blaxel.core.client.types.Response[blaxel.core.client.models.integration_connection.IntegrationConnection]`
:   Get integration
    
     Returns an integration connection by integration name and connection name.
    
    Args:
        connection_name (str):
    
    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.
    
    Returns:
        Response[IntegrationConnection]

`sync(connection_name: str, *, client: blaxel.core.client.client.Client) ‑> blaxel.core.client.models.integration_connection.IntegrationConnection | None`
:   Get integration
    
     Returns an integration connection by integration name and connection name.
    
    Args:
        connection_name (str):
    
    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.
    
    Returns:
        IntegrationConnection

`sync_detailed(connection_name: str, *, client: blaxel.core.client.client.Client) ‑> blaxel.core.client.types.Response[blaxel.core.client.models.integration_connection.IntegrationConnection]`
:   Get integration
    
     Returns an integration connection by integration name and connection name.
    
    Args:
        connection_name (str):
    
    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.
    
    Returns:
        Response[IntegrationConnection]