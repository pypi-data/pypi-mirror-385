import socket
from typing import Mapping

import requests


from enum import Enum

from requests.models import Response

from pylizlib.core.log.pylizLogger import logger


class NetResponseType(Enum):
    OK200 = "ok200"
    ERROR = "error"
    CONNECTION_ERROR = "connection_error"
    TIMEOUT = "timeout"
    REQUEST_ERROR = "request_error"



class NetResponse:

    def __init__(
            self,
            response: Response | None,
            response_type: NetResponseType,
            exception=None
    ):
        self.has_json_header = None
        self.json = None
        self.response = response
        self.hasResponse = self.response is not None
        if self.hasResponse:
            self.code = self.response.status_code
            self.text: str = self.response.text
        else:
            self.code = None
        self.type = response_type
        self.exception = exception
        if self.hasResponse:
            self.has_json_header = "application/json" in self.response.headers.get("Content-Type", "")
            if self.has_json_header:
                self.json = self.response.json()
        self.__log()


    def __log(self):
        logger.trace(f"NetResponse: code={self.code} | type={self.type} | jsonHeader={self.has_json_header}")

    def __str__(self):
        return ""

    def is_successful(self):
        return self.code == 200

    def is_error(self):
        return self.code != 200

    def get_error(self):
        if self.hasResponse:
            return "(" + str(self.code) + "): " + self.response.text
        else:
            pre = "(" + self.type.value + ") "
            if self.exception is not None:
                pre = pre + str(self.exception)
            return pre




HEADER_ONLY_CONTENT_JSON = {"Content-Type": "application/json"}



def test_with_head(url: str) -> bool:
    try:
        response = requests.head(url, timeout=5)
        return response.status_code < 400
    except requests.RequestException as e:
        logger.error("Error while testing URL: " + url + " - " + str(e))
        return False


def is_endpoint_reachable(url: str) -> bool:
    """Controlla se un endpoint risponde correttamente con HTTP 200."""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.RequestException as e:
        logger.error("Error while testing URL: " + url + " - " + str(e))
        return False


def is_internet_available() -> bool:
    host = "8.8.8.8"
    port = 53
    timeout = 3
    try:
        socket.setdefaulttimeout(timeout)
        # Utilizza un blocco `with` per gestire automaticamente il socket
        with socket.create_connection((host, port)):
            return True
    except OSError:
        return False


def exec_get(
        url: str,
        headers: Mapping[str, str | bytes | None] | None = None,
        sec_timeout: int | None = 10
) -> NetResponse:
    try:
        logger.trace("Executing GET request on URL: " + url)
        response = requests.get(url, allow_redirects=True, headers=headers, timeout=sec_timeout)
        if response.status_code == 200:
            return NetResponse(response, NetResponseType.OK200)
        else:
            return NetResponse(response, NetResponseType.ERROR)
    except requests.ConnectionError as e:
        return NetResponse(None, NetResponseType.CONNECTION_ERROR, e)
    except requests.Timeout as e:
        return NetResponse(None, NetResponseType.TIMEOUT, e)
    except requests.RequestException as e:
        return NetResponse(None, NetResponseType.REQUEST_ERROR, e)


def exec_post(
        url: str,
        payload,
        headers: Mapping[str, str | bytes | None] | None = None,
        verify_bool: bool = False,
) -> NetResponse:
    try:
        logger.trace("Executing POST request on URL: " + url)
        response = requests.post(url, json=payload, verify=verify_bool, allow_redirects=True, headers=headers)
        if response.status_code == 200:
            return NetResponse(response, NetResponseType.OK200)
        else:
            return NetResponse(response, NetResponseType.ERROR)
    except requests.ConnectionError as e:
        return NetResponse(None, NetResponseType.CONNECTION_ERROR, e)
    except requests.Timeout as e:
        return NetResponse(None, NetResponseType.TIMEOUT, e)
    except requests.RequestException as e:
        return NetResponse(None, NetResponseType.REQUEST_ERROR, e)


def get_file_size_byte(url: str, exception_on_fail: bool = False) -> int:
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        response.raise_for_status()
        file_size = response.headers.get('content-length', 0)
        if file_size is None:
            if exception_on_fail:
                raise ValueError("Unable to get file size for url: " + url)
            return -1
        return int(file_size)
    except requests.RequestException as e:
        if exception_on_fail:
            raise ValueError("Unable to get file size for url: " + url + ": " + str(e))
        return -1