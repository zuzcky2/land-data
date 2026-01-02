"""애플리케이션 라이프사이클 관리 모듈."""

from typing import Optional, Dict, Any, Final
import threading
import builtins
import sys

# Rich 라이브러리 로드
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich import inspect as rich_inspect
except ImportError:
    Console = None

from app.core.container import AppContainer


class ApplicationState:
    """애플리케이션의 전역 상태를 관리하는 싱글톤 클래스입니다."""

    def __init__(self) -> None:
        self._container: Optional[AppContainer] = None
        self._is_initialized: bool = False
        self._lock: threading.Lock = threading.Lock()

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> AppContainer:
        with self._lock:
            if self._is_initialized:
                return self._container

            self._container = AppContainer()
            if config:
                try:
                    self._container.config.from_dict(config)
                except Exception as e:
                    print(f"⚠️  설정 주입 실패: {e}")

            self._is_initialized = True
            return self._container

    def get_container(self) -> AppContainer:
        if not self._is_initialized:
            raise RuntimeError("애플리케이션이 초기화되지 않았습니다.")
        return self._container

    def is_initialized(self) -> bool:
        """이 메서드가 삭제되어 에러가 발생했었습니다. 다시 추가합니다."""
        return self._is_initialized

    def reset(self) -> None:
        with self._lock:
            if self._container:
                try:
                    self._container.unwire()
                except Exception:
                    pass
            self._container = None
            self._is_initialized = False


# --- 전역 dd() 등록 ---
def _register_global_debugger():
    def dd(*args, inspect: bool = False):
        if Console is None:
            for arg in args:
                print(arg)
            sys.exit(1)

        console = Console()
        console.print("\n")
        console.print(Panel("[bold red]DUMP & DIE[/bold red]", expand=False, border_style="red"))

        for arg in args:
            if inspect:
                rich_inspect(arg, console=console, methods=True)
            else:
                console.print(arg)
        sys.exit(1)

    builtins.dd = dd

# 즉시 실행
_register_global_debugger()

# 전역 상태 인스턴스
_app_state: Final[ApplicationState] = ApplicationState()

def get_app_state() -> ApplicationState:
    return _app_state

__all__ = ['ApplicationState', 'get_app_state', 'dd']