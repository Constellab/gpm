

import json
import os
from typing import Literal, Optional, TypedDict

from requests import Response, get


class CommunityBrick(TypedDict):
    brickName: str
    brickVersion: str
    repoType: Literal["git", "pip"]
    # url without credential to access the repository
    repositoryUrl: str
    # url with credential to access the repository
    repositoryAccessUrl: str


class CommunityService:
    """
    Service to request community api to retrieve informations about the bricks
    """

    @staticmethod
    def get_brick(brick_name: str, verison: str) -> CommunityBrick:
        """
        Get the information about a brick
        """

        # set the api key in the header if it is defined
        # is is only mandatory for private bricks
        headers = {}
        api_key = CommunityService._get_api_key()
        if api_key is not None:
            headers["X-Api-Key"] = api_key

        response = get(
            f"{CommunityService._get_api_url()}/brick/space/name/{brick_name}/{verison}",
            headers=headers
        )

        if response.status_code != 200:
            error = CommunityService.handle_error(response)
            raise Exception(error)

        return response.json()

    @staticmethod
    def handle_error(response: Response) -> str:
        try:
            error_json = response.json()

            if 'detail' in error_json:
                return error_json['detail']

            return response.text
        except Exception:
            return response.text

    @staticmethod
    def _get_api_url() -> str:
        """
        Get the url of the api
        """
        api_url = os.getenv("COMMUNITY_API_URL")

        if api_url is None:
            raise ValueError("COMMUNITY_API_URL env variable is not defined")

        return api_url

    @staticmethod
    def _get_api_key() -> Optional[str]:
        """
        Get the api key
        """
        return os.getenv("COMMUNITY_API_KEY")
