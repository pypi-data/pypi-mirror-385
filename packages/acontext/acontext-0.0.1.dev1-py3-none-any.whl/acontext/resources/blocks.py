"""
Block endpoints.
"""

from typing import Any, Mapping, MutableMapping

from ..client_types import RequesterProtocol


class BlocksAPI:
    def __init__(self, requester: RequesterProtocol) -> None:
        self._requester = requester

    def list(
        self,
        space_id: str,
        *,
        parent_id: str | None = None,
        block_type: str | None = None,
    ) -> Any:
        params: dict[str, Any] = {}
        if parent_id is not None:
            params["parent_id"] = parent_id
        if block_type is not None:
            params["type"] = block_type
        return self._requester.request("GET", f"/space/{space_id}/block", params=params or None)

    def create(
        self,
        space_id: str,
        *,
        block_type: str,
        parent_id: str | None = None,
        title: str | None = None,
        props: Mapping[str, Any] | MutableMapping[str, Any] | None = None,
    ) -> Any:
        if not block_type:
            raise ValueError("block_type is required")
        payload: dict[str, Any] = {"type": block_type}
        if parent_id is not None:
            payload["parent_id"] = parent_id
        if title is not None:
            payload["title"] = title
        if props is not None:
            payload["props"] = props
        return self._requester.request("POST", f"/space/{space_id}/block", json_data=payload)

    def delete(self, space_id: str, block_id: str) -> None:
        self._requester.request("DELETE", f"/space/{space_id}/block/{block_id}")

    def get_properties(self, space_id: str, block_id: str) -> Any:
        return self._requester.request("GET", f"/space/{space_id}/block/{block_id}/properties")

    def update_properties(
        self,
        space_id: str,
        block_id: str,
        *,
        title: str | None = None,
        props: Mapping[str, Any] | MutableMapping[str, Any] | None = None,
    ) -> None:
        payload: dict[str, Any] = {}
        if title is not None:
            payload["title"] = title
        if props is not None:
            payload["props"] = props
        if not payload:
            raise ValueError("title or props must be provided")
        self._requester.request("PUT", f"/space/{space_id}/block/{block_id}/properties", json_data=payload)

    def move(
        self,
        space_id: str,
        block_id: str,
        *,
        parent_id: str | None = None,
        sort: int | None = None,
    ) -> None:
        payload: dict[str, Any] = {}
        if parent_id is not None:
            payload["parent_id"] = parent_id
        if sort is not None:
            payload["sort"] = sort
        if not payload:
            raise ValueError("parent_id or sort must be provided")
        self._requester.request("PUT", f"/space/{space_id}/block/{block_id}/move", json_data=payload)

    def update_sort(self, space_id: str, block_id: str, *, sort: int) -> None:
        self._requester.request(
            "PUT",
            f"/space/{space_id}/block/{block_id}/sort",
            json_data={"sort": sort},
        )
