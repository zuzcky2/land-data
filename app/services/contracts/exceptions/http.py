from fastapi import HTTPException
from typing import Any, Optional


class HttpException(HTTPException):
    status_code: 500
    detail: str
    data: Any
    logging: bool = True

    def __init__(self, status_code: Optional[int] = None, detail: Optional[str] = None, data: Optional[Any] = None) -> None:
        self.status_code = status_code or self.status_code
        self.detail = detail or self.detail
        self.data = data
        super().__init__(status_code=self.status_code, detail=self.detail)

class NotFoundException(HttpException):
    status_code = 404
    logging = False
    detail = '찾을 수 없습니다.'