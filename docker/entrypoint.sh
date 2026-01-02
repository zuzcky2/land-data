#!/bin/bash
set -e  # 오류 발생 시 즉시 종료

# 의존성 설치 (루트 프로젝트 제외)
poetry install
#poetry export -f requirements.txt --without-hashes --without-urls --output requirements.txt
#poetry run pip install -r requirements.txt

# Supervisor 실행
exec supervisord -c /etc/supervisor/conf.d/supervisord.conf