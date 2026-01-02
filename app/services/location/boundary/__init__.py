from dataclasses import dataclass
from dependency_injector.wiring import Provide, inject
from app.services.location.boundary.container import BoundaryContainer
from app.services.location.boundary.service import BoundaryService
from app.core.service.service_cache import get_service_with_cache

@dataclass
class BoundaryFacade:
    service: BoundaryService


@inject
def get_service(
    _service: BoundaryService = Provide[BoundaryContainer.boundary_service],
) -> BoundaryFacade:
    return BoundaryFacade(
        service=_service
    )

# 의존성 주입을 위한 Container 인스턴스 생성
application = BoundaryContainer()

# 컨테이너의 구성 요소를 현재 모듈에 와이어링
application.wire(modules=[__name__])

facade: BoundaryFacade = get_service_with_cache('location_boundary', get_service)


# 외부로 노출할 변수들을 지정합니다.
__all__ = ['facade']