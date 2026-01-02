from pydantic import BaseModel, Field

from typing import Generic, TypeVar, Optional, Any

T = TypeVar("T")

class ResponseDto(BaseModel, Generic[T]):
    result: bool = Field(True, title='응답 성공 여부')
    message: str = Field('요청에 성공했습니다.', title='응답 메세지')
    data: Optional[T] = Field(None, title='응답 데이터')
    error: Optional[Any] = Field(None, title='에러 데이터')

__all__=['ResponseDto']