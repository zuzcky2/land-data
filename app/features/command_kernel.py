"""CLI 명령어 커널 모듈

애플리케이션의 모든 CLI 명령어 클래스들을 중앙 집중적으로 관리합니다.
각 서비스별 명령어 클래스들을 수집하여 CLI 시스템에 등록할 수 있도록 제공합니다.
"""

from typing import List, Any
from app.core.helpers.log import Log

# 커맨드 전용 로거
logger = Log.get_logger('command')

def get_command_list() -> List[Any]:
    """
    애플리케이션의 모든 CLI 명령어 클래스 인스턴스를 반환합니다.

    각 Command 클래스는 'app.core.packages.support.modules.command.Command'를 상속받아
    내부적으로 슬랙 알림 및 로깅 로직을 수행합니다.
    """
    try:
        # 각 서비스의 명령어 클래스 동적 로드
        from app.features.location.boundary.command import BoundaryCommand
        from app.features.building.raw.command import BuildingRawCommand
        from app.features.location.raw.command import LocationRawCommand
        from app.features.building.structure.command import StructureBuildCommand

        # 현재 등록된 명령어 클래스 인스턴스 리스트
        command_classes = [
            BoundaryCommand(),              # 지역 경계 데이터 관련
            BuildingRawCommand(),           # 건축물 원본 데이터 관련
            LocationRawCommand(),       # 주소 마스터 동기화 관련
            StructureBuildCommand()         # 공간정보 빌드 관련
        ]

        logger.info(f"명령어 클래스 로드 완료: {len(command_classes)}개")
        return command_classes

    except ImportError as e:
        error_msg = f"명령어 클래스 로드 실패 (ImportError): {e}"
        logger.error(f"❌ {error_msg}")
        raise ImportError(error_msg)

    except Exception as e:
        error_msg = f"명령어 시스템 초기화 중 예기치 않은 오류: {e}"
        logger.error(f"❌ {error_msg}")
        raise e


def register_all_commands(cli_group) -> None:
    """
    모든 명령어 클래스를 CLI 그룹에 등록합니다.

    각 클래스에 구현된 register_commands 메서드를 호출하여
    Click 시스템에 명령어를 바인딩합니다.
    """
    try:
        command_list = get_command_list()
        registered_count = 0

        for command_instance in command_list:
            if hasattr(command_instance, 'register_commands'):
                # Click 그룹에 명령어 등록
                command_instance.register_commands(cli_group)

                class_name = command_instance.__class__.__name__
                logger.debug(f"✅ {class_name} 명령어 등록 성공")
                registered_count += 1
            else:
                class_name = command_instance.__class__.__name__
                logger.warning(f"⚠️ {class_name} 클래스에 'register_commands' 메서드가 없습니다.")

        logger.info(f"CLI 시스템 명령어 등록 프로세스 완료: 총 {registered_count}개")

    except Exception as e:
        logger.error(f"❌ 명령어 등록 중 치명적 오류 발생: {e}")
        raise e


__all__ = ['get_command_list', 'register_all_commands']