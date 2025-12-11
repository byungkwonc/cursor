-- MySQL EVENT 생성 예제
-- EVENT Scheduler가 활성화되어 있어야 합니다 (기본적으로 비활성화)

-- 1. EVENT Scheduler 활성화 확인 및 설정
-- 현재 상태 확인
SHOW VARIABLES LIKE 'event_scheduler';

-- EVENT Scheduler 활성화 (서버 재시작 시 자동으로 활성화하려면 my.cnf에 추가)
SET GLOBAL event_scheduler = ON;

-- 2. EVENT 생성 예제

-- 예제 1: 매일 자정에 실행되는 EVENT
CREATE EVENT IF NOT EXISTS daily_cleanup
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_DATE + INTERVAL 1 DAY
DO
  BEGIN
    -- 여기에 실행할 SQL 문을 작성
    DELETE FROM logs WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY);
  END;

-- 예제 2: 매시간 실행되는 EVENT
CREATE EVENT IF NOT EXISTS hourly_backup
ON SCHEDULE EVERY 1 HOUR
DO
  BEGIN
    -- 백업 작업 등
    INSERT INTO backup_log (backup_time, status) VALUES (NOW(), 'completed');
  END;

-- 예제 3: 특정 시간에 한 번만 실행되는 EVENT
CREATE EVENT IF NOT EXISTS one_time_task
ON SCHEDULE AT '2025-12-15 10:00:00'
DO
  BEGIN
    -- 특정 작업 수행
    UPDATE users SET status = 'active' WHERE last_login > DATE_SUB(NOW(), INTERVAL 7 DAY);
  END;

-- 예제 4: 매주 월요일 오전 9시에 실행
CREATE EVENT IF NOT EXISTS weekly_report
ON SCHEDULE EVERY 1 WEEK
STARTS '2025-12-15 09:00:00'
DO
  BEGIN
    -- 주간 리포트 생성
    CALL generate_weekly_report();
  END;

-- 3. EVENT 관리 명령어

-- 모든 EVENT 목록 조회
SHOW EVENTS;

-- 특정 EVENT 상세 정보 조회
SHOW CREATE EVENT daily_cleanup;

-- EVENT 수정
ALTER EVENT daily_cleanup
ON SCHEDULE EVERY 2 DAY
DO
  BEGIN
    DELETE FROM logs WHERE created_at < DATE_SUB(NOW(), INTERVAL 60 DAY);
  END;

-- EVENT 일시 중지
ALTER EVENT daily_cleanup DISABLE;

-- EVENT 재개
ALTER EVENT daily_cleanup ENABLE;

-- EVENT 삭제
DROP EVENT IF EXISTS daily_cleanup;

-- 4. EVENT 권한 확인
-- EVENT를 생성하려면 EVENT 권한이 필요합니다
-- 권한 부여 예제:
-- GRANT EVENT ON database_name.* TO 'user_name'@'localhost';

-- 현재 사용자의 권한 확인
SHOW GRANTS FOR CURRENT_USER();

