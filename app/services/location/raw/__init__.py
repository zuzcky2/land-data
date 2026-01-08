from dataclasses import dataclass
from dependency_injector.wiring import Provide, inject
from app.services.location.raw.container import RawContainer
from app.core.service.service_cache import get_service_with_cache
from app.services.location.raw.services.address_service import AddressService
from app.services.location.raw.services.continuous_geometry_service import ContinuousGeometryService
from app.services.location.raw.services.point_geometry_service import PointGeometryService


@dataclass
class RawFacade:
    address_service: AddressService
    continuous_geometry_service: ContinuousGeometryService
    point_geometry_service: PointGeometryService

@inject
def get_service(
    _address_service: AddressService = Provide[RawContainer.address_service],
    _continuous_geometry_service: ContinuousGeometryService = Provide[RawContainer.continuous_geometry_service],
    _point_geometry_service: PointGeometryService = Provide[RawContainer.point_geometry_service],
) -> RawFacade:
    return RawFacade(
        address_service=_address_service,
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