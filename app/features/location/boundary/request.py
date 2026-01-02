from typing import Optional, Literal
from pydantic import BaseModel, root_validator, Field

from app.services.location.boundary.dto import BoundaryItemDto, BoundaryPaginationDto
from app.services.location.boundary.types.boundary import LEGAL, STATE, DISTRICT, TOWNSHIP, VILLAGE


class BoundaryRequest(BaseModel):
    """
    경계 정보를 조회할 때 사용되는 기본 파라미터 모델입니다.
    """
    item_code: Optional[str] = Field(None, title='지역 코드', example='11530102')
    item_name: Optional[str] = Field(None, title='지역 이름', example='구로동')
    state_code: Optional[str] = Field(None, title='시/도 코드', example='11')
    district_code: Optional[str] = Field(None, title='시/군/구 코드', example='11530')
    township_code: Optional[str] = Field(None, title='읍/면/동 코드', example='11530102')
    village_code: Optional[str] = Field(None, title='리 코드', example='1153010200')
    location_type: Optional[Literal[STATE, DISTRICT, TOWNSHIP, VILLAGE]] = Field(None, title='지역 구분', example=TOWNSHIP)
    jurisdiction_type: Optional[Literal[LEGAL]] = Field(None, title='법정/행정 구분', example=LEGAL)
    latitude: Optional[float] = Field(None, title='위도', example=37.49425480498678)
    longitude: Optional[float] = Field(None, title='경도', example=126.88468703854274)
    use_polygon: Optional[int] = Field(0, title='폴리곤 반환 여부', example=False)

    @root_validator
    def check_latitude_longitude(cls, values):
        """
        위도(latitude)와 경도(longitude) 값의 유효성을 검사합니다.

        위도와 경도 중 하나만 있는 경우 에러를 발생시킵니다.

        Args:
            values (dict): 모델의 필드 값들을 포함하는 딕셔너리입니다.

        Raises:
            ValueError: 위도와 경도가 둘 중 하나만 제공된 경우 에러가 발생합니다.

        Returns:
            dict: 유효성 검사를 통과한 값들을 반환합니다.
        """
        latitude = values.get('latitude')
        longitude = values.get('longitude')

        # 위도와 경도 중 하나만 제공된 경우 오류 발생
        if (latitude is not None and longitude is None) or (latitude is None and longitude is not None):
            raise ValueError('latitude와 longitude는 둘 다 있어야 합니다. 하나만 있을 수 없습니다.')

        return values


class BoundariesRequest(BoundaryRequest):
    """
    페이징 처리가 필요한 경계 정보 조회 파라미터 모델입니다.

    BoundaryRequest 에 페이징 필드를 추가로 제공합니다.
    """
    page: Optional[int] = Field(1, title='페이지 번호', example=1, ge=1)
    per_page: Optional[int] = Field(10, title='페이지 수량', example=10, ge=1, le=10000)


__all__ = ['BoundaryRequest', 'BoundariesRequest']