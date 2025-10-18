import re
from typing import NamedTuple

import httpx
from bs4 import BeautifulSoup as Bs

from usos_bridge.instance_config import UsosInstanceConfig

MAX_AUTH_RETRY: int = 4


class AuthPair(NamedTuple):
    cookie: str
    csrf_token: str


def _get_login_endpoint_url(instance_cfg: UsosInstanceConfig, client: httpx.Client) -> str:
    response = client.get(instance_cfg.auth_page_url)

    response.raise_for_status()

    auth_page = Bs(response.text, "html.parser", multi_valued_attributes=None)

    login_form = auth_page.select_one(instance_cfg.login_form_selector)

    if login_form is None:
        msg = "No login form found"
        raise RuntimeError(msg)  # TODO(ginal): custom error

    auth_url = str(login_form.attrs.get("action"))

    if auth_url is not None:
        return auth_url

    msg = "Auth url in login form not found"
    raise RuntimeError(msg)  # TODO(ginal): custom error


def _get_csrf_token(instance_cfg: UsosInstanceConfig, client: httpx.Client) -> str:
    response = client.get(instance_cfg.csrf_token_page)

    match = re.search(instance_cfg.csrf_token_regex, response.text)

    if match is not None:
        return match.group(1)  # TODO(ginal): test for checking regex pattern - if it has a singular group

    msg = "csrf token not found on page"
    raise RuntimeError(msg)  # TODO(ginal): custom error here


def _authorize_client(instance_cfg: UsosInstanceConfig, username: str, password: str, client: httpx.Client) -> None:
    auth_endpoint = _get_login_endpoint_url(instance_cfg, client)

    client.post(
        auth_endpoint,
        data={"username": username, "password": password},
        follow_redirects=True,
    )

    if client.cookies.get(instance_cfg.session_cookie_name) is None:
        raise RuntimeError  # TODO(ginal): custom error here


def get_auth_pair(instance_cfg: UsosInstanceConfig, username: str, password: str) -> AuthPair:
    with httpx.Client() as client:
        _authorize_client(instance_cfg, username, password, client)
        cookies: httpx.Cookies = client.cookies
        csrf_token = _get_csrf_token(instance_cfg, client)

    return AuthPair(cookies[instance_cfg.session_cookie_name], csrf_token)


class WebUsosAuthenticator:
    def __init__(self, username: str, password: str, instance_config: UsosInstanceConfig) -> None:
        self._username: str = username
        self._password: str = password
        self._instance_config: UsosInstanceConfig = instance_config

        self._auth_pair: AuthPair | None = None

    def _ensure_valid_auth_pair(self, *, retry: int = 1) -> AuthPair:
        if retry > MAX_AUTH_RETRY:
            raise RuntimeError  # TODO(ginal): implement custom error

        try:
            self._auth_pair = get_auth_pair(self._instance_config, self._username, self._password)
        except Exception:  # noqa: BLE001 TODO(ginal): catch possible errors here
            return self._ensure_valid_auth_pair(retry=retry + 1)

        return self._auth_pair

    def refresh(self) -> None:
        self._ensure_valid_auth_pair()

    @property
    def cookie(self) -> str:
        if self._auth_pair is None:
            return self._ensure_valid_auth_pair().cookie

        return self._auth_pair.cookie

    @property
    def csrf_token(self) -> str:
        if self._auth_pair is None:
            return self._ensure_valid_auth_pair().csrf_token

        return self._auth_pair.csrf_token
