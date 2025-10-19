USOS_HTTP_ERROR_MSG_TEMPLATE: str = "HTTP error occured, got status code {status_code}"
INVALID_CSRF_TOKEN_ERROR_MSG_TEMPLATE: str = "Invalid CSRF token"  # noqa: S105
INVALID_COOKIE_ERROR_MSG_TEMPLATE: str = "Invalid cookie"


class UsosBridgeError(Exception):
    pass


class UsosHttpError(UsosBridgeError):

    def __init__(self, status_code: int, response_text: str, message_template: str | None = None) -> None:
        self.status_code: int = status_code
        self.response_text: str = response_text

        if message_template is None:
            message_template = USOS_HTTP_ERROR_MSG_TEMPLATE

        super().__init__(message_template.format(status_code=status_code, response_text=response_text))


class AuthenticationError(UsosHttpError):
    pass


class InvalidCsrfTokenError(AuthenticationError):

    def __init__(self, status_code: int, response_text: str, message_template: str | None = None) -> None:
        if message_template is None:
            message_template = INVALID_CSRF_TOKEN_ERROR_MSG_TEMPLATE

        super().__init__(status_code, response_text, message_template)


class InvalidCookieError(AuthenticationError):
    def __init__(self, status_code: int, response_text: str, message_template: str | None = None) -> None:
        if message_template is None:
            message_template = INVALID_COOKIE_ERROR_MSG_TEMPLATE

        super().__init__(status_code, response_text, message_template)


class LoginFailedError(AuthenticationError):
    pass


class LoginPageLoadError(UsosHttpError):
    pass


class ParsingError(UsosBridgeError):
    pass


class LoginFormNotFoundError(ParsingError):
    pass


class LoginActionURLNotFoundError(ParsingError):
    pass


class CsrfTokenNotFoundError(ParsingError):
    pass
