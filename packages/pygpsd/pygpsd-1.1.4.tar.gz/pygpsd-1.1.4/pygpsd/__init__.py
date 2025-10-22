from __future__ import annotations

from io import TextIOWrapper
from json import loads
from socket import socket, AF_INET, SOCK_STREAM
from typing import Optional

from pygpsd.type.data import Data


class UnexpectedMessageException(Exception):
    def __init__(self, message: dict):
        Exception.__init__(self, f"Unexpected message: {message}")


class NoGPSDeviceFoundException(Exception):
    def __init__(self):
        Exception.__init__(self, "No GPS device found")


class GPSInactiveWarning(UserWarning):
    def __init__(self):
        Exception.__init__(self, "GPS is inactive")


class GPSD:
    socket: socket
    stream: Optional[TextIOWrapper] = None
    devices: list[dict[str, Data]] = []

    def _read(self) -> dict:
        return loads(self.stream.readline())

    def _write(self, data: str):
        self.stream.write(f"{data}\n")
        self.stream.flush()

    def on_unexpected_message(self, message: dict):
        raise UnexpectedMessageException(message)

    def __init__(self, host: str = "127.0.0.1", port: int = 2947):
        """
        Connect to the GPS daemon

        Throws
         - UnexpectedMessageException if an unexpected message is received
         - NoGPSDeviceFoundException if no GPS device is found

        :param host:
        :param port:
        """
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect((host, port))
        self.stream = self.socket.makefile("rw")

        msg = self._read()
        if msg["class"] != "VERSION":
            self.on_unexpected_message(msg)

        self._write('?WATCH={"enable":true}')

        msg = self._read()
        if msg["class"] == "DEVICES":
            self.devices = msg["devices"]
            if len(self.devices) == 0:
                raise NoGPSDeviceFoundException()

        msg = self._read()
        if msg["class"] == "WATCH":
            if not msg["enable"]:
                self.on_unexpected_message(msg)

    def poll(self) -> Data:
        """
        Poll the GPS daemon

        Throws
         - UnexpectedMessageException if an unexpected message is received
         - GPSInactiveWarning GPS is not active

        :return: Data
        """
        self._write("?POLL;")

        msg = self._read()
        if msg["class"] != "POLL":
            self.on_unexpected_message(msg)
        if not msg["active"]:
            raise GPSInactiveWarning()

        return Data.from_json(msg)
