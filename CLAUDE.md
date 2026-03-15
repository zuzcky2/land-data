# land-data

한국 부동산 데이터 수집/가공 플랫폼. 건축물대장 공공데이터를 수집하여 단지→건물→층→호실 계층 구조로 정규화한다.

## 현재 진행 상황 (2026-03-15 기준)

### 빌드 상태

| 컬렉션 | 상태 | 현재 건수 | 목표 |
|--------|------|----------|------|
| addresses | **빌드 중** | ~838K | ~3.2M |
| complexes | 대기 (address 완료 후 재빌드 예정) | 102,988 | - |
| buildings | 완료 | 548,286 | - |
| floors | 완료 | 421,306 | - |
| units | **빌드 중** | ~1.1M | ~10M |

### 자동 실행 체인 (서버에서 실행 중)

address 빌드 완료 → complex 전체 재빌드 → kapt-sync 순서로 자동 실행됨.

### 빌드 상태 확인 방법

```bash
# 빠른 현황 확인
ssh dev-ts "cd /home/kjs/workspace/landmark/data && docker-compose exec -T python bash -c 'tail -3 /var/volumes/log/monitor_builds.log'"

# 컬렉션 건수 확인
ssh dev-ts "cd /home/kjs/workspace/landmark/data && docker-compose exec -T python bash -c 'python -c \"
from app.facade import db
col = db.get_mongodb_driver(\\\\\"mongodb\\\\\").get_database(\\\\\"landmark\\\\\")
for name in [\\\\\"addresses\\\\\",\\\\\"complexes\\\\\",\\\\\"buildings\\\\\",\\\\\"floors\\\\\",\\\\\"units\\\\\"]:
    print(name, col.get_collection(name).count_documents({}))
\"'"
```

### 모니터링 스크립트

서버 컨테이너 내부에서 독립 실행 중 (`/var/workspace/monitor_builds.sh`).
로그: `/var/volumes/log/monitor_builds.log` (5분 간격)

## 개발 환경

- **로컬**: `/Users/kjs/workspace/landmark/land-data`
- **개발 서버**: `Host dev` (192.168.219.120 / Tailscale: `100.96.88.2`), 프로젝트 경로 `/home/kjs/workspace/landmark/data`
- **런타임**: Docker 컨테이너 (`landmark-data`) 내부에서 실행

### SSH 접속

```bash
ssh dev       # 홈 네트워크 내부 (192.168.219.120)
ssh dev-ts    # 외부 네트워크 — Tailscale 경유 (100.96.88.2)
```

`~/.ssh/config` 설정:
```
Host dev
    HostName 192.168.219.120
    User kjs
    IdentityFile ~/.ssh/id_rsa_dev
    Port 22

Host dev-ts
    HostName 100.96.88.2
    User kjs
    IdentityFile ~/.ssh/id_rsa_dev
    Port 22
```

> 다른 맥북에서 접속 시: Tailscale 설치 후 동일 계정(`jjambbongjoa@`) 로그인 → `ssh dev-ts` 로 접속

### 명령어 실행 방법

```bash
# 개발 서버에서 실행할 때 (항상 이 형식으로)
ssh dev "cd /home/kjs/workspace/landmark/data && docker-compose exec -T python bash -c 'poetry run command <명령어>'"

# 백그라운드 실행 (로그 파일로 출력)
ssh dev "cd /home/kjs/workspace/landmark/data && docker-compose exec -d python bash -c 'poetry run command <명령어> > /var/volumes/log/<파일>.log 2>&1'"
```

### Git 배포

```bash
git push  # 로컬에서 push
ssh dev "cd /home/kjs/workspace/landmark/data && git pull"  # 서버에서 pull 후 실행
```

---

## 아키텍처

### 계층 구조

```
단지 (Complex / complexes)
└── 건물 (Building / buildings)
    └── 층 (Floor / floors)
        └── 호실 (Unit / units)
```

### 건축물대장 regstrKindCd

| 코드 | 명칭 | 대상 컬렉션 |
|------|------|------------|
| 1 | 총괄표제부 | complexes |
| 2 | 일반건축물 | complexes |
| 3 | 표제부 | buildings |
| 4 | 전유부 | units |

### MongoDB 컬렉션 및 PK

| 컬렉션 | PK | 설명 |
|--------|-----|------|
| `addresses` | `building_manage_number` (bdMgtSn, 25자리) | 주소 + 공간정보 |
| `complexes` | `building_manage_number` | 단지 정보 |
| `buildings` | `register_manage_number` (mgmBldrgstPk) | 동별 건물 정보 |
| `floors` | `floor_id` (`{mgmBldrgstPk}_{flrGbCd}_{flrNo}`) | 층 정보 |
| `units` | `register_manage_number` (전유부 mgmBldrgstPk) | 호실 정보 |

### 컬렉션 간 참조

- `buildings.building_manage_number` → `complexes.building_manage_number`
- `floors.register_manage_number` → `buildings.register_manage_number`
- `floors.building_manage_number` → `complexes.building_manage_number`
- `units.parent_register_manage_number` → `buildings.register_manage_number`
- `units.building_manage_number` → `complexes.building_manage_number`

---

## 코드 구조

```
app/
├── services/building/structure/   # 핵심 도메인
│   ├── container.py               # DI 컨테이너 (dependency-injector)
│   ├── drivers/                   # MongoDB 드라이버 (PK, 컬렉션 정의)
│   ├── managers/                  # 드라이버 래퍼
│   ├── handlers/                  # Raw → DTO 변환 로직
│   ├── services/                  # 비즈니스 로직
│   └── dtos/                      # Pydantic 모델
├── services/building/raw/         # 건축물대장 원본 데이터 서비스
├── services/location/             # 위치/경계 데이터 서비스
└── features/building/structure/
    └── command.py                 # CLI 명령어 정의
notebooks/                         # 분석용 스크립트 (gitignore)
```

### DI 패턴

`Container` → `Manager` → `Driver` 순으로 의존성 주입. 새 엔티티 추가 시:
1. `drivers/` 에 MongoDB 드라이버 추가 (PK, 컬렉션명 정의)
2. `managers/` 에 매니저 추가
3. `handlers/` 에 Raw→DTO 핸들러 추가
4. `services/` 에 서비스 추가
5. `container.py` 에 등록
6. `__init__.py` 의 `StructureFacade` 에 추가
7. `features/.../command.py` 에 CLI 명령어 추가

---

## CLI 명령어

```bash
# 빌드 명령어
poetry run command building_structure:address          # 주소 빌드 (~3.2M)
poetry run command building_structure:complex          # 단지 빌드 (~120K)
poetry run command building_structure:building         # 건물 빌드 (~560K)
poetry run command building_structure:floor            # 층 빌드 (~3M)
poetry run command building_structure:unit             # 호실 빌드 (~10M)
poetry run command building_structure:kapt-sync        # K-APT 단지 정보 병합 (21,949건)

# 옵션
--continue    # 마지막 처리 지점부터 이어서 실행 (address, building, floor, unit)
--renew       # address 전체 재처리
```

### 빌드 순서 의존성

```
address → complex → (kapt-sync)
        → building → floor
                   → unit
```

---

## 로그 파일 위치 (컨테이너 내부)

```
/var/volumes/log/
├── building_structure/
│   ├── address_build.log
│   └── complex_build.log
├── building_build.log
├── floor_build.log
├── unit_build.log
└── kapt_sync.log
```

---

## K-APT 연동

- **데이터**: 21,949개 아파트 단지 (kaptCode PK)
- **매칭 방법**: `doroJuso` → 도로명/번지 파싱 → `addresses` 컬렉션 매칭 → `complexes` 에 `$set` 병합
- **주요 필드**: `kapt_code`, `heating_type`, `area_*_count`, `elevator_count`, `parking_count_kapt`, `subway_*`, `ev_charger_count` 등

---

## 카테고리 분류 (BuildingClassifierHandler)

`main_purpose` + `sub_purpose` 텍스트 기반 분류.

| 1차 | 주요 2차 |
|-----|---------|
| 주거용 | 아파트 (공동주택 포함), 단독/다가구, 오피스텔, 연립/다세대 |
| 상업용 | 제1·2종근린생활시설, 판매/영업, 숙박/위락 |
| 업무/공공용 | 업무시설, 교육/의료/복지, 종교/문화/공공 |
| 산업/창고용 | 공장/제조, 창고/유통, 위험물/처리 |
| 기타 | 자동차관련, 운수/물류, 동식물관련, 운동/관광/수련 |
