from dataclasses import dataclass
from dependency_injector.wiring import Provide, inject
from app.services.building.structure.container import StructureContainer
from app.core.service.service_cache import get_service_with_cache
from app.services.building.structure.services.address_service import AddressService
from app.services.building.structure.services.complex_service import ComplexService
from app.services.building.structure.services.building_service import BuildingService
from app.services.building.structure.services.floor_service import FloorService
from app.services.building.structure.services.unit_service import UnitService


@dataclass
class StructureFacade:
    address_service: AddressService
    complex_service: ComplexService
    building_service: BuildingService
    floor_service: FloorService
    unit_service: UnitService


@inject
def get_service(
    _address_service: AddressService = Provide[StructureContainer.address_service],
    _complex_service: ComplexService = Provide[StructureContainer.complex_service],
    _building_service: BuildingService = Provide[StructureContainer.building_service],
    _floor_service: FloorService = Provide[StructureContainer.floor_service],
    _unit_service: UnitService = Provide[StructureContainer.unit_service],
) -> StructureFacade:
    return StructureFacade(
        address_service=_address_service,
        complex_service=_complex_service,
        building_service=_building_service,
        floor_service=_floor_service,
        unit_service=_unit_service,
    )


# 의존성 주입을 위한 Container 인스턴스 생성
application = StructureContainer()

# 컨테이너의 구성 요소를 현재 모듈에 와이어링
application.wire(modules=[__name__])

facade: StructureFacade = get_service_with_cache('building_structure', get_service)


# 외부로 노출할 변수들을 지정합니다.
__all__ = ['facade']
