import httpx
from typing import Any, Dict, Optional, Union
from ..errors.SpaceError import SpaceError

async def request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    data: Optional[Union[Dict[str, Any], bytes]] = None,
    files: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, str]] = None,
    response_type: str = "json",
) -> Any:
    headers = headers or {}
    kwargs: Dict[str, Any] = {"headers": headers, "params": params}

    # Handle file uploads with additional form data
    if files is not None:
        kwargs["files"] = files
        if data and isinstance(data, dict):
            kwargs["data"] = data  # Text form fields go here
    elif data is not None:
        if isinstance(data, (bytes, bytearray)):
            kwargs["content"] = data
        else:
            kwargs["json"] = data
            kwargs["headers"]["Content-Type"] = "application/json"

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.request(method, url, **kwargs)

            if resp.status_code >= 400:
                try:
                    error_msg = resp.json().get("error")
                except Exception:
                    error_msg = resp.text or f"HTTP {resp.status_code}"
                raise SpaceError(error_msg)

            if response_type == "json":
                return resp.json()
            elif response_type == "arraybuffer":
                return resp.content
            elif response_type == "text":
                return resp.text
            return resp

        except httpx.RequestError as exc:
            raise SpaceError(f"Request failed: {exc}") from exc
