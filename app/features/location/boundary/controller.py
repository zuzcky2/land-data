from app.features.contracts.controller import Controller
from app.features.location.boundary.request import BoundariesRequest, BoundaryRequest
from app.features.location.boundary.response import BoundariesResponse, BoundaryResponse
from typing import Optional
from app.services.location.boundary import facade as boundary


class BoundaryController(Controller):
    """
    경계 데이터를 처리하는 클래스입니다.
    Boundary 클래스는 경계 정보에 대한 조회 기능을 제공합니다.
    """

    def index(self, params: BoundariesRequest) -> BoundariesResponse:
        """
        여러 경계 데이터를 조회합니다.
        """
        # 페이징 및 필터링 조건에 따라 경계 데이터를 조회하여 반환
        return boundary.service.get_boundaries(params.dict(), driver_name='mongodb')

    def show(self, params: BoundaryRequest) -> Optional[BoundaryResponse]:
        """
        단일 경계 데이터를 조회합니다.
        """
        # 필터링 조건에 따라 단일 경계 데이터를 조회하여 반환
        return boundary.service.get_boundary(params.dict(), driver_name='mongodb')


__all__ = ['BoundaryController']
