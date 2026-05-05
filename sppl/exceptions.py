"""Exception hierarchy for SPPL."""


class SPPLError(Exception):
    """Base exception for SPPL errors."""


class SPPLProtocolError(SPPLError):
    """Raised when an SPPL command or response is malformed."""


class SPPLTransportError(SPPLError):
    """Raised when a transport cannot send or receive data."""

