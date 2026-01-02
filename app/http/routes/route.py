"""메인 FastAPI 라우터 모듈.

FastAPI 애플리케이션의 생성, 설정, 라우팅을 담당하는 메인 모듈입니다.
- 애플리케이션 부트스트랩 및 초기화
- 미들웨어 설정 (CORS, 에러 처리, 응답 래핑)
- 예외 핸들러 설정 (HTTPException, 커스텀 예외)
- 라우터 등록 및 기본 엔드포인트 제공
- 설정 기반 동적 구성
"""

import logging
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_redoc_html
from starlette.middleware.cors import CORSMiddleware

from app.http.middlewares.response_middleware import result_wrapper_middleware
from app.configs.api import configs as api_configs
from app.core.helpers.log import Log

# API 전용 로거 설정
logger: logging.Logger = Log.get_logger('api')


def initialize_application() -> None:
    """
    애플리케이션을 초기화합니다.

    DI 컨테이너 부트스트랩을 수행하고 필요한 서비스들을 준비합니다.
    이미 초기화된 경우 중복 초기화를 방지합니다.

    Raises:
        Exception: 부트스트랩 과정에서 오류가 발생한 경우
    """
    logger.info("🔄 FastAPI 애플리케이션 초기화 시작")

    try:
        from app.bootstrap import bootstrap, is_initialized

        # 이미 초기화된 경우 스킵
        if is_initialized():
            logger.info("⏭️ 애플리케이션이 이미 초기화되어 있습니다")
            return

        # DI 컨테이너 부트스트랩 실행
        bootstrap()
        logger.info("✅ DI 컨테이너 부트스트랩 완료")

    except Exception as e:
        logger.error(f"❌ 애플리케이션 초기화 실패: {e}")
        raise


def setup_exception_handlers(app: FastAPI) -> None:
    """
    예외 핸들러들을 설정합니다.

    HTTPException과 기타 특정 예외들에 대한 커스텀 핸들러를 등록합니다.
    각 예외는 로깅되고 클라이언트에게 적절한 응답이 반환됩니다.

    Args:
        app (FastAPI): 예외 핸들러를 등록할 FastAPI 애플리케이션 인스턴스
    """

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, e: HTTPException) -> JSONResponse:
        """
        HTTPException 전용 핸들러입니다.

        FastAPI의 HTTPException(404, 403, 401 등)을 처리하고
        로깅 후 적절한 JSON 응답을 반환합니다.

        Args:
            request (Request): HTTP 요청 객체
            exc (HTTPException): 발생한 HTTP 예외

        Returns:
            JSONResponse: 에러 정보를 포함한 JSON 응답
        """
        # 예외 정보 추출

        message = e.detail if hasattr(e, 'detail') else None
        status_code = e.status_code if hasattr(e, 'status_code') else 500
        data = e.data if hasattr(e, 'data') else None
        logging = e.logging if hasattr(e, 'logging') else None

        if logging is True:
            # HTTP 요청과 함께 예외 로그 기록
            await Log.log_http_error(e, request)

        # 클라이언트에게 안전한 에러 응답 반환
        return JSONResponse(
            status_code=status_code,
            content={
                "message": message,
                "data": data,
                "type": 'http_exception'
            }
        )

    logger.info("✅ HTTPException 핸들러 설정 완료")


def setup_basic_routes(app: FastAPI) -> None:
    """
    기본 라우트들을 설정합니다.

    헬스 체크, 기본 정보 등 시스템 운영에 필요한 기본 엔드포인트들을 등록합니다.

    Args:
        app (FastAPI): 라우트를 등록할 FastAPI 애플리케이션 인스턴스
    """

    @app.get('/', tags=["기본"])
    def root() -> Dict[str, str]:
        """
        API 루트 엔드포인트입니다.

        Returns:
            Dict[str, str]: 기본 응답 메시지와 상태 정보
        """
        return {
            'message': 'Search 서버가 정상 작동 중입니다.',
            'status': 'running',
            'version': api_configs['version']
        }

    @app.get('/health', tags=["모니터링"])
    def health_check() -> Dict[str, str]:
        """
        헬스 체크 엔드포인트입니다.

        로드 밸런서나 모니터링 시스템에서 서버 상태를 확인하는 데 사용됩니다.

        Returns:
            Dict[str, str]: 서버 상태 정보
        """
        return {
            "status": "healthy",
            "message": "API 서버가 정상적으로 동작 중입니다",
            "service": api_configs['title']
        }


def setup_middlewares(app: FastAPI) -> None:
    """
    애플리케이션 미들웨어들을 설정합니다.

    CORS, 에러 처리, 응답 래핑 등의 미들웨어를 순서대로 등록합니다.
    미들웨어는 등록 순서의 역순으로 실행됩니다.

    Args:
        app (FastAPI): 미들웨어를 등록할 FastAPI 애플리케이션 인스턴스
    """
    # CORS 미들웨어 설정 (가장 먼저 처리되어야 함)
    cors_settings: Dict[str, Any] = _get_cors_settings()
    app.add_middleware(CORSMiddleware, **cors_settings)
    logger.info("✅ CORS 미들웨어 설정 완료")

    # 응답 래핑 미들웨어 (응답 형식 통일)
    app.middleware('http')(result_wrapper_middleware)
    logger.info("✅ 응답 래핑 미들웨어 설정 완료")


def _get_cors_settings() -> Dict[str, Any]:
    """
    CORS 설정을 반환합니다.

    환경변수나 설정 파일에서 CORS 관련 설정을 로드하거나
    개발 환경에 적합한 기본 설정을 제공합니다.

    Returns:
        Dict[str, Any]: CORS 미들웨어 설정 딕셔너리
    """
    # 개발 환경 기본 설정 (운영환경에서는 더 제한적으로 설정해야 함)
    return {
        "allow_origins": ["*"],  # 개발환경용, 운영시에는 특정 도메인만 허용
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": ["*"],
    }


def setup_service_routers(app: FastAPI) -> None:
    """
    서비스별 라우터들을 등록합니다.

    각 서비스 모듈에서 제공하는 라우터들을 FastAPI 애플리케이션에 등록합니다.
    라우터 로딩에 실패해도 애플리케이션은 계속 실행됩니다.

    Args:
        app (FastAPI): 라우터를 등록할 FastAPI 애플리케이션 인스턴스
    """
    # Geometry Boundary 서비스 라우터 등록
    try:
        from app.features.location.route import router as boundary_router
        app.include_router(
            boundary_router,
            prefix="/api",  # API 버전 관리
            tags=["지역경계"]
        )
        logger.info("✅ Boundary 서비스 라우터 등록 완료")

        # 2. 커스텀 Redoc 경로를 직접 정의합니다.
        @app.get("/redoc", include_in_schema=False)
        async def custom_redoc_html():
            return get_redoc_html(
                openapi_url=app.openapi_url,
                title=app.title + " - ReDoc",
                # 404가 뜨는 @next 대신 안정적인 버전으로 교체합니다.
                redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js",
            )
        
    except ImportError as e:
        logger.warning(f"⚠️ 라우터 로딩 실패: {e}")
    except Exception as e:
        logger.error(f"❌ 라우터 등록 중 오류: {e}", exc_info=True)

    # 향후 추가될 다른 서비스 라우터들:
    # - User 관리 라우터
    # - 인증/인가 라우터
    # - 파일 업로드 라우터
    # - 외부 API 프록시 라우터


def create_app() -> FastAPI:
    """
    FastAPI 애플리케이션을 생성하고 모든 설정을 적용합니다.

    애플리케이션 초기화부터 라우터 등록까지 전체 설정 과정을 수행합니다.

    Returns:
        FastAPI: 완전히 설정된 FastAPI 애플리케이션 인스턴스

    Raises:
        Exception: 애플리케이션 생성 과정에서 치명적인 오류가 발생한 경우
    """
    try:
        # 1. 애플리케이션 초기화 (DI 컨테이너 부트스트랩)
        initialize_application()

        # 2. FastAPI 인스턴스 생성
        app: FastAPI = FastAPI(
            title=api_configs['title'],
            description=api_configs['description'],
            version=api_configs['version'],
            root_path=api_configs['root_path'],
            openapi_url=api_configs['openapi_url'],
            redoc_url=api_configs['redoc_url'],
            docs_url="/docs",  # Swagger UI 경로

        )

        # 3. 예외 핸들러 설정 (미들웨어보다 먼저!)
        setup_exception_handlers(app)

        # 4. 기본 라우트 설정
        setup_basic_routes(app)

        # 5. 미들웨어 설정
        setup_middlewares(app)

        # 6. 서비스 라우터 등록
        setup_service_routers(app)

        logger.info("🚀 FastAPI 애플리케이션 생성 및 설정 완료")
        return app

    except Exception as e:
        logger.error(f"❌ FastAPI 애플리케이션 생성 실패: {e}")
        raise


# FastAPI 애플리케이션 인스턴스 생성
# 이 인스턴스는 ASGI 서버(uvicorn)에서 사용됩니다
route: FastAPI = create_app()

__all__ = ['route', 'create_app']