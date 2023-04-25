DROP TRIGGER IF EXISTS WORK_OUT_TRAN_LOG; 

DELIMITER $$ 
CREATE TRIGGER WORK_OUT_TRAN_LOG AFTER 
INSERT 
  ON W_WEIGHT_LOG FOR EACH ROW 
BEGIN 

  DECLARE $before_weight decimal (18, 13) DEFAULT 0; -- 前回重量
  DECLARE $limit_over_weight decimal (18, 13) DEFAULT 0; -- 重量許容域上限
  DECLARE $limit_low_weight decimal (18, 13) DEFAULT 0; -- 重量許容域下限
  DECLARE $drunked_weight decimal (18, 13) DEFAULT 0; -- 差分重量

-- 投稿件数をカウントする
SELECT
  W_WEIGHT_LOG.LOG_WEIGHT INTO $before_weight
FROM
  W_WEIGHT_LOG 
WHERE
  LOG_PLACE = NEW.LOG_PLACE 
ORDER BY
  LOG_DATETIME DESC 
LIMIT
  1 OFFSET 1; 

SET $limit_over_weight = $before_weight -5;
SET $limit_low_weight = $before_weight - 300;

IF $limit_low_weight < NEW.LOG_WEIGHT AND NEW.LOG_WEIGHT < $limit_over_weight THEN 
  SET
    $drunked_weight = $before_weight - NEW.LOG_WEIGHT; 

  INSERT INTO T_DRUNKED_LOG(LOG_PLACE, DRUNKED_WEIGHT) 
    VALUES (NEW.LOG_PLACE, $drunked_weight); 

END IF;

END $$ 

DELIMITER ;
