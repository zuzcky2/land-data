from dataclasses import dataclass
from dependency_injector.wiring import Provide, inject
from app.services.location.raw.container import RawContainer
from app.core.service.service_cache import get_service_with_cache
from app.services.location.raw.services.address_db_download_service import AddressDBDownloadService
from app.services.location.raw.services.address_service import AddressService
from app.services.location.raw.services.block_address_service import BlockAddressService
from app.services.location.raw.services.building_group_service import BuildingGroupService
from app.services.location.raw.services.continuous_geometry_service import ContinuousGeometryService
from app.services.location.raw.services.point_geometry_service import PointGeometryService
from app.services.location.raw.services.road_address_service import RoadAddressService
from app.services.location.raw.services.road_code_service import RoadCodeService


@dataclass
class RawFacade:
    address_service: AddressService
    block_address_service: BlockAddressService
    road_address_service: RoadAddressService
    building_group_service: BuildingGroupService
    road_code_service: RoadCodeService
    address_db_service: AddressDBDownloadService
    continuous_geometry_service: ContinuousGeometryService
    point_geometry_service: PointGeometryService

@inject
def get_service(
    _address_service: AddressService = Provide[RawContainer.address_service],
    _block_address_service: BlockAddressService = Provide[RawContainer.block_address_service],
    _road_address_service: RoadAddressService = Provide[RawContainer.road_address_service],
    _building_group_service: BuildingGroupService = Provide[RawContainer.building_group_service],
    _road_code_service: RoadCodeService = Provide[RawContainer.road_code_service],
    _address_db_service: AddressDBDownloadService = Provide[RawContainer.address_db_service],
    _continuous_geometry_service: ContinuousGeometryService = Provide[RawContainer.continuous_geometry_service],
    _point_geometry_service: PointGeometryService = Provide[RawContainer.point_geometry_service],
) -> RawFacade:
    return RawFacade(
        address_service=_address_service,
        block_address_service=_block_address_service,
        road_address_service=_road_address_service,
        building_group_service=_building_group_service,
        road_code_service=_road_code_service,
        address_db_service=_address_db_service,
        continuous_geometry_service=_continuous_geometry_service,
        point_geometry_service=_point_geometry_service
    )

# 의존성 주입을 위한 Container 인스턴스 생성
application = RawContainer()

# 컨테이너의 구성 요소를 현재 모듈에 와이어링
application.wire(modules=[__name__])

facade: RawFacade = get_service_with_cache('location_raw', get_service)


# 외부로 노출할 변수들을 지정합니다.
__all__ = ['facade']