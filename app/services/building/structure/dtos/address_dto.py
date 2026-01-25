from typing import Optional

from app.services.contracts.dto import MongoModel
from pydantic import Field, BaseModel
from typing import Dict, Tuple, Union, List

# GeoPoint 타입: 경도와 위도로 이루어진 좌표 튜플
GeoPoint = Tuple[float, float]

# GeoPolygon 타입: 외곽선과 내부 다각형이 포함된 리스트로 구성, 각 좌표는 (float, float) 튜플
GeoPolygon = List[List[GeoPoint]]

# GeoMultiPolygon 타입: 여러 개의 다각형을 포함하는 리스트
GeoMultiPolygon = List[GeoPolygon]

# GeoJSON 타입: GeoJSON 객체의 구조를 정의, 다양한 타입의 지오메트리를 포함
GeoJSONType = Dict[str, Union[str, GeoPoint, GeoPolygon, GeoMultiPolygon]]

# 명확한 GeoJSON 타입 정의
GeoJSONPointType = Dict[str, Union[str, GeoPoint]]  # 점 형태의 GeoJSON
GeoJSONPolygonType = Dict[str, Union[str, GeoPolygon]]  # 폴리곤 형태의 GeoJSON
GeoJSONMultiPolygonType = Dict[str, Union[str, GeoMultiPolygon]]  # 멀티폴리곤 형태의 GeoJSON


class BlockAddressDto(BaseModel):
    pnu: str = Field(None, title='필지 고유 식별 번호 (PNU)')
    township: Optional[str] = Field(None, title='읍/면/동 코드 8자리')
    township_name: Optional[str] = Field(None, title='읍/면/동 이름')

    village: Optional[str] = Field(None, title='리 코드 10자리')
    village_name: Optional[str] = Field(None, title='리 이름')

    display_boundary_address: str = Field(title='전체 행정구역 주소 문자열')
    display_boundary_short_address: str = Field(title='전체 행정구역 짧은 주소 문자열')
    is_representative: bool = Field(True, title='이 주소가 대표주소인지')
    sort_number: int = Field(title='순서')

    is_mountain: bool = Field(False, title='산 여부 (land_type이 1이면 True)')
    block_main: Optional[str] = Field(None, title='본번 (예: 437)')
    block_sub: Optional[str] = Field(None, title='부번 (예: 10)')
    display_block: str = Field(title='법정동과 하위 지번주소')
    display_block_address: str = Field(title='전체 지번 주소 문자열')
    display_block_short_address: str = Field(title='전체 지번 짧은 주소 문자열')

class AddressDto(MongoModel):
    address_id: str = Field(title='유니크 아이디 road_code_id + building_manage_number')
    building_manage_number: str = Field(None, title='건물관리번호 (25자리, bdMgtSn)')
    road_code_id: str = Field(title='도로명 코드')
    address_name: Optional[str] = Field(None, title='주소 이름')
    display_address_name: str = Field(None, title='주소 표기 이름')

    state: str = Field(title='시/도 코드 2자리')
    state_name: str = Field(title='시/도 이름')
    state_short_name: str = Field(title='시/도 짧은 이름')

    district: Optional[str] = Field(None, title='시/군/구 코드 5자리')
    district_name: Optional[str] = Field(None, title='시/군/구 이름')

    township_admin: Optional[str] = Field(None, title='행정동 읍/면/동 코드 8자리')
    township_admin_name: Optional[str] = Field(None, title='행정동 이름 (예: 교남동)')
    zip_code: Optional[str] = Field(None, title='우편번호 5자리')
    is_apartment: bool = Field('아파트 여부')

    main_block: BlockAddressDto = Field(title='메인 지번')
    related_blocks: List[BlockAddressDto] = Field(title='지번 목록들')

    # --- 도로명 주소 상세 (Road Name) ---
    road_name_code: Optional[str] = Field(None, title='도로명코드 (naRoadCd)')
    road_name: Optional[str] = Field(None, title='도로명')
    road_main: Optional[str] = Field(None, title='도로명 본번')
    road_sub: Optional[str] = Field(None, title='도로명 부번')
    display_road: str = Field(title='도로명과 하위 주소')
    display_road_address: str = Field(title='전체 도로명 주소 문자열')
    display_road_short_address: str = Field(title='전체 도로명 짧은 주소 문자열')
    display_road_include_address: str = Field(title='전체 도로명 주소 법정동 포함 문자열')
    display_road_include_short_address: str = Field(title='전체 도로명 주소 법정동 포함 짧은 문자열')

    latitude: Optional[float] = Field(None, title='위도')
    longitude: Optional[float] = Field(None, title='경도')
    geo_point: GeoJSONType = Field(None, title='geoJson Point')
    geometry: GeoJSONType = Field(None, title='geoJson Geometry')
