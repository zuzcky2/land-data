from app.core.packages.support.abstracts.abstract_container import AbstractContainer, providers
from app.services.building.raw.drivers.address_info.address_info_dgk import AddressInfoDgkDriver
from app.services.building.raw.drivers.address_info.address_info_mongodb import AddressInfoMongodbDriver
from app.services.building.raw.drivers.area_info.area_info_dgk import AreaInfoDgkDriver
from app.services.building.raw.drivers.area_info.area_info_mongodb import AreaInfoMongodbDriver
from app.services.building.raw.drivers.basic_info.basic_info_dgk import BasicInfoDgkDriver
from app.services.building.raw.drivers.basic_info.basic_info_mongodb import BasicInfoMongodbDriver
from app.services.building.raw.drivers.floor_info.floor_info_dgk import FloorInfoDgkDriver
from app.services.building.raw.drivers.floor_info.floor_info_mongodb import FloorInfoMongodbDriver
from app.services.building.raw.drivers.price_info.price_info_dgk import PriceInfoDgkDriver
from app.services.building.raw.drivers.price_info.price_info_mongodb import PriceInfoMongodbDriver
from app.services.building.raw.drivers.title_info.title_info_dgk import TitleInfoDgkDriver
from app.services.building.raw.drivers.title_info.title_info_mongodb import TitleInfoMongodbDriver
from app.services.building.raw.managers.address_info_manager import AddressInfoManager
from app.services.building.raw.managers.area_info_manager import AreaInfoManager
from app.services.building.raw.managers.basic_info_manager import BasicInfoManager
from app.services.building.raw.managers.floor_info_manager import FloorInfoManager
from app.services.building.raw.managers.price_info_manager import PriceInfoManager
from app.services.building.raw.managers.title_info_manager import TitleInfoManager
from app.services.building.raw.services.address_info_service import AddressInfoService
from app.services.building.raw.services.area_info_service import AreaInfoService
from app.services.building.raw.services.basic_info_service import BasicInfoService
from app.services.building.raw.services.floor_info_service import FloorInfoService
from app.services.building.raw.services.price_info_service import PriceInfoService
from app.services.building.raw.services.title_info_service import TitleInfoService


class RawContainer(AbstractContainer):

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
