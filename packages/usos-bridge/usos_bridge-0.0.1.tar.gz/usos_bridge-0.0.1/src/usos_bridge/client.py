import contextlib
import json

import httpx

from usos_bridge import errors
from usos_bridge.auth import WebUsosAuthenticator
from usos_bridge.instance_config import UsosInstanceConfig


class UsosApiClient:

    def __init__(self, instance_cfg: UsosInstanceConfig, authenticator: WebUsosAuthenticator) -> None:
        self._instance_config = instance_cfg
        self._authenticator = authenticator

    def request(self, method: str, data: dict | None = None, *, timeout: int = 5, retry: int = 3) -> httpx.Response:
        last_exception: Exception | None = None

        for _ in range(retry):
            try:
                return self._request(method, data=data, timeout=timeout)
            except (errors.InvalidCookieError, errors.InvalidCsrfTokenError) as e:
                last_exception = e
                self._authenticator.refresh()
            except httpx.RequestError as e:
                last_exception = e

        msg = "Request failed after multiple retries."
        raise last_exception or errors.UsosBridgeError(msg)

    def _request(self, method: str, data: dict | None = None, *, timeout: int = 5) -> httpx.Response:
        data_copy = data.copy() if data is not None else {}

        data_copy[self._instance_config.csrf_token_data_key] = self._authenticator.csrf_token

        params = {self._instance_config.proxy_api_method_param_key: method}

        response = httpx.post(
            self._instance_config.proxy_endpoint,
            data=data_copy,
            timeout=timeout,
            params=params,
            headers={"Cookie": f"{self._instance_config.session_cookie_name}={self._authenticator.cookie}"},
        )

        if not response.is_success:
            self._handle_unsuccessful_response(response)

        return response

    def _handle_unsuccessful_response(self, response: httpx.Response) -> None:
        match response.status_code:
            case httpx.codes.BAD_REQUEST:
                self._handle_bad_request_response(response)

        reason = "unknown"  # TODO(ginal): handle each api error separately
        with contextlib.suppress(json.JSONDecodeError):
            reason = response.json().get("message", reason)

        msg = f"status code {response.status_code}, reason: {reason}"
        raise errors.UsosHttpError(response.status_code, response.text, msg)

    def _handle_bad_request_response(self, response: httpx.Response) -> None:
        with contextlib.suppress(json.JSONDecodeError):
            self._handle_bad_request_json_response(response.json())

        self._handle_bad_request_text_response(response)

    def _handle_bad_request_json_response(self, response_json: dict) -> None:
        pass  # TODO(ginal): implement this

    @staticmethod
    def _handle_bad_request_text_response(response: httpx.Response) -> None:
        if "Invalid CSRF token" in response.text:
            raise errors.InvalidCsrfTokenError

        if "Missing session CSRF token." in response.text:
            raise errors.InvalidCookieError(response.status_code, response.text)
