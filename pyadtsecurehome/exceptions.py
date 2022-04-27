"""PyAdtSecureHome Exceptions."""


class PyAdtSecureHomeError(Exception):
    """ADT Secure Home api exception."""


class InvalidURL(PyAdtSecureHomeError):
    """Invalid url exception."""


class HTTPError(PyAdtSecureHomeError):
    """Invalid host exception."""
