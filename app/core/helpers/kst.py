from datetime import datetime
import pytz

class Kst:
    """
    한국 표준시(KST) 현재 시간을 반환하는 유틸리티 클래스입니다.
    """

    @staticmethod
    def now() -> datetime:
        """
        현재 한국 표준시(KST) 시간을 반환합니다.

        Returns:
            datetime: 한국 표준시(KST)로 설정된 현재 시간 객체입니다.
        """
        # 한국 표준시 타임존 설정
        timezone = pytz.timezone('Asia/Seoul')
        # 현재 시간을 KST로 반환
        return datetime.now(timezone)

# 외부에 노출할 클래스 목록을 정의합니다.
__all__ = ['Kst']