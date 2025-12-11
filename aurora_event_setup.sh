#!/bin/bash

# AWS Aurora MySQL EVENT 설정 스크립트
# 사용법: ./aurora_event_setup.sh

set -e  # 에러 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 설정 변수 (환경 변수 또는 직접 수정)
CLUSTER_NAME="${AURORA_CLUSTER_NAME:-your-aurora-cluster}"
PARAMETER_GROUP="${AURORA_PARAMETER_GROUP:-aurora-mysql-event-pg}"
ENDPOINT="${AURORA_ENDPOINT:-your-cluster.cluster-xxxxx.ap-northeast-2.rds.amazonaws.com}"
DB_NAME="${AURORA_DB_NAME:-your_database}"
DB_USER="${AURORA_DB_USER:-admin}"
DB_PASSWORD="${AURORA_DB_PASSWORD:-}"
REGION="${AWS_REGION:-ap-northeast-2}"

echo -e "${GREEN}AWS Aurora MySQL EVENT 설정 시작...${NC}"
echo ""

# 1. AWS CLI 설치 확인
if ! command -v aws &> /dev/null; then
    echo -e "${RED}오류: AWS CLI가 설치되어 있지 않습니다.${NC}"
    echo "설치 방법: https://aws.amazon.com/cli/"
    exit 1
fi

# 2. AWS 자격 증명 확인
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}오류: AWS 자격 증명이 설정되어 있지 않습니다.${NC}"
    echo "aws configure 명령어로 설정하거나 환경 변수를 설정하세요."
    exit 1
fi

echo -e "${YELLOW}현재 AWS 계정:${NC}"
aws sts get-caller-identity --query 'Account' --output text
echo ""

# 3. Parameter Group 생성 또는 확인
echo -e "${YELLOW}1. Parameter Group 확인/생성 중...${NC}"
if aws rds describe-db-cluster-parameter-groups \
    --db-cluster-parameter-group-name "$PARAMETER_GROUP" \
    --region "$REGION" &> /dev/null; then
    echo -e "${GREEN}Parameter Group '$PARAMETER_GROUP'이 이미 존재합니다.${NC}"
else
    echo "Parameter Group 생성 중..."
    aws rds create-db-cluster-parameter-group \
        --db-cluster-parameter-group-name "$PARAMETER_GROUP" \
        --db-parameter-group-family aurora-mysql8.0 \
        --description "Aurora MySQL EVENT Scheduler Parameter Group" \
        --region "$REGION"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Parameter Group 생성 완료!${NC}"
    else
        echo -e "${RED}Parameter Group 생성 실패${NC}"
        exit 1
    fi
fi
echo ""

# 4. event_scheduler 파라미터 설정
echo -e "${YELLOW}2. event_scheduler 파라미터 설정 중...${NC}"
aws rds modify-db-cluster-parameter-group \
    --db-cluster-parameter-group-name "$PARAMETER_GROUP" \
    --parameters "ParameterName=event_scheduler,ParameterValue=ON,ApplyMethod=immediate" \
    --region "$REGION"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}event_scheduler 파라미터 설정 완료!${NC}"
else
    echo -e "${RED}파라미터 설정 실패${NC}"
    exit 1
fi
echo ""

# 5. 클러스터에 Parameter Group 적용
echo -e "${YELLOW}3. 클러스터에 Parameter Group 적용 중...${NC}"
echo -e "${YELLOW}주의: 클러스터 재시작이 필요할 수 있습니다.${NC}"

# 현재 Parameter Group 확인
CURRENT_PG=$(aws rds describe-db-clusters \
    --db-cluster-identifier "$CLUSTER_NAME" \
    --region "$REGION" \
    --query 'DBClusters[0].DBClusterParameterGroup' \
    --output text)

if [ "$CURRENT_PG" != "$PARAMETER_GROUP" ]; then
    echo "Parameter Group 변경 중..."
    aws rds modify-db-cluster \
        --db-cluster-identifier "$CLUSTER_NAME" \
        --db-cluster-parameter-group-name "$PARAMETER_GROUP" \
        --apply-immediately \
        --region "$REGION"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Parameter Group 적용 완료!${NC}"
        echo -e "${YELLOW}클러스터 상태 확인 중...${NC}"

        # 클러스터 상태 확인
        while true; do
            STATUS=$(aws rds describe-db-clusters \
                --db-cluster-identifier "$CLUSTER_NAME" \
                --region "$REGION" \
                --query 'DBClusters[0].Status' \
                --output text)

            echo "현재 상태: $STATUS"

            if [ "$STATUS" == "available" ]; then
                echo -e "${GREEN}클러스터가 정상 상태입니다.${NC}"
                break
            elif [ "$STATUS" == "modifying" ]; then
                echo "변경 중... 10초 후 다시 확인합니다."
                sleep 10
            else
                echo -e "${YELLOW}예상치 못한 상태: $STATUS${NC}"
                break
            fi
        done
    else
        echo -e "${RED}Parameter Group 적용 실패${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}이미 올바른 Parameter Group이 적용되어 있습니다.${NC}"
fi
echo ""

# 6. MySQL 접속하여 EVENT Scheduler 상태 확인
echo -e "${YELLOW}4. EVENT Scheduler 상태 확인 중...${NC}"

if [ -z "$DB_PASSWORD" ]; then
    echo -e "${YELLOW}DB_PASSWORD 환경 변수가 설정되지 않았습니다.${NC}"
    echo "MySQL에 직접 접속하여 다음 명령어를 실행하세요:"
    echo "  SHOW VARIABLES LIKE 'event_scheduler';"
    echo ""
else
    # MySQL 클라이언트 설치 확인
    if ! command -v mysql &> /dev/null; then
        echo -e "${YELLOW}MySQL 클라이언트가 설치되어 있지 않습니다.${NC}"
        echo "다음 명령어로 직접 확인하세요:"
        echo "  mysql -h $ENDPOINT -u $DB_USER -p -e \"SHOW VARIABLES LIKE 'event_scheduler';\""
        echo ""
    else
        echo "EVENT Scheduler 상태 확인 중..."
        mysql -h "$ENDPOINT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" \
            -e "SHOW VARIABLES LIKE 'event_scheduler';" 2>/dev/null || {
            echo -e "${YELLOW}MySQL 접속에 실패했습니다. 수동으로 확인하세요.${NC}"
        }
    fi
fi

# 7. EVENT 생성 (SQL 파일이 있는 경우)
if [ -f "aurora_mysql_event_example.sql" ]; then
    echo ""
    echo -e "${YELLOW}5. EVENT 생성 SQL 파일이 발견되었습니다.${NC}"
    read -p "EVENT를 생성하시겠습니까? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -z "$DB_PASSWORD" ]; then
            echo "다음 명령어로 EVENT를 생성하세요:"
            echo "  mysql -h $ENDPOINT -u $DB_USER -p $DB_NAME < aurora_mysql_event_example.sql"
        else
            if command -v mysql &> /dev/null; then
                echo "EVENT 생성 중..."
                mysql -h "$ENDPOINT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" \
                    < aurora_mysql_event_example.sql 2>/dev/null && {
                    echo -e "${GREEN}EVENT 생성 완료!${NC}"
                    echo ""
                    echo "생성된 EVENT 목록:"
                    mysql -h "$ENDPOINT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" \
                        -e "SHOW EVENTS;" 2>/dev/null || echo "EVENT 목록 조회 실패"
                } || {
                    echo -e "${YELLOW}EVENT 생성 중 오류가 발생했습니다. 수동으로 확인하세요.${NC}"
                }
            else
                echo "MySQL 클라이언트가 없어 EVENT를 생성할 수 없습니다."
            fi
        fi
    fi
fi

echo ""
echo -e "${GREEN}설정 완료!${NC}"
echo ""
echo "다음 단계:"
echo "1. MySQL에 접속하여 EVENT Scheduler 상태 확인:"
echo "   SHOW VARIABLES LIKE 'event_scheduler';"
echo ""
echo "2. EVENT 생성 (aurora_mysql_event_example.sql 파일 사용)"
echo ""
echo "3. 생성된 EVENT 확인:"
echo "   SHOW EVENTS;"

