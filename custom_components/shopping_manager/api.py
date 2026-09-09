"""API client for the Shopping Manager backend."""

import aiohttp
import async_timeout


class ShoppingManagerApi:
    """Thin async wrapper around the Shopping Manager REST API."""

    def __init__(self, host: str, token: str | None, session: aiohttp.ClientSession) -> None:
        self._host = host.rstrip("/")
        self._token = token
        self._session = session

    async def _request(self, method: str, path: str, **kwargs):
        headers = {}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        url = f"{self._host}{path}"
        async with async_timeout.timeout(15):
            async with self._session.request(method, url, headers=headers, **kwargs) as resp:
                if resp.status == 401:
                    raise InvalidAuth("Ungültiger Token")
                if resp.status >= 400:
                    raise ApiError(f"HTTP {resp.status} für {path}")
                if resp.status == 204:
                    return None
                return await resp.json()

    async def get_lists(self) -> list:
        """Return all lists accessible to the (token) user: [{id, name, is_owner}]."""
        data = await self._request("GET", "/api/lists") or []
        return data

    async def get_items_for_list(self, list_id: int, status: str = "all") -> list:
        params = {"list_id": list_id}
        if status != "all":
            params["status"] = status
        data = await self._request("GET", "/api/items", params=params)
        return data or []

    async def get_counts_for_list(self, list_id: int) -> dict:
        data = await self._request("GET", "/api/items/summary/counts", params={"list_id": list_id}) or {}
        return data

    async def add_item_to_list(self, list_id: int, name: str, quantity: str = "", note: str = "") -> dict:
        payload = {"list_id": list_id, "name": name}
        if quantity:
            payload["quantity"] = quantity
        if note:
            payload["note"] = note
        return await self._request("POST", "/api/items", json=payload) or {}

    async def set_checked(self, item_id: int, checked: bool) -> dict:
        return await self._request("PATCH", f"/api/items/{item_id}/check", json={"checked": checked}) or {}

    async def delete_item(self, item_id: int) -> None:
        await self._request("DELETE", f"/api/items/{item_id}")

    async def get_items(self, status: str = "all", search: str = "") -> list:
        params = {}
        if status != "all":
            params["status"] = status
        if search:
            params["search"] = search
        data = await self._request("GET", "/api/items", params=params)
        return data or []

    async def get_counts(self) -> dict:
        # Multi-list: aggregate counts across ALL accessible lists.
        data = await self._request("GET", "/api/items/summary/counts/all") or {}
        return data

    async def create_list(self, name: str) -> dict:
        """Create a new shopping list (returns {id, name})."""
        return await self._request("POST", "/api/lists", json={"name": name}) or {}

    async def rename_list(self, list_id: int, name: str) -> dict:
        return await self._request("PATCH", f"/api/lists/{list_id}", json={"name": name}) or {}

    async def delete_list(self, list_id: int) -> None:
        await self._request("DELETE", f"/api/lists/{list_id}")


class ApiError(Exception):
    """Generic API error."""


class InvalidAuth(ApiError):
    """Authentication failed."""
