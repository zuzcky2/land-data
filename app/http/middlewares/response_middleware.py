"""결과 래핑 미들웨어 모듈.

HTTP 요청과 응답을 가로채서 일관된 응답 형식을 제공하거나
추가적인 메타데이터를 포함하는 미들웨어입니다.
"""

from typing import Callable, Awaitable, Dict, Any
import time
import uuid

from fastapi import Request
from starlette.responses import Response, JSONResponse


async def result_wrapper_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """
    모든 HTTP 요청을 래핑하여 일관된 응답 형식과 메타데이터를 제공하는 미들웨어입니다.

    이 미들웨어는 다음과 같은 기능을 제공합니다:
    - 요청 처리 시간 측정
    - 고유한 요청 ID 생성 및 헤더 추가
    - 향후 응답 형식 표준화 확장 가능

    Args:
        request (Request): 클라이언트로부터 받은 HTTP 요청 객체
        call_next (Callable[[Request], Awaitable[Response]]):
            다음 미들웨어 또는 엔드포인트를 호출하는 함수

    Returns:
        Response: 메타데이터가 추가된 HTTP 응답 객체

    Note:
        현재는 기본적인 메타데이터만 추가하지만,
        향후 응답 형식 표준화나 추가 기능을 쉽게 확장할 수 있습니다.
        에러 응답(4xx, 5xx)은 수정하지 않고 그대로 통과시킵니다.
    """
    # 요청 시작 시간 기록
    start_time: float = time.time()

    # 고유한 요청 ID 생성 (트레이싱 및 로깅용)
    request_id: str = str(uuid.uuid4())

    try:
        # 요청을 다음 미들웨어 또는 엔드포인트로 전달하여 응답 획득
        response: Response = await call_next(request)

        # 요청 처리 시간 계산
        process_time: float = time.time() - start_time

        # 응답 헤더에 메타데이터 추가 (모든 응답에 적용)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(round(process_time, 4))

        return response

    except Exception as e:
        # 예외가 발생한 경우에도 메타데이터 추가
        process_time: float = time.time() - start_time

        # 예외를 다시 발생시켜 ExceptionLoggingMiddleware가 처리하도록 함
        raise


async def api_response_wrapper_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """
    API 응답을 일관된 형식으로 래핑하는 미들웨어입니다.

    모든 성공적인 JSON 응답을 표준화된 형태로 변환합니다:
    {
        "success": true,
        "data": {...},
        "metadata": {
            "request_id": "...",
            "timestamp": "...",
            "process_time": "..."
        }
    }

    Args:
        request (Request): HTTP 요청 객체
        call_next (Callable[[Request], Awaitable[Response]]): 다음 호출 함수

    Returns:
        Response: 표준화된 형식의 HTTP 응답 객체

    Note:
        에러 응답(4xx, 5xx)이나 비JSON 응답은 래핑하지 않습니다.
    """
    start_time: float = time.time()
    request_id: str = str(uuid.uuid4())

    response: Response = await call_next(request)
    process_time: float = time.time() - start_time

    # 에러 응답(4xx, 5xx)은 래핑하지 않고 메타데이터만 추가
    if response.status_code >= 400:
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(round(process_time, 4))
        return response

    # JSON 응답이고 성공 상태 코드인 경우에만 래핑
    if (isinstance(response, JSONResponse) and
            200 <= response.status_code < 300):
        # 기존 응답 내용을 data 필드로 래핑
        original_content: Dict[str, Any] = response.body.decode()

        wrapped_content: Dict[str, Any] = {
            "success": True,
            "data": original_content,
            "metadata": {
                "request_id": request_id,
                "timestamp": time.time(),
                "process_time": round(process_time, 4),
                "path": str(request.url.path),
                "method": request.method
            }
        }

        # 새로운 JSONResponse 생성
        response = JSONResponse(
            content=wrapped_content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )

    # 기본 메타데이터 헤더 추가
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(round(process_time, 4))

    return response


async def cors_and_security_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """
    CORS 및 보안 헤더를 추가하는 미들웨어입니다.

    모든 응답에 보안 관련 헤더를 추가하여 웹 보안을 강화합니다.

    Args:
        request (Request): HTTP 요청 객체
        call_next (Callable[[Request], Awaitable[Response]]): 다음 호출 함수

    Returns:
        Response: 보안 헤더가 추가된 HTTP 응답 객체
    """
    response: Response = await call_next(request)

    # 보안 헤더 추가
    security_headers: Dict[str, str] = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Content-Security-Policy": "default-src 'self'",
    }

    for header_name, header_value in security_headers.items():
        response.headers[header_name] = header_value

    return response


__all__ = [
    'result_wrapper_middleware',
    'api_response_wrapper_middleware',
    'cors_and_security_middleware'
]