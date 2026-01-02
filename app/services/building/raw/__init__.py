from dataclasses import dataclass
from dependency_injector.wiring import Provide, inject
from app.services.building.raw.container import RawContainer
from app.services.building.raw.services.address_info_service import AddressInfoService
from app.services.building.raw.services.area_info_service import AreaInfoService
from app.services.building.raw.services.basic_info_service import BasicInfoService
from app.services.building.raw.services.price_info_service import PriceInfoService
from app.services.building.raw.services.title_info_service import TitleInfoService
from app.services.building.raw.services.floor_info_service import FloorInfoService
from app.core.service.service_cache import get_service_with_cache

@dataclass
class RawFacade:
    title_info_service: TitleInfoService
    basic_info_service: BasicInfoService
    floor_info_service: FloorInfoService
    area_info_service: AreaInfoService
    price_info_service: PriceInfoService
    address_info_service: AddressInfoService

@inject
def get_service(
    _title_info_service: TitleInfoService = Provide[RawContainer.title_info_service],
    _basic_info_service: BasicInfoService = Provide[RawContainer.basic_info_service],
    _floor_info_service: FloorInfoService = Provide[RawContainer.floor_info_service],
    _area_info_service: AreaInfoService = Provide[RawContainer.area_info_service],
    _price_info_service: PriceInfoService = Provide[RawContainer.price_info_service],
    _address_info_service: AddressInfoService = Provide[RawContainer.address_info_service],
) -> RawFacade:
    return RawFacade(
        title_info_service=_title_info_service,
        basic_info_service=_basic_info_service,
        floor_info_service=_floor_info_service,
        area_info_service=_area_info_service,
        price_info_service=_price_info_service,
        address_info_service=_address_info_service
    )

# 의존성 주입을 위한 Container 인스턴스 생성
application = RawContainer()

# 컨테이너의 구성 요소를 현재 모듈에 와이어링
application.wire(modules=[__name__])

facade: RawFacade = get_service_with_cache('building_raw', get_service)


# 외부로 노출할 변수들을 지정합니다.
__all__ = ['facade']