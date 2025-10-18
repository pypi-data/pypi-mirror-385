"""
Agents client for managing conversation agents.
"""

import httpx
from typing import Dict, List, Optional, Literal

from .types import Agent
from .exceptions import create_error_from_response


class Agents:
    """
    Agents client for managing conversation agents.
    
    Provides methods for creating, retrieving, updating, deleting, and searching agents.
    """

    def __init__(
        self,
        base_url: str,
        token: str,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        """
        Initialize the Agents client.
        
        Args:
            base_url: Base URL for the API
            token: Authentication token
            http_client: Optional shared HTTP client instance
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.api_url = self.base_url
        self._client = http_client or httpx.AsyncClient(timeout=httpx.Timeout(timeout=600.0, connect=5.0), limits=httpx.Limits(max_connections=1000, max_keepalive_connections=100))
        self._owns_client = http_client is None

    def _get_headers(self, content_type: Optional[str] = None) -> Dict[str, str]:
        """Get headers with authentication and optional content type."""
        headers = {"Authorization": f"Bearer {self.token}"}
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    async def create(
        self,
        name: str,
        type: Literal["human", "ai"],
        assistant_id: Optional[str] = None,
        profile_id: Optional[str] = None,
    ) -> Agent:
        """
        Create a new agent.
        
        Args:
            name: Name of the agent
            type: Type of agent ("human" or "ai")
            assistant_id: ID of the assistant (required for AI agents)
            profile_id: ID of the profile (required for human agents)
            
        Returns:
            The created agent
            
        Raises:
            ConversationsError: If the request fails
        """
        data = {
            "name": name,
            "type": type,
        }
        
        if assistant_id is not None:
            data["assistant_id"] = assistant_id
        if profile_id is not None:
            data["profile_id"] = profile_id

        response = await self._client.post(
            f"{self.api_url}/agents",
            json=data,
            headers=self._get_headers("application/json")
        )

        if response.status_code != 201:
            raise create_error_from_response(response)

        return Agent.model_validate(response.json())

    async def get(self, agent_id: str) -> Agent:
        """
        Retrieve an agent by ID.
        
        Args:
            agent_id: ID of the agent to retrieve
            
        Returns:
            The agent
            
        Raises:
            ConversationsError: If the agent is not found or request fails
        """
        response = await self._client.get(
            f"{self.api_url}/agents/{agent_id}",
            headers=self._get_headers()
        )

        if response.status_code != 200:
            raise create_error_from_response(response)

        return Agent.model_validate(response.json())

    async def update(
        self,
        agent_id: str,
        name: Optional[str] = None,
        assistant_id: Optional[str] = None,
        profile_id: Optional[str] = None,
    ) -> Agent:
        """
        Update an agent.
        
        Args:
            agent_id: ID of the agent to update
            name: New name for the agent
            assistant_id: New assistant ID (for AI agents)
            profile_id: New profile ID (for human agents)
            
        Returns:
            The updated agent
            
        Raises:
            ConversationsError: If the agent is not found or request fails
        """
        fields = {}
        if name is not None:
            fields["name"] = name
        if assistant_id is not None:
            fields["assistant_id"] = assistant_id
        if profile_id is not None:
            fields["profile_id"] = profile_id

        data = {"fields": fields}

        response = await self._client.patch(
            f"{self.api_url}/agents/{agent_id}",
            json=data,
            headers=self._get_headers("application/json")
        )

        if response.status_code != 200:
            raise create_error_from_response(response)

        return Agent.model_validate(response.json())

    async def delete(self, agent_id: str) -> None:
        """
        Delete an agent.
        
        Args:
            agent_id: ID of the agent to delete
            
        Raises:
            ConversationsError: If the agent is not found or request fails
        """
        response = await self._client.delete(
            f"{self.api_url}/agents/{agent_id}",
            headers=self._get_headers()
        )

        if response.status_code != 204:
            raise create_error_from_response(response)

    async def search(
        self,
        type: Optional[Literal["human", "ai"]] = None,
        assistant_id: Optional[str] = None,
        profile_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Agent]:
        """
        Search for agents with optional filters.
        
        Args:
            type: Filter by agent type ("human" or "ai")
            assistant_id: Filter by assistant ID
            profile_id: Filter by profile ID
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of matching agents
            
        Raises:
            ConversationsError: If the request fails
        """
        data = {}
        if type is not None:
            data["type"] = type
        if assistant_id is not None:
            data["assistant_id"] = assistant_id
        if profile_id is not None:
            data["profile_id"] = profile_id
        if limit is not None:
            data["limit"] = limit
        if offset is not None:
            data["offset"] = offset

        response = await self._client.post(
            f"{self.api_url}/agents/search",
            json=data,
            headers=self._get_headers("application/json")
        )

        if response.status_code != 200:
            raise create_error_from_response(response)

        return [Agent.model_validate(agent_data) for agent_data in response.json()]

    async def close(self) -> None:
        """Close the HTTP client to free up resources."""
        if self._owns_client:
            await self._client.aclose()
