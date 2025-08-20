"""
손절매 관련 쿼리 모듈
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from mysql.connector import Error
import logging
from database.connection import get_db_connection

def get_yesterday_trade_info() -> Optional[Dict[str, Any]]:
    """전날 0시 이후의 첫 구매 기록 조회"""
    try:
        connection = get_db_connection()
        if not connection:
            return None
            
        cursor = connection.cursor(dictionary=True)
        
        # 어제 0시 시간 계산
        yesterday_midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        query = """
        SELECT 
            price as buy_price,
            amount as buy_amount,
            total_value as buy_total,
            timestamp as buy_time
        FROM trades 
        WHERE action = 'buy' 
        AND timestamp >= %s
        ORDER BY timestamp ASC
        LIMIT 1
        """
        
        cursor.execute(query, (yesterday_midnight,))
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            # 어제 0시 이후 구매 기록이 없으면 가장 최근 구매 기록 조회
            cursor = connection.cursor(dictionary=True)
            query = """
            SELECT 
                price as buy_price,
                amount as buy_amount,
                total_value as buy_total,
                timestamp as buy_time
            FROM trades 
            WHERE action = 'buy'
            ORDER BY timestamp DESC
            LIMIT 1
            """
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
        
        return result
            
    except Error as e:
        logging.error(f"거래 기록 조회 오류: {e}")
        return None
