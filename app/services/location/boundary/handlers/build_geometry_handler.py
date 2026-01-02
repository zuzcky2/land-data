from typing import Union, Tuple
from shapely.geometry import mapping, shape, Polygon, MultiPolygon
from app.services.location.boundary.types.boundary import GeoJSONType


class BuildGeometryHandler:
    """
    geometry 데이터를 가공하여 geoJson을 만듭니다.
    """

    def build_geometry(self, geometry: Union[Polygon, MultiPolygon]) -> Tuple[list, GeoJSONType, GeoJSONType]:
        geometry = shape(self.item['geometry'])
        geo_point = None
        bbox = []

        if isinstance(geometry, (Polygon, MultiPolygon)):
            # 잘못된 다각형 수정
            geometry = self.fix_invalid_polygon(geometry)
            # 중복된 좌표 제거
            geometry = self.process_geometry(geometry)
            # GeoJSON 형식으로 좌표 변환
            geo_point = mapping(geometry.centroid)
            bbox = geometry.bounds
            geometry = mapping(geometry)

        return bbox, geo_point, geometry


    def process_geometry(self, geometry: Union[Polygon, MultiPolygon]) -> Union[Polygon, MultiPolygon]:
        """
        주어진 다각형의 중복 좌표를 제거하고, 필요한 경우 MultiPolygon을 처리합니다.

        Args:
            geometry (Union[Polygon, MultiPolygon]): 입력 다각형.

        Returns:
            Union[Polygon, MultiPolygon]: 중복 좌표가 제거된 다각형.
        """
        if isinstance(geometry, MultiPolygon):
            new_polygons = []
            for polygon in geometry.geoms:
                # 개별 Polygon에서 중복 좌표 제거
                coords = self.remove_duplicate_vertices(polygon.exterior.coords)
                new_polygons.append(Polygon(coords))
            geometry = MultiPolygon(new_polygons)
        elif isinstance(geometry, Polygon):
            coords = self.remove_duplicate_vertices(geometry.exterior.coords)
            geometry = Polygon(coords)

        return geometry

    def fix_invalid_polygon(self, polygon: Union[Polygon, MultiPolygon]) -> Union[Polygon, MultiPolygon]:
        """
        잘못된 형식의 다각형을 수정합니다.

        Args:
            polygon (Union[Polygon, MultiPolygon]): 수정할 다각형.

        Returns:
            Union[Polygon, MultiPolygon]: 수정된 다각형.
        """
        return polygon.buffer(0) if not polygon.is_valid else polygon

    def remove_duplicate_vertices(self, coords: Union[list, tuple]) -> list:
        """
        다각형의 중복 좌표를 제거합니다.

        Args:
            coords (Union[list, tuple]): 중복 좌표를 포함하는 좌표 리스트.

        Returns:
            list: 중복이 제거된 좌표 리스트.
        """
        filtered_coords = []
        for coord in coords:
            if not filtered_coords or filtered_coords[-1] != coord:
                filtered_coords.append(coord)
        return filtered_coords

__all__ = ['BuildGeometryHandler']