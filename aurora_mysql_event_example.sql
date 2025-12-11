-- AWS Aurora MySQL EVENT 생성 예제
-- 사용 전에 Parameter Group에서 event_scheduler = ON 설정 필요

-- ============================================
-- 1. EVENT Scheduler 상태 확인
-- ============================================
SHOW VARIABLES LIKE 'event_scheduler';

-- ============================================
-- 2. EVENT 생성 예제
-- ============================================

-- 예제 1: 매일 자정에 오래된 로그 삭제
CREATE EVENT IF NOT EXISTS daily_log_cleanup
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_DATE + INTERVAL 1 DAY
COMMENT '매일 오래된 로그 삭제 (30일 이상)'
DO
  BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
      -- 에러 발생 시 로그 기록
      INSERT INTO event_error_log (event_name, error_time, error_message)
      VALUES ('daily_log_cleanup', NOW(), CONCAT('Error: ', SQLSTATE, ' - ', SQLERRM));
    END;

    -- 30일 이상 된 로그 삭제
    DELETE FROM access_logs
    WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY);

    -- 실행 로그 기록
    INSERT INTO event_execution_log (event_name, executed_at, status, records_affected)
    VALUES ('daily_log_cleanup', NOW(), 'success', ROW_COUNT());
  END;

-- 예제 2: 매시간 통계 업데이트
CREATE EVENT IF NOT EXISTS hourly_stats_update
ON SCHEDULE EVERY 1 HOUR
STARTS DATE_FORMAT(NOW(), '%Y-%m-%d %H:00:00') + INTERVAL 1 HOUR
COMMENT '매시간 통계 데이터 업데이트'
DO
  BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
      INSERT INTO event_error_log (event_name, error_time, error_message)
      VALUES ('hourly_stats_update', NOW(), CONCAT('Error: ', SQLSTATE));
    END;

    -- 통계 업데이트 프로시저 호출
    CALL update_hourly_statistics();

    INSERT INTO event_execution_log (event_name, executed_at, status)
    VALUES ('hourly_stats_update', NOW(), 'success');
  END;

-- 예제 3: 주간 리포트 생성 (매주 월요일 오전 9시)
CREATE EVENT IF NOT EXISTS weekly_report_generation
ON SCHEDULE EVERY 1 WEEK
STARTS '2025-12-15 09:00:00'
COMMENT '매주 월요일 주간 리포트 생성'
DO
  BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
      INSERT INTO event_error_log (event_name, error_time, error_message)
      VALUES ('weekly_report_generation', NOW(), CONCAT('Error: ', SQLSTATE));
    END;

    CALL generate_weekly_report();

    INSERT INTO event_execution_log (event_name, executed_at, status)
    VALUES ('weekly_report_generation', NOW(), 'success');
  END;

-- 예제 4: 매일 새벽 2시에 데이터베이스 최적화
CREATE EVENT IF NOT EXISTS daily_maintenance
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_DATE + INTERVAL 1 DAY + INTERVAL 2 HOUR
COMMENT '매일 새벽 2시 데이터베이스 유지보수'
DO
  BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
      INSERT INTO event_error_log (event_name, error_time, error_message)
      VALUES ('daily_maintenance', NOW(), CONCAT('Error: ', SQLSTATE));
    END;

    -- 테이블 최적화 (주의: 큰 테이블의 경우 시간이 오래 걸릴 수 있음)
    OPTIMIZE TABLE large_table;

    -- 인덱스 통계 업데이트
    ANALYZE TABLE large_table;

    INSERT INTO event_execution_log (event_name, executed_at, status)
    VALUES ('daily_maintenance', NOW(), 'success');
  END;

-- 예제 5: 매 5분마다 세션 타임아웃 체크
CREATE EVENT IF NOT EXISTS session_cleanup
ON SCHEDULE EVERY 5 MINUTE
COMMENT '5분마다 만료된 세션 정리'
DO
  BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
      INSERT INTO event_error_log (event_name, error_time, error_message)
      VALUES ('session_cleanup', NOW(), CONCAT('Error: ', SQLSTATE));
    END;

    -- 30분 이상 비활성 세션 삭제
    DELETE FROM user_sessions
    WHERE last_activity < DATE_SUB(NOW(), INTERVAL 30 MINUTE);

    INSERT INTO event_execution_log (event_name, executed_at, status, records_affected)
    VALUES ('session_cleanup', NOW(), 'success', ROW_COUNT());
  END;

-- 예제 6: Aurora 멀티 마스터 모드 고려 (리더에서만 실행)
CREATE EVENT IF NOT EXISTS leader_only_task
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_DATE + INTERVAL 1 DAY
COMMENT '리더 인스턴스에서만 실행되는 작업'
DO
  BEGIN
    -- 리더 인스턴스 확인 (read_only = 0)
    IF @@read_only = 0 THEN
      BEGIN
        DECLARE EXIT HANDLER FOR SQLEXCEPTION
        BEGIN
          INSERT INTO event_error_log (event_name, error_time, error_message)
          VALUES ('leader_only_task', NOW(), CONCAT('Error: ', SQLSTATE));
        END;

        -- 리더에서만 실행할 작업
        CALL leader_specific_procedure();

        INSERT INTO event_execution_log (event_name, executed_at, status)
        VALUES ('leader_only_task', NOW(), 'success');
      END;
    END IF;
  END;

-- ============================================
-- 3. EVENT 로깅 테이블 생성 (선택사항)
-- ============================================

-- EVENT 실행 로그 테이블
CREATE TABLE IF NOT EXISTS event_execution_log (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  event_name VARCHAR(100) NOT NULL,
  executed_at DATETIME NOT NULL,
  status VARCHAR(20) NOT NULL,
  records_affected INT DEFAULT 0,
  execution_time_ms INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_event_name (event_name),
  INDEX idx_executed_at (executed_at),
  INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- EVENT 에러 로그 테이블
CREATE TABLE IF NOT EXISTS event_error_log (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  event_name VARCHAR(100) NOT NULL,
  error_time DATETIME NOT NULL,
  error_message TEXT,
  sql_state VARCHAR(5),
  error_code INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_event_name (event_name),
  INDEX idx_error_time (error_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- 4. EVENT 관리 명령어
-- ============================================

-- 모든 EVENT 목록 조회
SHOW EVENTS;

-- 특정 데이터베이스의 EVENT 조회
SHOW EVENTS FROM your_database;

-- EVENT 상세 정보 조회
SHOW CREATE EVENT daily_log_cleanup;

-- information_schema를 통한 EVENT 조회
SELECT
  EVENT_NAME,
  EVENT_DEFINITION,
  EVENT_TYPE,
  EXECUTE_AT,
  INTERVAL_VALUE,
  INTERVAL_FIELD,
  STATUS,
  ON_COMPLETION,
  CREATED,
  LAST_ALTERED,
  LAST_EXECUTED,
  NEXT_EXECUTION_TIME
FROM information_schema.EVENTS
WHERE EVENT_SCHEMA = DATABASE()
ORDER BY EVENT_NAME;

-- EVENT 수정 예제
ALTER EVENT daily_log_cleanup
ON SCHEDULE EVERY 2 DAY
COMMENT '2일마다 오래된 로그 삭제 (60일 이상)'
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

-- ============================================
-- 5. 권한 설정
-- ============================================

-- EVENT 생성 권한 부여
-- GRANT EVENT ON your_database.* TO 'event_user'@'%';

-- 현재 사용자 권한 확인
SHOW GRANTS FOR CURRENT_USER();

-- ============================================
-- 6. 모니터링 쿼리
-- ============================================

-- EVENT 실행 통계 조회
SELECT
  event_name,
  COUNT(*) as execution_count,
  SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
  SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_count,
  AVG(execution_time_ms) as avg_execution_time_ms,
  MAX(executed_at) as last_execution
FROM event_execution_log
WHERE executed_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY event_name
ORDER BY execution_count DESC;

-- 최근 에러 조회
SELECT
  event_name,
  error_time,
  error_message,
  sql_state,
  error_code
FROM event_error_log
ORDER BY error_time DESC
LIMIT 50;

-- EVENT 실행 이력 조회
SELECT
  event_name,
  executed_at,
  status,
  records_affected,
  execution_time_ms
FROM event_execution_log
ORDER BY executed_at DESC
LIMIT 100;
