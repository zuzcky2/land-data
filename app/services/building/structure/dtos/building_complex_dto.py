from typing import Optional

from app.services.contracts.dto import MongoModel
from pydantic import Field, BaseModel
from typing import Dict, Tuple, Union

# GeoPoint 타입: 경도와 위도로 이루어진 좌표 튜플
GeoPoint = Tuple[float, float]
GeoJSONPointType = Dict[str, Union[str, GeoPoint]]  # 점 형태의 GeoJSON

class AddressDto(MongoModel):
    pnu: str = Field(None, title='필지 고유 식별 번호 (PNU)')
    building_manage_number: str = Field(None, title='건물관리번호 (25자리, bdMgtSn)')

    state: str = Field(title='시/도 코드 2자리')
    state_name: str = Field(title='시/도 이름')
    state_short_name: str = Field(title='시/도 짧은 이름')
    state_boundary_code: str = Field(title='boundary location_type: state 의 item_code')

    district: Optional[str] = Field(None, title='시/군/구 코드 5자리')
    district_name: Optional[str] = Field(None, title='시/군/구 이름')
    district_boundary_code: Optional[str] = Field(None, title='boundary location_type: district 의 item_code')

    township: Optional[str] = Field(None, title='읍/면/동 코드 8자리')
    township_name: Optional[str] = Field(None, title='읍/면/동 이름')
    township_boundary_code: Optional[str] = Field(None, title='boundary location_type: township 의 item_code')

    village: Optional[str] = Field(None, title='리 코드 10자리')
    village_name: Optional[str] = Field(None, title='리 이름')
    village_boundary_code: str = Field(None, title='boundary location_type: village 의 item_code')

    township_admin: Optional[str] = Field(None, title='행정동 읍/면/동 코드 8자리')
    township_admin_name: Optional[str] = Field(None, title='행정동 이름 (예: 교남동)')
    zip_code: Optional[str] = Field(None, title='우편번호 5자리')

    display_boundary_address: str = Field(title='전체 행정구역 주소 문자열')
    display_boundary_short_address: str = Field(title='전체 행정구역 짧은 주소 문자열')

    # --- 지번 주소 상세 (Lot Number) ---
    land_type: int = Field(0, title='대지구분코드 (0:대지, 1:산, 2:기타)')
    is_mountain: bool = Field(False, title='산 여부 (land_type이 1이면 True)')
    block_main: Optional[int] = Field(None, title='본번 (예: 437)')
    block_sub: Optional[int] = Field(None, title='부번 (예: 10)')
    display_block_address: str = Field(title='전체 지번 주소 문자열')
    display_block_short_address: str = Field(title='전체 지번 짧은 주소 문자열')
    related_blocks: list = Field([], title='연결되는 지번 검색어')

    # --- 도로명 주소 상세 (Road Name) ---
    road_name_code: Optional[str] = Field(None, title='도로명코드 (naRoadCd)')
    road_name: Optional[str] = Field(None, title='도로명')
    road_main: Optional[int] = Field(None, title='도로명 본번')
    road_sub: Optional[int] = Field(None, title='도로명 부번')
    display_road_address: str = Field(title='전체 도로명 주소 문자열')
    display_road_short_address: str = Field(title='전체 도로명 짧은 주소 문자열')

    latitude: float = Field(title='위도')
    longitude: float = Field(title='경도')
    geo_point: GeoJSONPointType = Field(title='geoJson 포인트')




class BuildingComplexDto(MongoModel):
    dgk_id: str = Field(title='건축물대장 ID')