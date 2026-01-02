"""CLI 실행 진입점 모듈.

이 모듈은 애플리케이션의 CLI 명령어 실행을 담당합니다.
- DI(Dependency Injection) 컨테이너를 통해 필요한 서비스들을 주입받습니다
- 등록된 모든 명령어 클래스들을 자동으로 CLI 그룹에 등록합니다
- Click 프레임워크를 사용하여 CLI 인터페이스를 구성합니다
"""

import sys
import logging
from typing import List, Any

import click

from app.core.runner import run_with_services
from app.core.logger import log_exception


def _create_cli_group() -> click.Group:
    """
    Click CLI 그룹을 생성합니다.

    Returns:
        click.Group: 생성된 CLI 그룹 객체
    """

    @click.group()
    def cli() -> None:
        """애플리케이션 CLI 명령어 그룹을 정의합니다."""
        pass

    return cli


def _register_commands(cli_group: click.Group, logger: logging.Logger) -> None:
    """
    등록된 모든 명령어 클래스들을 CLI 그룹에 등록합니다.

    Args:
        cli_group (click.Group): 명령어를 등록할 CLI 그룹
        logger (logging.Logger): 로깅을 위한 Logger 객체

    Raises:
        ImportError: 명령어 커널 모듈을 가져올 수 없는 경우
    """
    try:
        # DI 초기화 후 명령어 리스트 가져오기
        from app.features.command_kernel import get_command_list
        command_list: List[Any] = get_command_list()

        # 각 명령어 인스턴스를 CLI 그룹에 등록
        for command_instance in command_list:
            if hasattr(command_instance, 'register_commands'):
                # 명령어 등록 메서드가 있는 경우 실행
                command_class_name: str = command_instance.__class__.__name__
                logger.info(f"✅ {command_class_name} 명령어 등록")
                command_instance.register_commands(cli_group)
            else:
                # 명령어 등록 메서드가 없는 경우 경고 로그
                command_type: str = str(type(command_instance))
                logger.warning(f"⚠️ {command_type}에 register_commands 메서드가 없습니다.")

    except ImportError as e:
        logger.error(f"❌ 명령어 커널 모듈 import 실패: {e}")
        raise


def run_command(logger: logging.Logger, log_config: Any) -> None:
    """
    Command CLI 실행 함수.

    CLI 그룹을 생성하고 등록된 모든 명령어들을 등록한 후 CLI를 실행합니다.

    Args:
        logger (logging.Logger): 로깅을 위한 Logger 객체
        log_config (Any): 로그 설정 객체 (현재 미사용이지만 runner 인터페이스 호환성을 위해 유지)

    Raises:
        SystemExit: CLI 실행 중 오류 발생 시 시스템 종료
    """
    try:
        logger.info("🟢 Command CLI 실행 시작")

        # CLI 그룹 생성
        cli_group: click.Group = _create_cli_group()

        # 명령어들을 CLI 그룹에 등록
        _register_commands(cli_group, logger)

        # CLI 실행 - 사용자가 입력한 명령어에 따라 해당 명령어 실행
        cli_group()

        logger.info("✅ Command CLI 정상 종료")

    except Exception as e:
        # 예외 발생 시 로그 기록 후 시스템 종료
        log_exception(logger, "Command 실행", e)
        sys.exit(1)


def main() -> None:
    """
    프로그램 실행 진입점.

    DI 기반으로 logger와 관련 서비스들을 주입받아 run_command() 함수를 실행합니다.
    run_with_services는 애플리케이션의 부트스트랩 과정을 처리하고
    필요한 의존성들을 주입해줍니다.
    """
    run_with_services(
        app_name='command',  # 애플리케이션 이름 (로깅 및 설정에 사용)
        main_fn=run_command,  # 실제 실행할 메인 함수
        bootstrap_condition=True  # 부트스트랩 조건 (항상 True로 설정하여 초기화 수행)
    )


# 스크립트가 직접 실행될 때만 main() 함수 호출
if __name__ == '__main__':
    main()
