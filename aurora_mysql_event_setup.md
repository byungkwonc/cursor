# AWS Aurora MySQL EVENT 설정 가이드

## 목차
1. [Aurora MySQL EVENT 특징](#aurora-mysql-event-특징)
2. [Parameter Group 설정](#parameter-group-설정)
3. [EVENT Scheduler 활성화](#event-scheduler-활성화)
4. [EVENT 생성 및 관리](#event-생성-및-관리)
5. [AWS CLI를 통한 설정](#aws-cli를-통한-설정)
6. [CloudFormation/CDK 예제](#cloudformationcdk-예제)
7. [모니터링 및 트러블슈팅](#모니터링-및-트러블슈팅)

---

## Aurora MySQL EVENT 특징

### 일반 MySQL과의 차이점
- **Parameter Group 관리**: `event_scheduler` 파라미터는 Parameter Group을 통해 관리됩니다
- **권한 제한**: RDS/Aurora는 `SUPER` 권한이 없으므로 일부 제한이 있을 수 있습니다
- **멀티 마스터**: Aurora MySQL은 멀티 마스터 모드에서 EVENT가 각 인스턴스에서 독립적으로 실행됩니다
- **리더/리더리스**: 리더 인스턴스에서만 EVENT가 실행됩니다 (기본 설정)

---

## Parameter Group 설정

### 1. AWS Console을 통한 설정

1. **RDS Console** → **Parameter Groups** 이동
2. 클러스터에 연결된 **DB Parameter Group** 선택
3. `event_scheduler` 파라미터 검색
4. 값을 `ON`으로 설정
5. **Save changes** 클릭
6. 클러스터에 Parameter Group 적용 (재부팅 필요할 수 있음)

### 2. AWS CLI를 통한 설정

```bash
# Parameter Group 생성 (필요한 경우)
aws rds create-db-cluster-parameter-group \
  --db-cluster-parameter-group-name aurora-mysql-event-pg \
  --db-parameter-group-family aurora-mysql8.0 \
  --description "Parameter group for Aurora MySQL EVENT Scheduler"

# event_scheduler 파라미터 설정
aws rds modify-db-cluster-parameter-group \
  --db-cluster-parameter-group-name aurora-mysql-event-pg \
  --parameters "ParameterName=event_scheduler,ParameterValue=ON,ApplyMethod=immediate"

# 클러스터에 Parameter Group 적용
aws rds modify-db-cluster \
  --db-cluster-identifier your-cluster-name \
  --db-cluster-parameter-group-name aurora-mysql-event-pg \
  --apply-immediately
```

### 3. 현재 Parameter Group 확인

```sql
-- MySQL에 접속하여 확인
SHOW VARIABLES LIKE 'event_scheduler';
```

---

## EVENT Scheduler 활성화

### 방법 1: Parameter Group을 통한 영구 설정 (권장)

위의 Parameter Group 설정을 사용하면 클러스터 재시작 후에도 유지됩니다.

### 방법 2: SQL을 통한 임시 설정

```sql
-- 현재 세션에서만 활성화 (재시작 시 초기화됨)
SET GLOBAL event_scheduler = ON;

-- 상태 확인
SHOW VARIABLES LIKE 'event_scheduler';
```

**주의**: Parameter Group 설정이 우선되므로, Parameter Group에서 `OFF`로 설정되어 있으면 SQL로 변경할 수 없습니다.

---

## EVENT 생성 및 관리

### 기본 EVENT 생성 예제

```sql
-- 예제 1: 매일 자정에 로그 정리
CREATE EVENT IF NOT EXISTS daily_log_cleanup
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_DATE + INTERVAL 1 DAY
COMMENT '매일 오래된 로그 삭제'
DO
  BEGIN
    DELETE FROM access_logs
    WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY);

    INSERT INTO event_log (event_name, executed_at, status)
    VALUES ('daily_log_cleanup', NOW(), 'success');
  END;

-- 예제 2: 매시간 통계 업데이트
CREATE EVENT IF NOT EXISTS hourly_stats_update
ON SCHEDULE EVERY 1 HOUR
DO
  BEGIN
    CALL update_hourly_statistics();
  END;

-- 예제 3: 주간 리포트 생성 (매주 월요일 오전 9시)
CREATE EVENT IF NOT EXISTS weekly_report
ON SCHEDULE EVERY 1 WEEK
STARTS '2025-12-15 09:00:00'
DO
  BEGIN
    CALL generate_weekly_report();
  END;
```

### Aurora 멀티 마스터 모드 고려사항

```sql
-- 리더 인스턴스에서만 실행되도록 설정
-- (Aurora MySQL은 기본적으로 리더에서만 EVENT 실행)
CREATE EVENT IF NOT EXISTS leader_only_event
ON SCHEDULE EVERY 1 DAY
DO
  BEGIN
    -- 리더 확인 (선택사항)
    IF @@read_only = 0 THEN
      -- 리더에서만 실행할 작업
      CALL leader_specific_task();
    END IF;
  END;
```

### EVENT 관리 명령어

```sql
-- 모든 EVENT 목록 조회
SHOW EVENTS;

-- 특정 데이터베이스의 EVENT 조회
SHOW EVENTS FROM your_database;

-- EVENT 상세 정보
SHOW CREATE EVENT daily_log_cleanup;

-- EVENT 수정
ALTER EVENT daily_log_cleanup
ON SCHEDULE EVERY 2 DAY
DO
  BEGIN
    DELETE FROM access_logs
    WHERE created_at < DATE_SUB(NOW(), INTERVAL 60 DAY);
  END;

-- EVENT 일시 중지
ALTER EVENT daily_log_cleanup DISABLE;

-- EVENT 재개
ALTER EVENT daily_log_cleanup ENABLE;

-- EVENT 삭제
DROP EVENT IF EXISTS daily_log_cleanup;
```

### 권한 설정

```sql
-- EVENT 생성 권한 부여
GRANT EVENT ON your_database.* TO 'event_user'@'%';

-- 권한 확인
SHOW GRANTS FOR 'event_user'@'%';
```

---

## AWS CLI를 통한 설정

### 스크립트 예제

```bash
#!/bin/bash
# aurora_event_setup.sh

CLUSTER_NAME="your-aurora-cluster"
PARAMETER_GROUP="aurora-mysql-event-pg"
ENDPOINT="your-cluster.cluster-xxxxx.ap-northeast-2.rds.amazonaws.com"
DB_NAME="your_database"
DB_USER="admin"
DB_PASSWORD="your_password"

# Parameter Group 생성 및 설정
aws rds create-db-cluster-parameter-group \
  --db-cluster-parameter-group-name "$PARAMETER_GROUP" \
  --db-parameter-group-family aurora-mysql8.0 \
  --description "Aurora MySQL EVENT Scheduler Parameter Group" \
  2>/dev/null || echo "Parameter Group already exists"

# event_scheduler 활성화
aws rds modify-db-cluster-parameter-group \
  --db-cluster-parameter-group-name "$PARAMETER_GROUP" \
  --parameters "ParameterName=event_scheduler,ParameterValue=ON,ApplyMethod=immediate"

# 클러스터에 적용
aws rds modify-db-cluster \
  --db-cluster-identifier "$CLUSTER_NAME" \
  --db-cluster-parameter-group-name "$PARAMETER_GROUP" \
  --apply-immediately

echo "Parameter Group 설정 완료. 클러스터 재시작이 필요할 수 있습니다."
```

---

## CloudFormation/CDK 예제

### CloudFormation 템플릿

```yaml
Resources:
  # DB Cluster Parameter Group
  AuroraEventParameterGroup:
    Type: AWS::RDS::DBClusterParameterGroup
    Properties:
      DBParameterGroupFamily: aurora-mysql8.0
      Description: Parameter group for Aurora MySQL EVENT Scheduler
      Parameters:
        event_scheduler: ON

  # Aurora MySQL Cluster
  AuroraMySQLCluster:
    Type: AWS::RDS::DBCluster
    Properties:
      Engine: aurora-mysql
      EngineVersion: 8.0.mysql_aurora.3.02.0
      DBClusterIdentifier: aurora-mysql-cluster
      MasterUsername: admin
      MasterUserPassword: !Ref MasterPassword
      DBClusterParameterGroupName: !Ref AuroraEventParameterGroup
      DatabaseName: myapp
      BackupRetentionPeriod: 7
      PreferredBackupWindow: "03:00-04:00"
```

### AWS CDK (TypeScript) 예제

```typescript
import * as rds from 'aws-cdk-lib/aws-rds';

// Parameter Group 생성
const parameterGroup = new rds.ParameterGroup(this, 'AuroraEventParameterGroup', {
  engine: rds.DatabaseClusterEngine.auroraMysql({
    version: rds.AuroraMysqlEngineVersion.VER_3_02_0,
  }),
  parameters: {
    event_scheduler: 'ON',
  },
});

// Aurora Cluster 생성
const cluster = new rds.DatabaseCluster(this, 'AuroraMySQLCluster', {
  engine: rds.DatabaseClusterEngine.auroraMysql({
    version: rds.AuroraMysqlEngineVersion.VER_3_02_0,
  }),
  instanceProps: {
    instanceType: ec2.InstanceType.of(ec2.InstanceClass.R5, ec2.InstanceSize.LARGE),
    vpcSubnets: {
      subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
    },
    vpc: vpc,
  },
  parameterGroup: parameterGroup,
  defaultDatabaseName: 'myapp',
});
```

---

## 모니터링 및 트러블슈팅

### CloudWatch 모니터링

```sql
-- EVENT 실행 로그 테이블 생성
CREATE TABLE IF NOT EXISTS event_execution_log (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  event_name VARCHAR(100) NOT NULL,
  executed_at DATETIME NOT NULL,
  status VARCHAR(20) NOT NULL,
  error_message TEXT,
  execution_time_ms INT,
  INDEX idx_event_name (event_name),
  INDEX idx_executed_at (executed_at)
);

-- EVENT에 로깅 추가
CREATE EVENT IF NOT EXISTS monitored_event
ON SCHEDULE EVERY 1 HOUR
DO
  BEGIN
    DECLARE start_time BIGINT;
    DECLARE end_time BIGINT;
    DECLARE error_msg TEXT DEFAULT NULL;

    SET start_time = UNIX_TIMESTAMP(NOW(3)) * 1000;

    BEGIN
      DECLARE EXIT HANDLER FOR SQLEXCEPTION
      BEGIN
        GET DIAGNOSTICS CONDITION 1
          error_msg = MESSAGE_TEXT;
        SET end_time = UNIX_TIMESTAMP(NOW(3)) * 1000;
        INSERT INTO event_execution_log
        (event_name, executed_at, status, error_message, execution_time_ms)
        VALUES ('monitored_event', NOW(), 'error', error_msg, end_time - start_time);
      END;

      -- 실제 작업 수행
      CALL your_procedure();

      SET end_time = UNIX_TIMESTAMP(NOW(3)) * 1000;
      INSERT INTO event_execution_log
      (event_name, executed_at, status, execution_time_ms)
      VALUES ('monitored_event', NOW(), 'success', end_time - start_time);
    END;
  END;
```

### EVENT 상태 확인

```sql
-- 실행 중인 EVENT 확인
SELECT * FROM information_schema.EVENTS
WHERE EVENT_SCHEMA = 'your_database';

-- EVENT 실행 이력 확인
SELECT * FROM event_execution_log
ORDER BY executed_at DESC
LIMIT 100;
```

### 일반적인 문제 해결

1. **EVENT가 실행되지 않음**
   ```sql
   -- EVENT Scheduler 상태 확인
   SHOW VARIABLES LIKE 'event_scheduler';

   -- EVENT 활성화 상태 확인
   SELECT EVENT_NAME, STATUS, LAST_EXECUTED, NEXT_EXECUTION_TIME
   FROM information_schema.EVENTS
   WHERE EVENT_SCHEMA = 'your_database';
   ```

2. **권한 오류**
   ```sql
   -- 현재 사용자 권한 확인
   SHOW GRANTS FOR CURRENT_USER();

   -- EVENT 권한 부여
   GRANT EVENT ON your_database.* TO 'your_user'@'%';
   FLUSH PRIVILEGES;
   ```

3. **Parameter Group 변경이 적용되지 않음**
   - 클러스터 재시작이 필요할 수 있습니다
   - `apply-immediately` 옵션 사용 확인

---

## 보안 고려사항

1. **최소 권한 원칙**: EVENT 생성에 필요한 최소한의 권한만 부여
2. **로깅**: 모든 EVENT 실행을 로깅하여 감사 추적 가능
3. **에러 처리**: EVENT 내부에서 적절한 에러 핸들링 구현
4. **네트워크 보안**: Aurora는 VPC 내부에서만 접근 가능하도록 설정

---

## 참고 자료

- [AWS Aurora MySQL 문서](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraMySQL.Overview.html)
- [MySQL EVENT Scheduler 문서](https://dev.mysql.com/doc/refman/8.0/en/event-scheduler.html)
- [RDS Parameter Groups](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithParamGroups.html)

