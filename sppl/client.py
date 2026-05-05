"""Transport clients for SPPL printers."""

from __future__ import annotations

import socket
from dataclasses import dataclass
from typing import Optional, Protocol, Union

from .commands import SPPLCommands
from .exceptions import SPPLTransportError
from .protocol import END, SPPLCommand, SPPLResponse, parse_response


class Transport(Protocol):
    def open(self) -> None:
        ...

    def close(self) -> None:
        ...

    def send(self, payload: bytes) -> None:
        ...

    def receive_until(self, terminator: bytes = b"^", max_bytes: int = 65536) -> bytes:
        ...


@dataclass
class TcpTransport:
    host: str
    port: int = 9100
    timeout: float = 5.0
    encoding: str = "ascii"
    _socket: Optional[socket.socket] = None

    def open(self) -> None:
        if self._socket is not None:
            return
        try:
            self._socket = socket.create_connection((self.host, self.port), timeout=self.timeout)
            self._socket.settimeout(self.timeout)
        except OSError as exc:
            raise SPPLTransportError(f"Cannot connect to {self.host}:{self.port}") from exc

    def close(self) -> None:
        if self._socket is not None:
            self._socket.close()
            self._socket = None

    def send(self, payload: bytes) -> None:
        self.open()
        assert self._socket is not None
        try:
            self._socket.sendall(payload)
        except OSError as exc:
            raise SPPLTransportError("Cannot send SPPL payload") from exc

    def receive_until(self, terminator: bytes = b"^", max_bytes: int = 65536) -> bytes:
        self.open()
        assert self._socket is not None
        chunks = bytearray()
        while len(chunks) < max_bytes:
            try:
                chunk = self._socket.recv(1)
            except socket.timeout as exc:
                raise SPPLTransportError("Timed out waiting for SPPL response") from exc
            except OSError as exc:
                raise SPPLTransportError("Cannot receive SPPL response") from exc
            if not chunk:
                break
            chunks.extend(chunk)
            if chunk == terminator:
                return bytes(chunks)
        if not chunks:
            raise SPPLTransportError("No SPPL response received")
        return bytes(chunks)


@dataclass
class SerialTransport:
    port: str
    baudrate: int = 115200
    timeout: float = 5.0
    parity: str = "N"
    bytesize: int = 8
    stopbits: int = 1
    _serial: Optional[object] = None

    def open(self) -> None:
        if self._serial is not None:
            return
        try:
            import serial  # type: ignore
        except ImportError as exc:
            raise SPPLTransportError("Install savema-sppl[serial] to use SerialTransport") from exc
        self._serial = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            timeout=self.timeout,
            parity=self.parity,
            bytesize=self.bytesize,
            stopbits=self.stopbits,
        )

    def close(self) -> None:
        if self._serial is not None:
            self._serial.close()
            self._serial = None

    def send(self, payload: bytes) -> None:
        self.open()
        assert self._serial is not None
        written = self._serial.write(payload)
        if written != len(payload):
            raise SPPLTransportError("Serial transport wrote a partial SPPL payload")

    def receive_until(self, terminator: bytes = b"^", max_bytes: int = 65536) -> bytes:
        self.open()
        assert self._serial is not None
        data = self._serial.read_until(terminator, size=max_bytes)
        if not data:
            raise SPPLTransportError("No SPPL response received")
        return data


class SavemaPrinterClient(SPPLCommands):
    """SPPL command factory plus an Ethernet or serial transport."""

    def __init__(self, transport: Transport, encoding: str = "ascii") -> None:
        self.transport = transport
        self.encoding = encoding

    @classmethod
    def tcp(
        cls, host: str, port: int = 9100, timeout: float = 5.0, encoding: str = "ascii"
    ) -> "SavemaPrinterClient":
        return cls(TcpTransport(host=host, port=port, timeout=timeout, encoding=encoding), encoding)

    @classmethod
    def serial(
        cls,
        port: str,
        baudrate: int = 115200,
        timeout: float = 5.0,
        parity: str = "N",
        bytesize: int = 8,
        stopbits: int = 1,
        encoding: str = "ascii",
    ) -> "SavemaPrinterClient":
        transport = SerialTransport(
            port=port,
            baudrate=baudrate,
            timeout=timeout,
            parity=parity,
            bytesize=bytesize,
            stopbits=stopbits,
        )
        return cls(transport, encoding)

    def open(self) -> None:
        self.transport.open()

    def close(self) -> None:
        self.transport.close()

    def __enter__(self) -> "SavemaPrinterClient":
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def send(self, command: Union[str, SPPLCommand]) -> None:
        frame = command.frame if isinstance(command, SPPLCommand) else str(command)
        self.transport.send(frame.encode(self.encoding))

    def receive(self) -> SPPLResponse:
        raw = self.transport.receive_until(END.encode(self.encoding))
        return parse_response(raw, encoding=self.encoding)

    def execute(self, command: Union[str, SPPLCommand], expect_response: bool = True) -> Optional[SPPLResponse]:
        self.send(command)
        if not expect_response:
            return None
        return self.receive()

