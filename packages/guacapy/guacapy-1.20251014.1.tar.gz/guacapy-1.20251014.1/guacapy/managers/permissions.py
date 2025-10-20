"""
Permissions management module for the Guacamole REST API.

This module provides the `PermissionsManager` class to interact with permissions-related endpoints
of the Apache Guacamole REST API, enabling operations such as assigning and revoking system permissions
for users.

The API endpoints are based on the unofficial documentation for Guacamole version 1.1.0:
https://github.com/ridvanaltun/guacamole-rest-api-documentation

Parameters
----------
client : Guacamole
    The Guacamole client instance with authentication details.
datasource : str, optional
    The data source identifier (e.g., 'mysql', 'postgresql'). Defaults to the client's primary data source.

Examples
--------
Create a client and assign a system permission:
>>> from guacapy import Guacamole
>>> client = Guacamole(
...     hostname="guacamole.example.com",
...     username="admin",
...     password="secret",
...     datasource="mysql"
... )
>>> permissions_manager = client.permissions
>>> response = permissions_manager.assign_system_permission(username="daxm", permission="CREATE_USER")
>>> print(response.status_code)
204
"""

import logging
import requests
from typing import Any, Optional
from .base import BaseManager
from ..utilities import requester

# Get the logger for this module
logger = logging.getLogger(__name__)


class PermissionsManager(BaseManager):
    def __init__(
        self,
        client: Any,
        datasource: Optional[str] = None,
    ):
        """
        Initialize the PermissionsManager for interacting with Guacamole permissions endpoints.

        Parameters
        ----------
        client : Any
            The Guacamole client instance with base_url and authentication details.
        datasource : Optional[str], optional
            The data source identifier (e.g., 'mysql', 'postgresql'). Defaults to
            client.primary_datasource if None.

        Attributes
        ----------
        client : Any
            The provided Guacamole client instance.
        datasource : str
            The data source identifier for API requests.

        Raises
        ------
        requests.HTTPError
            If the API authentication fails or the datasource is invalid.
        """
        super().__init__(client, datasource)
        self.url = (
            f"{self.client.base_url}/session/data/{self.datasource}/users"
        )

    def assign_system_permission(
        self,
        username: str,
        permission: str,
    ) -> requests.Response:
        """
        Assign a system permission to a user.

        Parameters
        ----------
        username : str
            The username of the user to assign the permission to.
        permission : str
            The system permission to assign (e.g., "CREATE_USER", "CREATE_CONNECTION").

        Returns
        -------
        requests.Response
            The HTTP response indicating success (204 No Content).

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 404 for non-existent user, 400 for invalid permission).

        Examples
        --------
        >>> response = permissions_manager.assign_system_permission("daxm", "CREATE_USER")
        >>> print(response.status_code)
        204
        """
        payload = [
            {
                "op": "add",
                "path": "/systemPermissions",
                "value": permission,
            }
        ]
        result = requester(
            guac_client=self.client,
            url=f"{self.url}/{username}/permissions",
            method="PATCH",
            payload=payload,
            json_response=False,
        )
        return result  # type: ignore[return-value]

    def revoke_system_permission(
        self,
        username: str,
        permission: str,
    ) -> requests.Response:
        """
        Revoke a system permission from a user.

        Parameters
        ----------
        username : str
            The username of the user to revoke the permission from.
        permission : str
            The system permission to revoke (e.g., "CREATE_USER", "CREATE_CONNECTION").

        Returns
        -------
        requests.Response
            The HTTP response indicating success (204 No Content).

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 404 for non-existent user, 400 for invalid permission).

        Examples
        --------
        >>> response = permissions_manager.revoke_system_permission("daxm", "CREATE_USER")
        >>> print(response.status_code)
        204
        """
        payload = [
            {
                "op": "remove",
                "path": "/systemPermissions",
                "value": permission,
            }
        ]
        result = requester(
            guac_client=self.client,
            url=f"{self.url}/{username}/permissions",
            method="PATCH",
            payload=payload,
            json_response=False,
        )
        return result  # type: ignore[return-value]
