from bson.objectid import ObjectId
from pydantic import BaseModel
from typing import Dict, Any


class PyObjectId(ObjectId):
    """
    MongoDB의 ObjectId에 대한 Pydantic 유효성 검사와 변환을 위한 클래스입니다.
    """

    @classmethod
    def __get_validators__(cls):
        """
        Pydantic 유효성 검사기를 제공합니다.

        Yields:
            Callable: ObjectId 유효성 검사 함수
        """
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        """
        값이 유효한 ObjectId인지 확인하고 반환합니다.

        Args:
            v (Any): 유효성 검사를 수행할 값

        Returns:
            ObjectId: 유효한 ObjectId 객체

        Raises:
            ValueError: 주어진 값이 유효한 ObjectId가 아닌 경우
        """
        if not ObjectId.is_valid(v):
            raise ValueError("잘못된 ObjectId입니다.")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]):
        """
        Pydantic 스키마에서 ObjectId 필드를 문자열로 정의합니다.

        Args:
            field_schema (Dict[str, Any]): 수정할 스키마
        """
        field_schema.update(type="string")


class MongoModel(BaseModel):
    """
    MongoDB 문서 모델을 위한 Pydantic 기본 모델 클래스입니다.
    ObjectId 필드 처리와 MongoDB JSON 직렬화를 지원합니다.
    """

    class Config:
        # 필드 이름으로 데이터 설정 허용 (alias 지원)
        allow_population_by_field_name = True
        # ObjectId를 JSON 문자열로 변환
        json_encoders = {ObjectId: str}
        # 임의의 데이터 타입 허용
        arbitrary_types_allowed = True

    def dict(self, **kwargs) -> Dict[str, Any]:
        """
        모델 인스턴스를 딕셔너리로 변환하여 MongoDB 저장 형식에 맞춥니다.

        Args:
            **kwargs: Pydantic dict 메서드에 전달할 추가 인수

        Returns:
            Dict[str, Any]: MongoDB 형식에 맞게 변환된 딕셔너리
        """
        kwargs['by_alias'] = True  # 별칭으로 필드 이름 변환
        original_dict = super().dict(**kwargs)  # 원래 딕셔너리 생성

        # 'id' 필드를 '_id'로 변경하여 MongoDB에 맞게 조정
        if 'id' in original_dict and original_dict['id'] is not None:
            original_dict['_id'] = original_dict.pop('id')
        else:
            # 'id'가 없거나 None이면 '_id' 제거
            original_dict.pop('_id', None)

        return original_dict