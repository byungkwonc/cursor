# AWS Aurora MySQL EVENT 설정 가이드

이 디렉토리에는 AWS Aurora MySQL에서 EVENT Scheduler를 설정하고 사용하는 방법에 대한 가이드와 예제가 포함되어 있습니다.

## 파일 목록

- **`aurora_mysql_event_setup.md`** - 상세한 설정 가이드 (한글)
- **`aurora_mysql_event_example.sql`** - EVENT 생성 예제 SQL
- **`aurora_event_setup.sh`** - 자동화된 설정 스크립트
- **`README_AURORA_EVENT.md`** - 이 파일

## 빠른 시작

### 1. Parameter Group 설정 (AWS Console)

1. RDS Console → Parameter Groups 이동
2. 클러스터에 연결된 DB Parameter Group 선택
3. `event_scheduler` 파라미터를 `ON`으로 설정
4. 클러스터에 적용 (재부팅 필요할 수 있음)

### 2. 자동화 스크립트 사용

```bash
# 환경 변수 설정
export AURORA_CLUSTER_NAME="your-cluster-name"
export AURORA_ENDPOINT="your-cluster.cluster-xxxxx.ap-northeast-2.rds.amazonaws.com"
export AURORA_DB_NAME="your_database"
export AURORA_DB_USER="admin"
export AURORA_DB_PASSWORD="your_password"
export AWS_REGION="ap-northeast-2"

# 스크립트 실행
chmod +x aurora_event_setup.sh
./aurora_event_setup.sh
```

### 3. 수동 설정 (AWS CLI)

```bash
# Parameter Group 생성
aws rds create-db-cluster-parameter-group \
  --db-cluster-parameter-group-name aurora-mysql-event-pg \
  --db-parameter-group-family aurora-mysql8.0 \
  --description "Aurora MySQL EVENT Scheduler"

# event_scheduler 활성화
aws rds modify-db-cluster-parameter-group \
  --db-cluster-parameter-group-name aurora-mysql-event-pg \
  --parameters "ParameterName=event_scheduler,ParameterValue=ON,ApplyMethod=immediate"

# 클러스터에 적용
aws rds modify-db-cluster \
  --db-cluster-identifier your-cluster-name \
  --db-cluster-parameter-group-name aurora-mysql-event-pg \
  --apply-immediately
```

### 4. EVENT 생성

```bash
# MySQL 접속하여 EVENT 생성
mysql -h your-cluster-endpoint -u admin -p your_database < aurora_mysql_event_example.sql
```

## 주요 차이점 (일반 MySQL vs Aurora MySQL)

| 항목 | 일반 MySQL | Aurora MySQL |
|------|-----------|--------------|
| 설정 방법 | my.cnf 또는 SET GLOBAL | Parameter Group |
| 영구 설정 | my.cnf 파일 | Parameter Group에 저장 |
| 권한 | SUPER 권한 가능 | SUPER 권한 없음 |
| 멀티 마스터 | N/A | 각 인스턴스에서 독립 실행 |

## EVENT 예제

### 매일 자정 로그 정리
```sql
CREATE EVENT daily_log_cleanup
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_DATE + INTERVAL 1 DAY
DO
  DELETE FROM logs WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY);
```

### 매시간 통계 업데이트
```sql
CREATE EVENT hourly_stats
ON SCHEDULE EVERY 1 HOUR
DO
  CALL update_statistics();
```

## 모니터링

```sql
-- EVENT 목록 조회
SHOW EVENTS;

-- EVENT 실행 상태 확인
SELECT * FROM information_schema.EVENTS
WHERE EVENT_SCHEMA = 'your_database';

-- EVENT 실행 로그 확인 (로깅 테이블이 있는 경우)
SELECT * FROM event_execution_log
ORDER BY executed_at DESC
LIMIT 100;
```

## 트러블슈팅

### EVENT가 실행되지 않음

1. **EVENT Scheduler 상태 확인**
   ```sql
   SHOW VARIABLES LIKE 'event_scheduler';
   ```
   - `ON`이어야 합니다

2. **Parameter Group 확인**
   - AWS Console에서 Parameter Group의 `event_scheduler` 값 확인
   - 클러스터에 올바른 Parameter Group이 적용되었는지 확인

3. **EVENT 상태 확인**
   ```sql
   SELECT EVENT_NAME, STATUS, LAST_EXECUTED, NEXT_EXECUTION_TIME
   FROM information_schema.EVENTS
   WHERE EVENT_SCHEMA = 'your_database';
   ```
   - `STATUS`가 `ENABLED`여야 합니다

### 권한 오류

```sql
-- EVENT 권한 부여
GRANT EVENT ON your_database.* TO 'your_user'@'%';
FLUSH PRIVILEGES;

-- 권한 확인
SHOW GRANTS FOR CURRENT_USER();
```

## 참고 자료

- [AWS Aurora MySQL 문서](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraMySQL.Overview.html)
- [MySQL EVENT Scheduler](https://dev.mysql.com/doc/refman/8.0/en/event-scheduler.html)
- [RDS Parameter Groups](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithParamGroups.html)

## 주의사항

1. **클러스터 재시작**: Parameter Group 변경 시 클러스터 재시작이 필요할 수 있습니다
2. **멀티 마스터 모드**: 각 인스턴스에서 EVENT가 독립적으로 실행됩니다
3. **리소스 사용**: EVENT는 데이터베이스 리소스를 사용하므로 모니터링이 필요합니다
4. **에러 처리**: EVENT 내부에서 적절한 에러 핸들링을 구현하세요

