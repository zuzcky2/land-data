from dataclasses import dataclass
from dependency_injector.wiring import Provide, inject
from app.services.building.raw.container import RawContainer
from app.services.building.raw.services.address_info_service import AddressInfoService
from app.services.building.raw.services.area_info_service import AreaInfoService
from app.services.building.raw.services.basic_info_service import BasicInfoService
from app.services.building.raw.services.group_info_service import GroupInfoService
from app.services.building.raw.services.kapt_basic_service import KaptBasicService
from app.services.building.raw.services.kapt_detail_service import KaptDetailService
from app.services.building.raw.services.kapt_list_service import KaptListService
from app.services.building.raw.services.price_info_service import PriceInfoService
from app.services.building.raw.services.relation_info_service import RelationInfoService
from app.services.building.raw.services.title_info_service import TitleInfoService
from app.services.building.raw.services.floor_info_service import FloorInfoService
from app.core.service.service_cache import get_service_with_cache
from app.services.building.raw.services.zone_info_service import ZoneInfoService


@dataclass
class RawFacade:
    group_info_service: GroupInfoService
    title_info_service: TitleInfoService
    basic_info_service: BasicInfoService
    floor_info_service: FloorInfoService
    area_info_service: AreaInfoService
    price_info_service: PriceInfoService
    address_info_service: AddressInfoService
    relation_info_service: RelationInfoService
    zone_info_service: ZoneInfoService
    kapt_list_service: KaptListService
    kapt_basic_service: KaptBasicService
    kapt_detail_service: KaptDetailService

@inject
def get_service(
    _group_info_service: GroupInfoService = Provide[RawContainer.group_info_service],
    _title_info_service: TitleInfoService = Provide[RawContainer.title_info_service],
    _basic_info_service: BasicInfoService = Provide[RawContainer.basic_info_service],
    _floor_info_service: FloorInfoService = Provide[RawContainer.floor_info_service],
    _area_info_service: AreaInfoService = Provide[RawContainer.area_info_service],
    _price_info_service: PriceInfoService = Provide[RawContainer.price_info_service],
    _address_info_service: AddressInfoService = Provide[RawContainer.address_info_service],
    _relation_info_service: RelationInfoService = Provide[RawContainer.relation_info_service],
    _zone_info_service: ZoneInfoService = Provide[RawContainer.zone_info_service],
    _kapt_list_service: KaptListService = Provide[RawContainer.kapt_list_service],
    _kapt_basic_service: KaptBasicService = Provide[RawContainer.kapt_basic_service],
    _kapt_detail_service: KaptDetailService = Provide[RawContainer.kapt_detail_service],
) -> RawFacade:
    return RawFacade(
        group_info_service=_group_info_service,
        title_info_service=_title_info_service,
        basic_info_service=_basic_info_service,
        floor_info_service=_floor_info_service,
        area_info_service=_area_info_service,
        price_info_service=_price_info_service,
        address_info_service=_address_info_service,
        relation_info_service=_relation_info_service,
        zone_info_service=_zone_info_service,
        kapt_list_service=_kapt_list_service,
        kapt_basic_service=_kapt_basic_service,
        kapt_detail_service=_kapt_detail_service,
    )

# 의존성 주입을 위한 Container 인스턴스 생성
application = RawContainer()

# 컨테이너의 구성 요소를 현재 모듈에 와이어링
application.wire(modules=[__name__])

facade: RawFacade = get_service_with_cache('building_raw', get_service)


# 외부로 노출할 변수들을 지정합니다.
__all__ = ['facade']