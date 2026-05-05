"""Low-level SPPL framing and response parsing."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Optional, Sequence, Union

from .exceptions import SPPLProtocolError

START = "~"
END = "^"
COMMAND_SEPARATOR = "|"
PARAM_SEPARATOR = ">"
RESPONSE_SEPARATOR = "<"
GT_SEPARATOR = "~gt~"


Scalar = Union[str, int, float, bool, Enum]


def _stringify(value: Scalar) -> str:
    if isinstance(value, Enum):
        return str(value.value)
    if isinstance(value, bool):
        return "1" if value else "0"
    return str(value)


def _validate_code(code: str) -> str:
    normalized = code.strip().upper()
    if len(normalized) != 6 or not normalized.startswith("SP"):
        raise SPPLProtocolError(f"Invalid SPPL command code: {code!r}")
    if any(ch in normalized for ch in "{}~^|"):
        raise SPPLProtocolError(f"Invalid SPPL command code: {code!r}")
    return normalized


def _validate_parameter(value: str, separator: str) -> None:
    forbidden = [END, "{", "}"]
    if separator:
        forbidden.append(separator)
    for token in forbidden:
        if token and token in value:
            raise SPPLProtocolError(
                f"Parameter contains reserved token {token!r}; use raw_params for opaque payloads"
            )


@dataclass(frozen=True)
class SPPLCommand:
    """A single SPPL command body that can be framed for transport."""

    code: str
    params: Sequence[Scalar] = ()
    separator: str = PARAM_SEPARATOR
    raw_params: Optional[str] = None
    validate_params: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "code", _validate_code(self.code))
        if self.raw_params is not None and self.params:
            raise SPPLProtocolError("Use either params or raw_params, not both")

    @property
    def body(self) -> str:
        if self.raw_params is not None:
            return f"{self.code}{{{self.raw_params}}}"
        if not self.params:
            return self.code
        values = [_stringify(value) for value in self.params]
        if self.validate_params:
            for value in values:
                _validate_parameter(value, self.separator)
        return f"{self.code}{{{self.separator.join(values)}}}"

    @property
    def frame(self) -> str:
        return f"{START}{self.body}{END}"

    def encode(self, encoding: str = "ascii") -> bytes:
        return self.frame.encode(encoding)

    def __str__(self) -> str:
        return self.frame


@dataclass(frozen=True)
class SPPLResponse:
    """Parsed response frame returned by a printer."""

    raw: str
    code: str
    payload: Optional[str] = None
    source_command: Optional[str] = None
    values: Sequence[str] = ()

    @property
    def ok(self) -> bool:
        text = (self.payload or "").upper()
        return "FAIL" not in text and "ERROR" not in text


def build_command(
    code: str,
    *params: Scalar,
    separator: str = PARAM_SEPARATOR,
    raw_params: Optional[str] = None,
    validate_params: bool = True,
) -> SPPLCommand:
    """Build a typed SPPL command object."""

    return SPPLCommand(
        code=code,
        params=params,
        separator=separator,
        raw_params=raw_params,
        validate_params=validate_params,
    )


def build_batch(commands: Iterable[Union[str, SPPLCommand]]) -> str:
    """Build a multi-command SPPL frame.

    SPPL batches start once with ``~`` and end once with ``^``; individual command
    bodies are separated by ``|``.
    """

    bodies = []
    for command in commands:
        text = command.frame if isinstance(command, SPPLCommand) else str(command)
        text = text.strip()
        if text.startswith(START) and text.endswith(END):
            text = text[1:-1]
        if not text:
            raise SPPLProtocolError("Empty command in batch")
        bodies.append(text)
    if not bodies:
        raise SPPLProtocolError("Cannot build an empty SPPL batch")
    return f"{START}{COMMAND_SEPARATOR.join(bodies)}{END}"


def parse_response(raw: Union[str, bytes], encoding: str = "ascii") -> SPPLResponse:
    """Parse an SPPL response frame.

    The manual shows general responses as ``~SPGRES{COMMAND:value<value}^``.
    This parser also handles simple command responses without payload.
    """

    text = raw.decode(encoding, errors="replace") if isinstance(raw, bytes) else raw
    text = text.strip()
    if not (text.startswith(START) and text.endswith(END)):
        raise SPPLProtocolError(f"Invalid SPPL frame: {text!r}")
    body = text[1:-1]
    if "{" not in body:
        return SPPLResponse(raw=text, code=_validate_code(body))
    if not body.endswith("}"):
        raise SPPLProtocolError(f"Invalid SPPL response payload: {text!r}")
    code, payload = body.split("{", 1)
    code = _validate_code(code)
    payload = payload[:-1]
    source_command = None
    value_text = payload
    if ":" in payload:
        source_command, value_text = payload.split(":", 1)
        source_command = source_command.strip().upper() or None
    values = tuple(value_text.split(RESPONSE_SEPARATOR)) if value_text else ()
    return SPPLResponse(
        raw=text,
        code=code,
        payload=payload,
        source_command=source_command,
        values=values,
    )

