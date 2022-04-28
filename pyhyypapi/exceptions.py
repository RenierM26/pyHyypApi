"""Hyyp Api Exceptions."""


class HyypApiError(Exception):
    """ADT Secure Home api exception."""


class InvalidURL(HyypApiError):
    """Invalid url exception."""


class HTTPError(HyypApiError):
    """Invalid host exception."""
