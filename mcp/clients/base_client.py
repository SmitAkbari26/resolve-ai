import httpx
from typing import Dict, Any


class BaseClient:
    def __init__(self, base_url: str, endpoint: str, timeout: int = 30):
        self.base_url = base_url
        self.endpoint = f"{self.base_url}/{endpoint}"
        self.client = httpx.AsyncClient(
            timeout=timeout, headers={"Content-Type": "application/json"}
        )

    async def get(self, path: str = "", params: dict = None):
        try:
            response = await self.client.get(f"{self.endpoint}{path}", params=params)
            return self._handle_response(response)
        except Exception as ex:
            return self._error_response(ex)

    async def post(self, path: str = "", payload: dict = None):
        try:
            response = await self.client.post(f"{self.endpoint}{path}", json=payload)
            return self._handle_response(response)
        except Exception as ex:
            return self._error_response(ex)

    async def put(self, path: str = "", payload: dict = None):
        try:
            response = await self.client.put(f"{self.endpoint}{path}", json=payload)
            return self._handle_response(response)
        except Exception as ex:
            return self._error_response(ex)

    async def patch(self, path: str = "", payload: dict = None):
        try:
            response = await self.client.patch(f"{self.endpoint}{path}", json=payload)
            return self._handle_response(response)
        except Exception as ex:
            return self._error_response(ex)

    async def delete(self, path: str = ""):
        try:
            response = await self.client.delete(f"{self.endpoint}{path}")
            return self._handle_response(response)
        except Exception as ex:
            return self._error_response(ex)

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        try:
            response.raise_for_status()
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json(),
            }
        except httpx.HTTPStatusError as ex:
            try:
                details = response.json()
            except Exception:
                details = response.text
            return {
                "success": False,
                "status_code": response.status_code,
                "error": str(ex),
                "details": details,
            }

    def _error_response(self, error: Exception):
        return {"success": False, "error": str(error)}

    async def close(self):
        await self.client.aclose()
