#!/bin/bash

# MySQL EVENT 설정 스크립트
# 사용법: ./mysql_event_setup.sh

echo "MySQL EVENT Scheduler 설정 시작..."

# MySQL 접속 정보 (환경 변수 또는 직접 입력)
MYSQL_USER="${MYSQL_USER:-root}"
MYSQL_PASSWORD="${MYSQL_PASSWORD:-}"
MYSQL_HOST="${MYSQL_HOST:-localhost}"
MYSQL_DATABASE="${MYSQL_DATABASE:-your_database}"

# EVENT Scheduler 활성화
echo "EVENT Scheduler 활성화 중..."
mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h "$MYSQL_HOST" <<EOF
SET GLOBAL event_scheduler = ON;
SHOW VARIABLES LIKE 'event_scheduler';
EOF

# EVENT 생성 (mysql_event_example.sql 파일 사용)
if [ -f "mysql_event_example.sql" ]; then
    echo "EVENT 생성 중..."
    mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h "$MYSQL_HOST" "$MYSQL_DATABASE" < mysql_event_example.sql
    echo "EVENT 생성 완료!"
else
    echo "mysql_event_example.sql 파일을 찾을 수 없습니다."
fi

# 생성된 EVENT 목록 확인
echo "생성된 EVENT 목록:"
mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h "$MYSQL_HOST" "$MYSQL_DATABASE" -e "SHOW EVENTS;"
