from __future__ import annotations


class AppError(Exception):
    """Application error that can be rendered as a stable JSON response."""

    def __init__(self, status_code: int, msg: str, code: int | None = None):
        super().__init__(msg)
        self.status_code = status_code
        self.msg = msg
        self.code = code or status_code

