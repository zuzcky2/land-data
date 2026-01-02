from typing import TypedDict, Literal, Optional, Tuple, List, Dict, Union

# 구역 및 위치 유형 상수 정의
LEGAL: str = 'legal'  # 법정 구역
STATE: str = 'state'  # 시도
DISTRICT: str = 'district'  # 시군구
TOWNSHIP: str = 'township'  # 읍면동
VILLAGE: str = 'village'  # 리

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

