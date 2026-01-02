"""Boundary 서비스 라우터."""

from fastapi import APIRouter, Depends, HTTPException
from app.features.location.boundary.response import BoundaryResponse, BoundariesResponse
from app.features.location.boundary.request import BoundaryRequest, BoundariesRequest
from app.features.contracts.response import ResponseDto
from app.features.location.boundary.controller import BoundaryController

# APIRouter 인스턴스 생성
router = APIRouter(
    prefix="/location"
)

boundary_controller = BoundaryController()

@router.get('/boundaries', response_model=ResponseDto[BoundariesResponse])
def get_boundaries(params: BoundariesRequest = Depends()) -> ResponseDto:
    """
    여러 지역의 경계 데이터를 조회하는 엔드포인트.

    Args:
        params (BoundaryFetchPagingParams): 페이징 및 필터링에 필요한 파라미터.

    Returns:
        ResponseFetchDto: 조회 결과를 포함한 응답 객체.
    """
    try:
        # Boundary facade를 통해 컨트롤러 접근
        data = boundary_controller.index(params)
        print(data)
        return ResponseDto(data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/boundary', response_model=ResponseDto[BoundaryResponse])
def get_boundary(params: BoundaryRequest = Depends()) -> ResponseDto:
    """
    단일 지역의 경계 데이터를 조회하는 엔드포인트.

    Args:
        params (BoundaryFetchParams): 지역 코드를 포함한 조회 파라미터.

    Returns:
        ResponseFetchItemDto: 조회 결과를 포함한 응답 객체.
    """
    try:
        # Boundary facade를 통해 컨트롤러 접근
        data = boundary_controller.show(params)
        return ResponseDto(data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 외부 모듈에서 접근할 수 있는 router 객체
__all__ = ['router']