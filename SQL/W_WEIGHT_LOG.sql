DROP TABLE IF EXISTS `W_WEIGHT_LOG`;
CREATE TABLE `W_WEIGHT_LOG` (
  `LOG_DATETIME` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'ログ日付',
  `LOG_PLACE` VARCHAR(100) NOT NULL COMMENT '計測場所',
  `LOG_WEIGHT` decimal(18,13) NOT NULL COMMENT '計測重量',
  PRIMARY KEY (`LOG_DATETIME`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='重量生ログ';