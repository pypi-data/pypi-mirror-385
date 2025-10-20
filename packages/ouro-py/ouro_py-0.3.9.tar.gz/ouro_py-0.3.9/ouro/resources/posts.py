import logging
from typing import List, Optional, Union

from ouro._resource import SyncAPIResource
from ouro.models import Post

from .content import Content, Editor

log: logging.Logger = logging.getLogger(__name__)


__all__ = ["Posts"]


class Posts(SyncAPIResource):
    def __init__(self, client):
        super().__init__(client)

    @staticmethod
    def Editor(**kwargs) -> Editor:
        return Editor(**kwargs)

    @staticmethod
    def Content(**kwargs) -> "Content":
        return Content(**kwargs)

    def create(
        self,
        content: "Content",
        name: str,
        description: Optional[Union[str, "Content"]] = None,
        visibility: Optional[str] = None,
        monetization: Optional[str] = None,
        price: Optional[float] = None,
        **kwargs,
    ) -> Post:
        """
        Create a new Post
        """

        post = {
            "name": name,
            # Allow description to be a plain string or Content
            "description": (
                description.to_dict()
                if isinstance(description, Content)
                else description
            ),
            "visibility": visibility,
            "monetization": monetization,
            "price": price,
            **kwargs,
            # Strictly enforce these fields
            "source": "api",
            "asset_type": "post",
        }
        # Filter out None values
        post = {k: v for k, v in post.items() if v is not None}

        request = self.client.post(
            "/posts/create",
            json={
                "post": post,
                "content": content.to_dict(),
            },
        )
        request.raise_for_status()
        response = request.json()
        if response["error"]:
            raise Exception(response["error"])

        return Post(**response["data"])

    def retrieve(self, id: str):
        """
        Retrieve a Post by its id
        """
        request = self.client.get(
            f"/posts/{id}",
        )
        request.raise_for_status()
        response = request.json()
        if response["error"]:
            raise Exception(response["error"])

        return Post(**response["data"])

    def update(
        self,
        id: str,
        content: Optional["Content"] = None,
        name: Optional[str] = None,
        description: Optional[Union[str, "Content"]] = None,
        visibility: Optional[str] = None,
        monetization: Optional[str] = None,
        price: Optional[float] = None,
        **kwargs,
    ) -> Post:
        """
        Update a Post by its id
        """

        post = {
            "name": name,
            # Allow description to be a plain string or Content
            "description": (
                description.to_dict()
                if isinstance(description, Content)
                # TODO: handle conversion of string
                else description
            ),
            "visibility": visibility,
            "monetization": monetization,
            "price": price,
            **kwargs,
        }
        # Filter out None values
        post = {k: v for k, v in post.items() if v is not None}

        request = self.client.put(
            f"/posts/{id}",
            json={
                "post": post,
                "content": content.to_dict() if content is not None else None,
            },
        )
        request.raise_for_status()
        response = request.json()
        if response["error"]:
            raise Exception(response["error"])
        return Post(**response["data"])

    def delete(self, id: str):
        """
        Delete a Post by its id
        """
        request = self.client.delete(
            f"/posts/{id}",
        )
        request.raise_for_status()
        response = request.json()
        return response
