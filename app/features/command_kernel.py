"""CLI 명령어 커널 모듈

애플리케이션의 모든 CLI 명령어 클래스들을 중앙 집중적으로 관리합니다.
각 서비스별 명령어 클래스들을 수집하여 CLI 시스템에 등록할 수 있도록 제공합니다.
"""

from typing import List, Any
from app.core.helpers.log import Log

logger = Log.get_logger('command')

def get_command_list() -> List[Any]:
    """
    애플리케이션의 모든 CLI 명령어 클래스 인스턴스를 반환합니다.

    각 서비스 패키지에서 제공하는 명령어 클래스들을 동적으로 로드하여
    CLI 시스템에서 사용할 수 있도록 리스트로 반환합니다.
    """
    try:
        # 각 서비스의 명령어 클래스 로드
        from app.features.location.boundary.command import BoundaryCommand
        from app.features.building.raw.command import BuildingRawCommand
        from app.features.location.address.command import LocationAddressCommand
        from app.features.building.structure.command import StructureBuildCommand

        # 현재 등록된 명령어 클래스들
        command_classes = [
            BoundaryCommand(),              # 지역 경계 데이터 관련 명령어들
            BuildingRawCommand(), # 건축물 원본 데이터 관련 명령어들
            LocationAddressCommand(),
            StructureBuildCommand()
        ]

        logger.info(f"명령어 클래스 로드 완료: {len(command_classes)}개")
        return command_classes

    except ImportError as e:
        error_msg = f"명령어 클래스 로드 실패: {e}"
        logger.error(f"❌ {error_msg}")
        raise ImportError(error_msg)

    except AttributeError as e:
        error_msg = f"명령어 클래스 속성 접근 실패: {e}"
        logger.error(f"❌ {error_msg}")
        raise AttributeError(error_msg)


def register_all_commands(cli_group) -> None:
    """
    모든 명령어 클래스를 CLI 그룹에 등록하는 편의 함수입니다.

    get_command_list()에서 반환된 모든 명령어 클래스들을
    주어진 CLI 그룹에 자동으로 등록합니다.
    """
    command_list = get_command_list()
    registered_count = 0

    for command_class in command_list:
        if hasattr(command_class, 'register_commands'):
            command_class.register_commands(cli_group)

            # 명령어 클래스 정보 로깅
            class_name = command_class.__class__.__name__
            logger.info(f"✅ {class_name} 명령어 등록")
            registered_count += 1
        else:
            class_name = command_class.__class__.__name__
            error_msg = f"명령어 클래스 '{class_name}'에 register_commands 메서드가 없습니다."
            logger.error(f"❌ {error_msg}")
            raise AttributeError(error_msg)

    logger.info(f"명령어 등록 완료: {registered_count}개")


__all__ = ['get_command_list', 'register_all_commands']