from __future__ import annotations
import logging
from typing import TYPE_CHECKING, Any, Dict, Optional
from urllib.parse import urljoin
import requests
import os 
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")
if TYPE_CHECKING:
    from fin68.exceptions import HttpError  # pragma: no cover

logger = logging.getLogger(__name__)

BASE_URL=os.getenv('FIN68_URL','https://fin68.vn/api/v1/fin68')

# BASE_URL = "https://fin68.vn/api/v1/fin68"
# BASE_URL = "http://127.0.0.1:33033/api/v1/fin68"
DEFAULT_TIMEOUT = 30


def _default_user_agent(version: str) -> str:
    return f"fin68/{version}"


class HttpSession:
    """Lightweight wrapper around :class:`requests.Session` with Fin68 defaults."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = BASE_URL,
        version: str = "0.0.0",
        timeout: int = DEFAULT_TIMEOUT,
        user_agent: Optional[str] = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": user_agent or _default_user_agent(version),
            }
        )

    def _prepare_url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return urljoin(f"{self.base_url}/", path.lstrip("/"))

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        url = self._prepare_url(path)
        merged_headers = {}
        if headers:
            merged_headers.update(headers)
        logger.debug("HTTP %s %s params=%s", method, url, params)
        try:
            response = self._session.request(
                method,
                url,
                params=params,
                json=json_body,
                data=data,
                headers=merged_headers or None,
                timeout=timeout or self.timeout,
            )
        except requests.RequestException as exc:  # pragma: no cover - network failure
            from fin68.exceptions import HttpError

            raise HttpError(f"Failed to reach {url}") from exc

        if response.status_code >= 400:
            payload: Optional[Any]
            try:
                payload = response.json()
            except ValueError:
                payload = response.text
            from fin68.exceptions import HttpError

            raise HttpError(
                f"Fin68 backend returned HTTP {response.status_code} for {url}",
                status_code=response.status_code,
                payload=payload,
            )
        return response

    def get(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        return self.request("GET", path, params=params, headers=headers, timeout=timeout)

    def post(
        self,
        path: str,
        *,
        json_body: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        return self.request(
            "POST",
            path,
            json_body=json_body,
            data=data,
            headers=headers,
            timeout=timeout,
        )

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "HttpSession":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
