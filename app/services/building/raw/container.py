from app.core.packages.support.abstracts.abstract_container import AbstractContainer, providers
from app.services.building.raw.drivers.address_info.address_info_dgk import AddressInfoDgkDriver
from app.services.building.raw.drivers.address_info.address_info_mongodb import AddressInfoMongodbDriver
from app.services.building.raw.drivers.area_info.area_info_dgk import AreaInfoDgkDriver
from app.services.building.raw.drivers.area_info.area_info_mongodb import AreaInfoMongodbDriver
from app.services.building.raw.drivers.basic_info.basic_info_dgk import BasicInfoDgkDriver
from app.services.building.raw.drivers.basic_info.basic_info_mongodb import BasicInfoMongodbDriver
from app.services.building.raw.drivers.floor_info.floor_info_dgk import FloorInfoDgkDriver
from app.services.building.raw.drivers.floor_info.floor_info_mongodb import FloorInfoMongodbDriver
from app.services.building.raw.drivers.group_info.group_info_dgk import GroupInfoDgkDriver
from app.services.building.raw.drivers.group_info.group_info_mongodb import GroupInfoMongodbDriver
from app.services.building.raw.drivers.kapt_basic.kapt_basic_dgk_driver import KaptBasicDgkDriver
from app.services.building.raw.drivers.kapt_basic.kapt_basic_mongodb import KaptBasicMongodbDriver
from app.services.building.raw.drivers.kapt_detail.kapt_detail_dgk_driver import KaptDetailDgkDriver
from app.services.building.raw.drivers.kapt_detail.kapt_detail_mongodb import KaptDetailMongodbDriver
from app.services.building.raw.drivers.kapt_list.kapt_list_dgk_driver import KaptListDgkDriver
from app.services.building.raw.drivers.kapt_list.kapt_list_mongodb import KaptListMongodbDriver
from app.services.building.raw.drivers.price_info.price_info_dgk import PriceInfoDgkDriver
from app.services.building.raw.drivers.price_info.price_info_mongodb import PriceInfoMongodbDriver
from app.services.building.raw.drivers.relation_info.relation_info_dgk import RelationInfoDgkDriver
from app.services.building.raw.drivers.relation_info.relation_info_mongodb import RelationInfoMongodbDriver
from app.services.building.raw.drivers.title_info.title_info_dgk import TitleInfoDgkDriver
from app.services.building.raw.drivers.title_info.title_info_mongodb import TitleInfoMongodbDriver
from app.services.building.raw.drivers.zone_info.zone_info_dgk import ZoneInfoDgkDriver
from app.services.building.raw.drivers.zone_info.zone_info_mongodb import ZoneInfoMongodbDriver
from app.services.building.raw.managers.address_info_manager import AddressInfoManager
from app.services.building.raw.managers.area_info_manager import AreaInfoManager
from app.services.building.raw.managers.basic_info_manager import BasicInfoManager
from app.services.building.raw.managers.floor_info_manager import FloorInfoManager
from app.services.building.raw.managers.group_info_manager import GroupInfoManager
from app.services.building.raw.managers.kapt_basic_manager import KaptBasicManager
from app.services.building.raw.managers.kapt_detail_manager import KaptDetailManager
from app.services.building.raw.managers.kapt_list_manager import KaptListManager
from app.services.building.raw.managers.price_info_manager import PriceInfoManager
from app.services.building.raw.managers.relation_info_manager import RelationInfoManager
from app.services.building.raw.managers.title_info_manager import TitleInfoManager
from app.services.building.raw.managers.zone_info_manager import ZoneInfoManager
from app.services.building.raw.services.address_info_service import AddressInfoService
from app.services.building.raw.services.area_info_service import AreaInfoService
from app.services.building.raw.services.basic_info_service import BasicInfoService
from app.services.building.raw.services.floor_info_service import FloorInfoService
from app.services.building.raw.services.group_info_service import GroupInfoService
from app.services.building.raw.services.kapt_basic_service import KaptBasicService
from app.services.building.raw.services.kapt_detail_service import KaptDetailService
from app.services.building.raw.services.kapt_list_service import KaptListService
from app.services.building.raw.services.price_info_service import PriceInfoService
from app.services.building.raw.services.relation_info_service import RelationInfoService
from app.services.building.raw.services.title_info_service import TitleInfoService
from app.services.building.raw.services.zone_info_service import ZoneInfoService


class RawContainer(AbstractContainer):
    group_info_dgk_driver: GroupInfoDgkDriver = providers.Factory(GroupInfoDgkDriver)
    group_info_mongodb_driver: GroupInfoMongodbDriver = providers.Factory(GroupInfoMongodbDriver)
    group_info_manager: GroupInfoManager = providers.Singleton(
        GroupInfoManager,
        dgk_driver=group_info_dgk_driver,
        mongodb_driver=group_info_mongodb_driver,
    )
    group_info_service: GroupInfoService = providers.Singleton(GroupInfoService, manager=group_info_manager)

    title_info_dgk_driver: TitleInfoDgkDriver = providers.Factory(TitleInfoDgkDriver)
    title_info_mongodb_driver: TitleInfoMongodbDriver = providers.Factory(TitleInfoMongodbDriver)
    title_info_manager: TitleInfoManager = providers.Singleton(
        TitleInfoManager,
        dgk_driver=title_info_dgk_driver,
        mongodb_driver=title_info_mongodb_driver,
    )
    title_info_service: TitleInfoService = providers.Singleton(TitleInfoService, manager=title_info_manager)

    basic_info_dgk_driver: BasicInfoDgkDriver = providers.Factory(BasicInfoDgkDriver)
    basic_info_mongodb_driver: BasicInfoMongodbDriver = providers.Factory(BasicInfoMongodbDriver)
    basic_info_manager: BasicInfoManager = providers.Singleton(
        BasicInfoManager,
        dgk_driver=basic_info_dgk_driver,
        mongodb_driver=basic_info_mongodb_driver,
    )
    basic_info_service: BasicInfoService = providers.Singleton(BasicInfoService, manager=basic_info_manager)

    floor_info_dgk_driver: FloorInfoDgkDriver = providers.Factory(FloorInfoDgkDriver)
    floor_info_mongodb_driver: FloorInfoMongodbDriver = providers.Factory(FloorInfoMongodbDriver)
    floor_info_manager: FloorInfoManager = providers.Singleton(
        FloorInfoManager,
        dgk_driver=floor_info_dgk_driver,
        mongodb_driver=floor_info_mongodb_driver,
    )
    floor_info_service: FloorInfoService = providers.Singleton(FloorInfoService, manager=floor_info_manager)

    area_info_dgk_driver: AreaInfoDgkDriver = providers.Factory(AreaInfoDgkDriver)
    area_info_mongodb_driver: AreaInfoMongodbDriver = providers.Factory(AreaInfoMongodbDriver)
    area_info_manager: AreaInfoManager = providers.Singleton(
        AreaInfoManager,
        dgk_driver=area_info_dgk_driver,
        mongodb_driver=area_info_mongodb_driver,
    )
    area_info_service: AreaInfoService = providers.Singleton(AreaInfoService, manager=area_info_manager)

    price_info_dgk_driver: PriceInfoDgkDriver = providers.Factory(PriceInfoDgkDriver)
    price_info_mongodb_driver: PriceInfoMongodbDriver = providers.Factory(PriceInfoMongodbDriver)
    price_info_manager: PriceInfoManager = providers.Singleton(
        PriceInfoManager,
        dgk_driver=price_info_dgk_driver,
        mongodb_driver=price_info_mongodb_driver,
    )
    price_info_service: PriceInfoService = providers.Singleton(PriceInfoService, manager=price_info_manager)

    address_info_dgk_driver: AddressInfoDgkDriver = providers.Factory(AddressInfoDgkDriver)
    address_info_mongodb_driver: AddressInfoMongodbDriver = providers.Factory(AddressInfoMongodbDriver)
    address_info_manager: AddressInfoManager = providers.Singleton(
        AddressInfoManager,
        dgk_driver=address_info_dgk_driver,
        mongodb_driver=address_info_mongodb_driver,
    )
    address_info_service: AddressInfoService = providers.Singleton(AddressInfoService, manager=address_info_manager)

    relation_info_dgk_driver: RelationInfoDgkDriver = providers.Factory(RelationInfoDgkDriver)
    relation_info_mongodb_driver: RelationInfoMongodbDriver = providers.Factory(RelationInfoMongodbDriver)
    relation_info_manager: RelationInfoManager = providers.Singleton(
        RelationInfoManager,
        dgk_driver=relation_info_dgk_driver,
        mongodb_driver=relation_info_mongodb_driver,
    )
    relation_info_service: RelationInfoService = providers.Singleton(RelationInfoService, manager=relation_info_manager)

    zone_info_dgk_driver: ZoneInfoDgkDriver = providers.Factory(ZoneInfoDgkDriver)
    zone_info_mongodb_driver: ZoneInfoMongodbDriver = providers.Factory(ZoneInfoMongodbDriver)
    zone_info_manager: ZoneInfoManager = providers.Singleton(
        ZoneInfoManager,
        dgk_driver=zone_info_dgk_driver,
        mongodb_driver=zone_info_mongodb_driver,
    )
    zone_info_service: ZoneInfoService = providers.Singleton(ZoneInfoService, manager=zone_info_manager)

    kapt_list_dgk_driver: KaptListDgkDriver = providers.Factory(KaptListDgkDriver)
    kapt_list_mongodb_driver: KaptListMongodbDriver = providers.Factory(KaptListMongodbDriver)
    kapt_list_manager: KaptListManager = providers.Singleton(
        KaptListManager,
        dgk_driver=kapt_list_dgk_driver,
        mongodb_driver=kapt_list_mongodb_driver,
    )
    kapt_list_service: KaptListService = providers.Singleton(
        KaptListService,
        manager=kapt_list_manager,
    )

    kapt_basic_dgk_driver: KaptBasicDgkDriver = providers.Factory(KaptBasicDgkDriver)
    kapt_basic_mongodb_driver: KaptBasicMongodbDriver = providers.Factory(KaptBasicMongodbDriver)
    kapt_basic_manager: KaptBasicManager = providers.Singleton(
        KaptBasicManager,
        dgk_driver=kapt_basic_dgk_driver,
        mongodb_driver=kapt_basic_mongodb_driver,
    )
    kapt_basic_service: KaptBasicService = providers.Singleton(KaptBasicService, manager=kapt_basic_manager)

    kapt_detail_dgk_driver: KaptDetailDgkDriver = providers.Factory(KaptDetailDgkDriver)
    kapt_detail_mongodb_driver: KaptDetailMongodbDriver = providers.Factory(KaptDetailMongodbDriver)
    kapt_detail_manager: KaptDetailManager = providers.Singleton(
        KaptDetailManager,
        dgk_driver=kapt_detail_dgk_driver,
        mongodb_driver=kapt_detail_mongodb_driver,
    )
    kapt_detail_service: KaptDetailService = providers.Singleton(KaptDetailService, manager=kapt_detail_manager)