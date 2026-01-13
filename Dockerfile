# ✅ 1 단계: 기본 이미지 설정
FROM continuumio/miniconda3:25.1.1-2 AS base

LABEL maintainer="jinsoo.kim <jjambbongjoa@gmail.com>"

USER root
WORKDIR /var/workspace
ENV PYTHONPATH=/var/workspace
ENV PROJECT_ROOT=/var/workspace
COPY docker/jupyter /root/.jupyter

# 로그 디렉토리 생성
RUN mkdir -p /var/volumes/log

# -----------------------------------------------------------------------------
### ✅ SERVER COMMON Configuration
# -----------------------------------------------------------------------------
ENV LANG="ko_KR.UTF-8"
RUN ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
    echo "Asia/Seoul" > /etc/timezone

# 필수 패키지 설치 (logrotate 추가)
RUN apt-get update && \
    apt-get install -y \
    gcc \
    python3-dev \
    supervisor \
    logrotate \
    cron && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 나눔고딕 설치 (패키지)
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-nanum fontconfig && \
    fc-cache -f -v && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN conda install -y setuptools

# -----------------------------------------------------------------------------
### ✅ Poetry 설정
# -----------------------------------------------------------------------------
RUN pip install --upgrade pip setuptools wheel && \
    pip install poetry==1.8.5 && \
    poetry config virtualenvs.create false && \
    poetry config warnings.export false

# Entrypoint 및 스크립트 설정
COPY docker/entrypoint.sh /var/entrypoint.sh
COPY docker/logrotate.sh /var/logrotate.sh
RUN chmod +x /var/entrypoint.sh && \
    chmod +x /var/logrotate.sh

# Supervisor 설정
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Logrotate 환경 변수
ENV CRON_EXPR="* * * * *"
ENV LOGROTATE_LOGFILES="/var/volumes/log/*/*.log"
ENV LOGROTATE_FILESIZE="10M"
ENV LOGROTATE_FILENUM="5"
ENV LOGROTATE_INTERVAL="3600"

# -----------------------------------------------------------------------------
### ✅ 2 단계: "logrotate" 이미지에서 필요한 파일 복사 (선택사항)
# -----------------------------------------------------------------------------
# realz/logrotate 이미지를 사용하지 않고 직접 logrotate 설정
FROM base AS logrotate_base

# -----------------------------------------------------------------------------
### ✅ 3 단계: "배포 환경" (Production)
# -----------------------------------------------------------------------------
FROM logrotate_base AS production
COPY . /var/workspace
COPY docker/jupyter /root/.jupyter
WORKDIR /var/workspace
ENV PYTHONPATH=/var/workspace
ENV PROJECT_ROOT=/var/workspace
ENV ENV_MODE=production

RUN poetry install --no-root
ENTRYPOINT ["/bin/bash", "/var/entrypoint.sh"]

# -----------------------------------------------------------------------------
### ✅ 4 단계: "개발 환경" (Development)
# -----------------------------------------------------------------------------
FROM logrotate_base AS development
COPY pyproject.toml poetry.lock* /var/workspace/
WORKDIR /var/workspace

RUN poetry install --no-root

ENTRYPOINT ["/bin/bash", "/var/entrypoint.sh"]