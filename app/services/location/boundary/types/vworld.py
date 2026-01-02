from typing import Any, List, Optional, Dict
import requests
from app.services.location.boundary.drivers.interface import BoundaryInterface
from app.services.location.boundary.handlers.build_boundary_item_handler import BuildBoundaryItemHandler
from app.services.location.boundary.types.boundary import STATE, DISTRICT, TOWNSHIP, VILLAGE, LEGAL
from app.core.helpers.config import Config


class VworldDriver(BoundaryInterface):
    """
    VWorld API 통합 드라이버.
    location_type에 따라 레이어와 속성 추출 방식을 자동으로 결정합니다.
    """

    _last_response_raw: Optional[dict] = None

    # 시도(STATE) 전용 매핑 데이터
    STATE_MAPPING = {
        '서울특별시': {'short_name': '서울시', 'manual_order': 0},
        '경기도': {'short_name': '경기도', 'manual_order': 1},
        '인천광역시': {'short_name': '인천시', 'manual_order': 2},
        '부산광역시': {'short_name': '부산시', 'manual_order': 3},
        '대전광역시': {'short_name': '대전시', 'manual_order': 4},
        '대구광역시': {'short_name': '대구시', 'manual_order': 5},
        '울산광역시': {'short_name': '울산시', 'manual_order': 6},
        '세종특별자치시': {'short_name': '세종시', 'manual_order': 7},
        '광주광역시': {'short_name': '광주시', 'manual_order': 8},
        '강원특별자치도': {'short_name': '강원도', 'manual_order': 9},
        '충청북도': {'short_name': '충청북도', 'manual_order': 10},
        '충청남도': {'short_name': '충청남도', 'manual_order': 11},
        '전북특별자치도': {'short_name': '전라북도', 'manual_order': 12},
        '전라남도': {'short_name': '전라남도', 'manual_order': 13},
        '경상북도': {'short_name': '경상북도', 'manual_order': 14},
        '경상남도': {'short_name': '경상남도', 'manual_order': 15},
        '제주특별자치도': {'short_name': '제주도', 'manual_order': 16},
    }

    # location_type별 VWorld 레이어 및 필드 매핑 설정
    LAYER_CONFIG = {
        STATE: {
            'feature_data': 'LT_C_ADSIDO_INFO',
            'code_field': 'ctprvn_cd',
            'name_field': 'ctp_kor_nm'
        },
        DISTRICT: {
            'feature_data': 'LT_C_ADSIGG_INFO',
            'code_field': 'sig_cd',
            'name_field': 'sig_kor_nm'
        },
        TOWNSHIP: {
            'feature_data': 'LT_C_ADEMD_INFO',
            'code_field': 'emd_cd',
            'name_field': 'emd_kor_nm'
        },
        VILLAGE: {
            'feature_data': 'LT_C_ADRI_INFO',
            'code_field': 'li_cd',
            'name_field': 'li_kor_nm'
        }
    }

    def __init__(self, build_boundary_item_handler: BuildBoundaryItemHandler):
        super().__init__(build_boundary_item_handler)

    def _fetch_raw(self, single: bool = False) -> Any:
        # 1. 현재 location_type에 맞는 설정 로드
        loc_type = self.arguments('location_type')
        config = self.LAYER_CONFIG.get(loc_type)
        if not config:
            raise ValueError(f"지원하지 않는 location_type입니다: {loc_type}")

        # 2. 파라미터 빌드
        url = 'https://api.vworld.kr/req/data'
        params = {
            'key': Config.get('vworld.key'),
            'domain': Config.get('vworld.domain'),
            'format': 'json',
            'crs': 'EPSG:4326',
            'service': 'data',
            'version': '2.0',
            'request': 'getFeature',
            'data': config['feature_data'],
            'page': str(self.page),
            'size': str(self.per_page if not single else 1),
        }

        # 3. 필터링 로직 (기존 드라이버 분석 내용 반영)
        # item_code가 있으면 레이어별 코드 필드에 맞춰 attrFilter 생성
        if self.arguments('item_code'):
            params['attrFilter'] = f"{config['code_field']}:like:{self.arguments('item_code')}"

        # STATE의 경우 전국 단위 조회를 위한 BBOX 기본값 처리 가능
        if loc_type == STATE and not self.arguments('bbox'):
            params['geomFilter'] = 'BOX(124.60,33.10,131.87,38.61)'
        elif self.arguments('bbox'):
            params['geomFilter'] = f"BOX({','.join(map(str, self.arguments('bbox')))})"

        # 4. API 호출 및 결과 처리
        response = requests.get(url, params=params)
        data = response.json()
        self._last_response_raw = data

        if data.get('response', {}).get('status') == 'OK':
            features = data['response']['result']['featureCollection']['features']
            # 각 feature를 공통 규격(HandlerInput 형식)으로 변환
            return [self._map_to_handler_input(f, loc_type, config) for f in features]

        return []

    def _map_to_handler_input(self, feature: dict, loc_type: str, config: dict) -> dict:
        """
        VWorld API 원본 데이터를 BuildBoundaryItemHandler가 인식할 수 있는
        공통 딕셔너리(HandlerInput) 형태로 매핑합니다.
        """
        props = feature['properties']
        item_name = props.get(config['name_field'])

        # STATE 전용 매핑 처리
        short_name = item_name
        manual_order = None
        if loc_type == STATE:
            mapping = self.STATE_MAPPING.get(item_name, {'short_name': item_name, 'manual_order': 99})
            short_name = mapping['short_name']
            manual_order = mapping['manual_order']

        return {
            'item_code': props.get(config['code_field']),
            'item_name': item_name,
            'item_full_name': props.get('full_nm', item_name),  # 시도는 full_nm이 없을 수 있음
            'short_name': short_name,
            'location_type': loc_type,
            'jurisdiction_type': LEGAL,  # 법정동 기준
            'geometry': feature['geometry'],
            'last_updated_at': None,
            'manual_order': manual_order
        }

    def _get_total_count(self) -> int:
        try:
            return int(self._last_response_raw['response']['record']['total'])
        except (KeyError, TypeError, AttributeError):
            return 0

    def store(self, items: List[Any]):
        raise NotImplementedError("VworldDriver는 읽기 전용입니다.")