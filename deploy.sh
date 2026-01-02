#!/usr/bin/env bash

# @author jinsoo.kim <jjambbongjoa@gmail.com>
MSG_COLOR="\033[1;32m"
MSG_RESET="\033[0m"
MSG_PREFIX="${MSG_COLOR}[Jinsoo.Kim@IAPI-WORK-STATUS]$ ${MSG_RESET}"

echo -e "${MSG_PREFIX}서비스 빌드 가능성 검사 시작..\n"

# .env 파일 확인
if [ ! -f .env ]; then
    echo -e "${MSG_PREFIX}#ERROR .env 파일이 존재하지 않습니다."
    exit 1
fi

# docker-compose.yml 파일 확인
if [ ! -f docker-compose.yml ]; then
    echo -e "${MSG_PREFIX}#ERROR docker-compose.yml 파일이 존재하지 않습니다."
    exit 1
fi

bash ./__docker-network-setup.sh

echo -e "${MSG_PREFIX}서비스 빌드 가능성 검사 통과\n"

# .env 파일 로드
export $(grep -v '^#' .env | xargs)

echo -e "${MSG_PREFIX}log, data 디렉토리 세팅 시작...\n"

# 로그 및 데이터 디렉토리 생성
DIRECTORIES=(
    "${__VOLUME_PATH__}/data/${APP_NAME}"
    "${__VOLUME_PATH__}/log/${APP_NAME}"
)

for DIRECTORY in "${DIRECTORIES[@]}"; do
    if [ ! -d "$DIRECTORY" ]; then
        mkdir -p "$DIRECTORY"
        chmod 707 "$DIRECTORY"
    fi
done

echo -e "${MSG_PREFIX}log, data 디렉토리 세팅 완료\n"

# APP_ENV 값에 따라 실행 분기
if [[ "$APP_ENV" == "production" ]]; then
    echo -e "${MSG_PREFIX}⚡ Production 모드 - 개별 Docker 빌드 및 실행 시작...\n"

    docker build --target=production -t ${APP_NAME} .

    # 2. 기존 컨테이너 종료 및 삭제
    if docker ps -a --format '{{.Names}}' | grep -Eq "^${APP_NAME}"; then
      echo "✅ 기존 컨테이너 종료 및 삭제"
      docker stop ${APP_NAME} && docker rm ${APP_NAME}
    fi

    docker run -d \
      --name ${APP_NAME} \
      --network micro-network \
      -p "${API_PORT}:8000" \
      -p "${JUPYTER_PORT}:8888" \
      -e ENV_MODE=production \
      -v "$(pwd)/${__VOLUME_PATH__}/log/${APP_NAME}:/var/volumes/log:delegated" \
      -v "$(pwd)/${__VOLUME_PATH__}/data/${APP_NAME}:/root/.cache/pypoetry/virtualenvs:delegated" \
      --log-driver json-file \
      --log-opt max-size=3m \
      --log-opt max-file=3 \
      --log-opt compress=true \
      --restart unless-stopped \
      ${APP_NAME}

        echo -e "${MSG_PREFIX}⚡ Production 모드 - 개별 Docker 빌드 및 실행 시작...\n"

    echo -e "${MSG_PREFIX}🚀 Production 모드 - Docker 컨테이너 실행 완료\n"
else
    echo -e "${MSG_PREFIX}🛠 Development 모드 - Docker Compose 실행...\n"

    docker-compose -f docker-compose.yml up --build -d

    echo -e "${MSG_PREFIX}✅ Development 모드 - Docker Compose 실행 완료\n"
fi