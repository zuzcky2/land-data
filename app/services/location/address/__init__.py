from dataclasses import dataclass
from dependency_injector.wiring import Provide, inject
from app.services.location.address.container import AddressContainer
from app.core.service.service_cache import get_service_with_cache
from app.services.location.address.services.search_service import SearchService


@dataclass
class RawFacade:
    search_service: SearchService

@inject
def get_service(
    _search_service: SearchService = Provide[AddressContainer.search_service],
) -> RawFacade:
    return RawFacade(
        search_service=_search_service,
    )

# 의존성 주입을 위한 Container 인스턴스 생성
application = AddressContainer()

# 컨테이너의 구성 요소를 현재 모듈에 와이어링
application.wire(modules=[__name__])

facade: RawFacade = get_service_with_cache('location_address', get_service)


# 외부로 노출할 변수들을 지정합니다.
__all__ = ['facade']