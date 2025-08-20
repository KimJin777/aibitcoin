"""
MySQL 데이터베이스 연결 모듈
"""

import mysql.connector
from mysql.connector import Error
from typing import Optional
import logging

class DatabaseConnection:
    """MySQL 데이터베이스 연결 클래스"""
    
    def __init__(self, host=None, port=None, database=None, user=None, password=None):
        from config.settings import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
        
        self.host = host or DB_HOST
        self.port = port or DB_PORT
        self.database = database or DB_NAME
        self.user = user or DB_USER
        self.password = password or DB_PASSWORD
        self.connection = None
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """데이터베이스 연결"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                charset='utf8mb4',
                autocommit=True
            )
            
            if self.connection.is_connected():
                self.logger.info("MySQL 데이터베이스 연결 성공")
                return True
            else:
                self.logger.error("MySQL 데이터베이스 연결 실패")
                return False
                
        except Error as e:
            self.logger.error(f"MySQL 연결 오류: {e}")
            return False
    
    def disconnect(self):
        """데이터베이스 연결 해제"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.logger.info("MySQL 데이터베이스 연결 해제")
    
    def create_tables(self):
        """거래 기록 테이블 생성"""
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            
            # 거래 기록 테이블
            create_trades_table = """
            CREATE TABLE IF NOT EXISTS trades (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME NOT NULL,
                decision VARCHAR(10) NOT NULL,
                action VARCHAR(10) NOT NULL,
                price DECIMAL(20, 8) NOT NULL,
                amount DECIMAL(20, 8) NOT NULL,
                total_value DECIMAL(20, 2) NOT NULL,
                fee DECIMAL(20, 2) DEFAULT 0,
                balance_krw DECIMAL(20, 2) NOT NULL,
                balance_btc DECIMAL(20, 8) NOT NULL,
                order_id VARCHAR(100),
                status VARCHAR(20) DEFAULT 'executed',
                confidence DECIMAL(5, 4),
                reasoning TEXT,
                market_data JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # 시장 데이터 테이블
            create_market_data_table = """
            CREATE TABLE IF NOT EXISTS market_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME NOT NULL,
                current_price DECIMAL(20, 2) NOT NULL,
                volume_24h DECIMAL(20, 2),
                change_24h DECIMAL(10, 4),
                rsi DECIMAL(10, 4),
                macd DECIMAL(10, 4),
                macd_signal DECIMAL(10, 4),
                bollinger_upper DECIMAL(20, 2),
                bollinger_lower DECIMAL(20, 2),
                fear_greed_index INT,
                fear_greed_value DECIMAL(10, 4),
                news_sentiment DECIMAL(5, 4),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # 시스템 로그 테이블
            create_system_logs_table = """
            CREATE TABLE IF NOT EXISTS system_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME NOT NULL,
                level VARCHAR(10) NOT NULL,
                message TEXT NOT NULL,
                module VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # 거래 반성 테이블
            create_trading_reflections_table = """
            CREATE TABLE IF NOT EXISTS trading_reflections (
                id INT AUTO_INCREMENT PRIMARY KEY,
                trade_id INT NOT NULL,
                reflection_type ENUM('immediate', 'daily', 'weekly', 'monthly') NOT NULL,
                performance_score DECIMAL(5, 4),
                profit_loss DECIMAL(20, 2),
                profit_loss_percentage DECIMAL(10, 4),
                market_conditions JSON,
                decision_quality_score DECIMAL(5, 4),
                timing_score DECIMAL(5, 4),
                risk_management_score DECIMAL(5, 4),
                ai_analysis TEXT,
                improvement_suggestions TEXT,
                lessons_learned TEXT,
                next_actions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (trade_id) REFERENCES trades(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # 성과 지표 테이블
            create_performance_metrics_table = """
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INT AUTO_INCREMENT PRIMARY KEY,
                period_type ENUM('daily', 'weekly', 'monthly') NOT NULL,
                period_start DATETIME NOT NULL,
                period_end DATETIME NOT NULL,
                total_trades INT NOT NULL,
                winning_trades INT NOT NULL,
                losing_trades INT NOT NULL,
                win_rate DECIMAL(5, 4),
                total_profit_loss DECIMAL(20, 2),
                total_profit_loss_percentage DECIMAL(10, 4),
                max_drawdown DECIMAL(10, 4),
                sharpe_ratio DECIMAL(10, 4),
                average_trade_duration INT,
                best_trade_profit DECIMAL(20, 2),
                worst_trade_loss DECIMAL(20, 2),
                market_condition_performance JSON,
                strategy_performance JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # 학습 인사이트 테이블
            create_learning_insights_table = """
            CREATE TABLE IF NOT EXISTS learning_insights (
                id INT AUTO_INCREMENT PRIMARY KEY,
                insight_type ENUM('pattern', 'strategy', 'risk', 'timing', 'market') NOT NULL,
                insight_title VARCHAR(200) NOT NULL,
                insight_description TEXT NOT NULL,
                confidence_level DECIMAL(5, 4),
                supporting_data JSON,
                applicable_conditions JSON,
                action_items TEXT,
                priority_level ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
                status ENUM('discovered', 'implemented', 'validated', 'archived') DEFAULT 'discovered',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # 전략 개선 이력 테이블
            create_strategy_improvements_table = """
            CREATE TABLE IF NOT EXISTS strategy_improvements (
                id INT AUTO_INCREMENT PRIMARY KEY,
                improvement_type ENUM('parameter', 'condition', 'timing', 'risk') NOT NULL,
                old_value TEXT,
                new_value TEXT,
                reason TEXT,
                expected_impact TEXT,
                implementation_date DATETIME,
                validation_period_days INT DEFAULT 30,
                performance_before JSON,
                performance_after JSON,
                success_metric DECIMAL(5, 4),
                status ENUM('proposed', 'implemented', 'validated', 'reverted') DEFAULT 'proposed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # 테이블이 이미 확실하게 있으므로 테이블 생성쿼리는 주석처리
            # cursor.execute(create_trades_table)
            # cursor.execute(create_market_data_table)
            # cursor.execute(create_system_logs_table)
            # cursor.execute(create_trading_reflections_table)
            # cursor.execute(create_performance_metrics_table)
            # cursor.execute(create_learning_insights_table)
            # cursor.execute(create_strategy_improvements_table)
            
            # self.connection.commit()
            cursor.close()
            
            # self.logger.info("데이터베이스 테이블 생성 완료")
            return True
            
        except Error as e:
            self.logger.error(f"테이블 생성 오류: {e}")
            return False
    
    def get_connection(self):
        """데이터베이스 연결 객체 반환"""
        if not self.connection or not self.connection.is_connected():
            self.connect()
        return self.connection

# 전역 데이터베이스 연결 객체
db_connection = DatabaseConnection()

def get_db_connection():
    """데이터베이스 연결 객체 반환"""
    return db_connection.get_connection()

def init_database():
    """데이터베이스 초기화 및 테이블 생성"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # news 테이블 생성 (없으면 생성)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                data JSON NOT NULL,
                fetched_at DATETIME NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_fetched_at (fetched_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        # 기존 테이블 마이그레이션: fetched_at 컬럼/인덱스 보정
        try:
            cursor.execute("SHOW COLUMNS FROM news LIKE 'fetched_at'")
            column_exists = cursor.fetchone()
            if not column_exists:
                cursor.execute(
                    "ALTER TABLE news ADD COLUMN fetched_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"
                )

            # 인덱스 확인 및 생성
            cursor.execute("SHOW INDEX FROM news WHERE Key_name = %s", ("idx_fetched_at",))
            index_exists = cursor.fetchone()
            if not index_exists:
                cursor.execute("CREATE INDEX idx_fetched_at ON news (fetched_at)")
        except Exception as _e:
            # 마이그레이션 시도 실패는 치명적이지 않으므로 로깅만 하고 계속 진행
            pass
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ 데이터베이스 테이블 초기화 완료")
        return True
        
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 중 오류 발생: {e}")
        return False
