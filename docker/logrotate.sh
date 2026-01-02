#!/bin/bash

LOGROTATE_LOGFILES="${LOGROTATE_LOGFILES:?Files for rotating must be given}"
LOGROTATE_FILESIZE="${LOGROTATE_FILESIZE:-10M}"
LOGROTATE_FILENUM="${LOGROTATE_FILENUM:-5}"
LOGROTATE_USER="${LOGROTATE_USER:-root}"
LOGROTATE_GROUP="${LOGROTATE_GROUP:-root}"
LOGROTATE_INTERVAL="${LOGROTATE_INTERVAL:-3600}"

# logrotate 설치 확인
if ! command -v logrotate &> /dev/null; then
    echo "ERROR: logrotate is not installed"
    exit 1
fi

# 로그 파일 회전을 위한 logrotate 설정 생성
cat > /etc/logrotate.d/app-logs << EOF
${LOGROTATE_LOGFILES}
{
  size ${LOGROTATE_FILESIZE}
  missingok
  notifempty
  copytruncate
  rotate ${LOGROTATE_FILENUM}
  su ${LOGROTATE_USER} ${LOGROTATE_GROUP}
  compress
  delaycompress
}
EOF

echo "Logrotate configuration created:"
cat /etc/logrotate.d/app-logs

# logrotate를 주기적으로 실행
while true; do
    echo "[$(date)] Running logrotate..."
    /usr/sbin/logrotate -v /etc/logrotate.d/app-logs 2>&1

    if [ $? -eq 0 ]; then
        echo "[$(date)] Logrotate completed successfully."
    else
        echo "[$(date)] Logrotate failed with exit code $?"
    fi

    echo "[$(date)] Sleeping for ${LOGROTATE_INTERVAL} seconds..."
    sleep ${LOGROTATE_INTERVAL}
done