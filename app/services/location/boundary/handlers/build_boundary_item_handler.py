from app.services.location.boundary.dto import BoundaryItemDto
from app.services.location.boundary.handlers.build_geometry_handler import BuildGeometryHandler


class BuildBoundaryItemHandler(BuildGeometryHandler):
    """
    주어진 핸들러 입력 데이터를 처리하여 FetchItemDto 형식으로 변환하는 핸들러 클래스입니다.
    """

    item: dict
    result: dict

    def set_item(self, item: dict) -> 'BuildBoundaryItemHandler':
        """
        입력 데이터를 설정합니다.

        Args:
            item (HandlerInput): 변환할 입력 데이터.

        Returns:
            BuildFetchItemHandler: 자기 자신을 반환하여 메서드 체이닝을 지원합니다.
        """
        self.item = item
        return self

    def handle(self) -> 'BuildBoundaryItemHandler':
        """
        입력 데이터를 처리하여 필요한 필드와 형식으로 변환합니다.

        Returns:
            BuildFetchItemHandler: 변환된 결과를 가진 자신을 반환합니다.
        """
        item_full_code = self.item['item_code'].ljust(10, '0')

        bbox, geo_point, geometry = self.build_geometry(self.item['geometry'])

        # 변환된 데이터를 result에 저장
        self.result = {
            'id': None,
            'item_code': self.item['item_code'],
            'item_name': self.item['item_name'],
            'item_full_name': self.item['item_full_name'],
            'short_name': self.item['short_name'],
            'location_type': self.item['location_type'],
            'state_code': item_full_code[:2],
            'district_code': item_full_code[:5],
            'township_code': item_full_code[:8],
            'village_code': item_full_code,
            'jurisdiction_type': self.item['jurisdiction_type'],
            'bbox': bbox,
            'geo_point': geo_point,
            'geo_polygon': geometry,
            'last_updated_at': self.item['last_updated_at'],
            'manual_order': self.item['manual_order'],
        }

        return self

    def get(self) -> BoundaryItemDto:
        """
        변환된 결과를 FetchItemDto로 반환합니다.

        Returns:
            FetchItemDto: 변환된 데이터 DTO.
        """
        return BoundaryItemDto(**self.result)


__all__ = ['BuildBoundaryItemHandler']