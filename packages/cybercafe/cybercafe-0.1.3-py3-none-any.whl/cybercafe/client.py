from .models.space import Space
from .utils.request import request
from typing import Dict, Any, List


class Cybercafe:
    """
    Cybercafe client entrypoint.
    """

    def __init__(self, api_key: str, base_url: str = "https://api.cybercafe.space"):
        if not api_key:
            raise ValueError("API key must be provided")
        self.api_key = api_key
        self.base_url = base_url

    def space(self, space_id: str) -> Space:
        """
        Create a Space instance by ID.
        """
        return Space(self.base_url, self.api_key, space_id)

    async def create_space(self, name: str, location: str, type: int) -> Dict[str, Any]:
        """
        Create a new space.

        :param name: The username for the space.
        :param location: The space region.
        :param type: The space type.
        :return: { "success": bool, "message": str }
        """
        return await request(
            f"{self.base_url}/v1/spaces/create",
            method="POST",
            headers={"x-api-key": self.api_key},
            data={"name": name, "location": location, "type": type},
        )

    async def delete_space(self, space_id: str) -> Dict[str, Any]:
        """
        Delete an existing space.

        :param space_id: The ID of the space to delete.
        :return: { "success": bool, "message": str }
        """
        return await request(
            f"{self.base_url}/v1/spaces/delete",
            method="POST",
            headers={"x-api-key": self.api_key},
            data={"space_id": space_id},
        )

    async def list_spaces(self) -> List[Dict[str, Any]]:
        """
        List all spaces belonging to the authenticated user.

        Each space has:
            - location: the Azure region where the VM is hosted
            - type: the machine type (used for billing rates)
            - name: the username assigned to the machine
        """
        return await request(
            f"{self.base_url}/v1/spaces",
            method="GET",
            headers={"x-api-key": self.api_key},
        )
