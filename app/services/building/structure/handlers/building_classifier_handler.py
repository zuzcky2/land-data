import re


class BuildingClassifierHandler:
    def __init__(self):
        # 2차 카테고리 및 태그 정의 (태그 리스트를 만들기 위한 매핑)
        # 키워드가 발견되는 모든 항목을 결과 배열에 담습니다.
        self.tag_map = {
            "주거용": {
                "아파트": [r"아파트"],
                "오피스텔": [r"오피스텔"],
                "연립/다세대": [r"다세대", r"연립", r"도시형생활", r"빌라"],
                "단독/다가구": [r"단독", r"다가구", r"다중주택", r"주택"],
                "기타주거": [r"기숙사", r"노인복지주택", r"주거시설"]
            },
            "상업용": {
                "제1종근린생활시설": [r"제1종근린생활", r"1종근생", r"소매점", r"마을회관", r"변전소", r"정수장"],
                "제2종근린생활시설": [r"제2종근린생활", r"2종근생", r"음식점", r"사무소", r"학원", r"사진관", r"체육도장"],
                "근린생활시설": [r"(?<!제[12]종)근린생활", r"(?<![12]종)근생", r"점포", r"상가"],  # 1,2종 명시 없을 때
                "판매/영업시설": [r"판매시설", r"시장", r"상점", r"백화점", r"영업소"],
                "숙박/위락시설": [r"숙박", r"위락", r"유흥", r"단란주점", r"여관"]
            },
            "산업/창고용": {
                "공장/제조": [r"공장", r"제조업", r"작업장", r"제조소"],
                "창고/유통": [r"창고", r"저장고", r"물류", r"집배송"],
                "위험물/처리": [r"위험물", r"자원순환", r"분뇨", r"쓰레기", r"주유소"]
            },
            "업무/공공용": {
                "업무시설": [r"업무", r"사무실", r"공공업무"],
                "교육/의료/복지": [r"교육", r"연구", r"학교", r"의료", r"병원", r"노유자", r"복지", r"어린이집"],
                "종교/문화/공공": [r"종교", r"교회", r"사찰", r"문화및집회", r"군사", r"교정", r"발전", r"방송", r"박물관"]
            },
            "기타": {
                "자동차관련": [r"자동차", r"주차장", r"세차장", r"정비공장"],
                "동식물관련": [r"동물", r"식물", r"축사", r"온실", r"재배사"],
                "운동/관광/수련": [r"운동시설", r"관광휴게", r"수련시설", r"야영장"]
            }
        }

    def process(self, main_purp: str, etc_purp: str):
        full_text = f"{main_purp or ''} {etc_purp or ''}".replace(" ", "")

        cat1_tags = set()
        cat2_tags = set()

        for cat1, sub_dict in self.tag_map.items():
            for cat2, patterns in sub_dict.items():
                for pattern in patterns:
                    if re.search(pattern, full_text):
                        cat1_tags.add(cat1)
                        cat2_tags.add(cat2)
                        break  # 해당 2차 카테고리에서 하나라도 매칭되면 다음 2차 카테고리로

        # 결과 리스트화 (정렬하여 일관성 유지)
        cat1_list = sorted(list(cat1_tags))
        cat2_list = sorted(list(cat2_tags))

        # 단수 값 결정 (기존 로직 유지 - 가장 우선순위가 높은 첫 번째 항목 선택)
        # 우선순위: 주거 > 상업 > 업무 > 산업 > 기타
        priority = ["주거용", "상업용", "업무/공공용", "산업/창고용", "기타"]
        main_cat1 = next((p for p in priority if p in cat1_list), "기타") if cat1_list else "기타"

        # main_cat1에 해당하는 sub_tags 중 첫 번째 선택
        sub_tags_for_main = [c2 for c2 in cat2_list if c2 in self.tag_map.get(main_cat1, {})]
        main_cat2 = sub_tags_for_main[0] if sub_tags_for_main else "기타"

        return {
            "main_category": main_cat1,  # 1차 단수
            "sub_category": main_cat2,  # 2차 단수
            "category_tags": cat1_list,  # 1차 복수 (배열)
            "sub_category_tags": cat2_list  # 2차 복수 (배열)
        }