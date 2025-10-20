class InvalidPhoneError(Exception):
    """
    Исключение, вызываемое при неверном формате номера телефона.

    Args:
        phone (str): Некорректный номер телефона.
    """

    def __init__(self, phone: str) -> None:
        super().__init__(f"Invalid phone number format: {phone}")


class WebSocketNotConnectedError(Exception):
    """
    Исключение, вызываемое при попытке обращения к WebSocket,
    если соединение не установлено.
    """

    def __init__(self) -> None:
        super().__init__("WebSocket is not connected")


class LoginError(Exception):
    """
    Исключение, вызываемое при ошибке авторизации.
    """

    def __init__(self, message: str) -> None:
        super().__init__(f"Login error: {message}")
