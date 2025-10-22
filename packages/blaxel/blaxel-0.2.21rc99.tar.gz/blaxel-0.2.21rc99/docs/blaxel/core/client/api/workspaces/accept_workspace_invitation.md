Module blaxel.core.client.api.workspaces.accept_workspace_invitation
====================================================================

Functions
---------

`asyncio(workspace_name: str, *, client: blaxel.core.client.client.Client) ‑> Any | blaxel.core.client.models.pending_invitation_accept.PendingInvitationAccept | None`
:   Accept invitation to workspace
    
     Accepts an invitation to a workspace.
    
    Args:
        workspace_name (str):
    
    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.
    
    Returns:
        Union[Any, PendingInvitationAccept]

`asyncio_detailed(workspace_name: str, *, client: blaxel.core.client.client.Client) ‑> blaxel.core.client.types.Response[Any | blaxel.core.client.models.pending_invitation_accept.PendingInvitationAccept]`
:   Accept invitation to workspace
    
     Accepts an invitation to a workspace.
    
    Args:
        workspace_name (str):
    
    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.
    
    Returns:
        Response[Union[Any, PendingInvitationAccept]]

`sync(workspace_name: str, *, client: blaxel.core.client.client.Client) ‑> Any | blaxel.core.client.models.pending_invitation_accept.PendingInvitationAccept | None`
:   Accept invitation to workspace
    
     Accepts an invitation to a workspace.
    
    Args:
        workspace_name (str):
    
    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.
    
    Returns:
        Union[Any, PendingInvitationAccept]

`sync_detailed(workspace_name: str, *, client: blaxel.core.client.client.Client) ‑> blaxel.core.client.types.Response[Any | blaxel.core.client.models.pending_invitation_accept.PendingInvitationAccept]`
:   Accept invitation to workspace
    
     Accepts an invitation to a workspace.
    
    Args:
        workspace_name (str):
    
    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.
    
    Returns:
        Response[Union[Any, PendingInvitationAccept]]