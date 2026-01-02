from typing import Optional, List, Any
from app.services.location.boundary.manager import BoundaryManager
from app.services.location.boundary.dto import BoundaryItemDto, BoundaryPaginationDto
from app.services.location.boundary.drivers.interface import BoundaryStoreResult


class BoundaryService:
    # 드라이버 이름을 상수로 관리하여 오타 방지
    DRIVER_MONGODB = 'mongodb'
    DRIVER_VWORLD = 'vworld'

    def __init__(self, boundary_manager: BoundaryManager):
        self.boundary_manager = boundary_manager

    def get_boundaries(self, params: dict, driver_name: Optional[str] = None) -> BoundaryPaginationDto:
        """
        다양한 드라이버를 통해 지역 경계 목록을 페이징 조회합니다.
        """
        page = int(params.get('page', 1))
        per_page = int(params.get('per_page', 20))

        driver = self.boundary_manager.driver(driver_name)

        return (
            driver.clear()
            .set_arguments(params)
            .set_pagination(page=page, per_page=per_page)
            .read()
        )

    def get_boundary(self, params: dict, driver_name: Optional[str] = None) -> Optional[BoundaryItemDto]:
        """
        단일 지역 경계 데이터를 조회합니다.
        """
        return (
            self.boundary_manager.driver(driver_name)
            .clear()
            .set_arguments(params)
            .read_one()
        )

    def store_boundaries(self, items: List[BoundaryItemDto], driver_name: Optional[str] = None) -> BoundaryStoreResult:
        """
        경계 데이터를 영구 저장소에 저장합니다.
        """
        # 저장 시에는 기본적으로 mongodb 드라이버를 사용하도록 지정 가능
        target_driver = driver_name or self.DRIVER_MONGODB
        return self.boundary_manager.driver(target_driver).store(items)

    def sync_from_vworld(self, location_type: str, page: int = 1, per_page: int = 100) -> Any:
        """
        [기본 싱크] 상위 데이터가 필요 없는 경우(STATE 등) 직접 VWorld에서 가져와 저장합니다.
        """
        vworld_result = (
            self.boundary_manager.driver(self.DRIVER_VWORLD)
            .clear()
            .set_arguments({'location_type': location_type})
            .set_pagination(page=page, per_page=per_page)
            .read()
        )

        if vworld_result.items:
            self.store_boundaries(vworld_result.items)

        return vworld_result.meta

    def sync_hierarchy(self, parent_type: str, current_type: str):
        """
        [계층 싱크] 상위 지역(parent_type) 코드를 기반으로 현재 지역(current_type)을 동기화합니다.
        """
        page = 1
        total_stored = 0

        while True:
            # [수정] params에 page를 명시적으로 전달해야 합니다.
            parent_pagination = self.get_boundaries(
                params={
                    'location_type': parent_type,
                    'page': page,
                    'per_page': 100  # 한 번에 많이 처리하도록 설정 권장
                },
                driver_name=self.DRIVER_MONGODB
            )

            # 더 이상 읽을 상위 데이터가 없거나 아이템이 비어있으면 종료
            if not parent_pagination.items:
                break

            for parent_item in parent_pagination.items:
                # VWorld 드라이버를 통해 하위 데이터 조회
                vworld_result = (
                    self.boundary_manager.driver(self.DRIVER_VWORLD)
                    .clear()
                    .set_arguments({
                        'location_type': current_type,
                        'item_code': parent_item.item_code,
                        'jurisdiction_type': 'legal'
                    })
                    .read()
                )

                if vworld_result.items:
                    self.store_boundaries(vworld_result.items)
                    total_stored += len(vworld_result.items)
                    print(f"  -> [{current_type}] {parent_item.item_name} 하위 데이터 {len(vworld_result.items)}개 동기화")

            # [핵심 수정] 마지막 페이지인지 체크하여 탈출 조건 강화
            if page >= parent_pagination.meta.last_page:
                break

            # 다음 페이지로 이동
            page += 1

        return total_stored