"""
설정 관리 모듈
환경 변수, API 키, 설정값들을 관리합니다.
"""

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# API 키 설정
UPBIT_ACCESS_KEY = os.getenv("UPBIT_ACCESS_KEY")
UPBIT_SECRET_KEY = os.getenv("UPBIT_SECRET_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")

# 트레이딩 설정
TRADING_SYMBOL = "KRW-BTC"
MIN_TRADE_AMOUNT = 5000  # 최소 거래 금액 (원)
TRADE_RATIO = 0.95  # 거래 시 사용할 비율 (95%)
FEE_RATE = 0.0005  # 수수료율 (0.05%)

# 분석 설정
DAILY_DATA_COUNT = 30  # 일봉 데이터 개수
MINUTE_DATA_COUNT = 1440  # 분봉 데이터 개수 (24시간)
TECHNICAL_INDICATORS = [
    'SMA_20', 'SMA_50', 'EMA_12', 'EMA_26',
    'MACD', 'MACD_Signal', 'MACD_Histogram',
    'RSI', 'BB_Upper', 'BB_Middle', 'BB_Lower',
    'Stoch_K', 'Stoch_D', 'Williams_R', 'ATR',
    'ADX', 'OBV', 'ROC', 'CCI'
]

# 뉴스 분석 설정
NEWS_COUNT = 20  # 수집할 뉴스 개수
NEWS_LANGUAGE = "ko"  # 뉴스 언어
NEWS_REGION = "kr"  # 뉴스 지역

# 스크린샷 설정
SCREENSHOT_WINDOW_SIZE = (1920, 1080)
SCREENSHOT_MAX_SIZE_MB = 2.0
SCREENSHOT_QUALITY = 85

# 실행 설정
ANALYSIS_INTERVAL = 300  # 분석 간격 (초)
NEWS_ANALYSIS_INTERVAL = 1800  # 뉴스 분석 간격 (초)

# 데이터베이스 설정
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "gptbitcoin")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "kimjink@@7")

def validate_api_keys():
    """API 키 유효성 검사"""
    missing_keys = []
    
    if not UPBIT_ACCESS_KEY:
        missing_keys.append("UPBIT_ACCESS_KEY")
    if not UPBIT_SECRET_KEY:
        missing_keys.append("UPBIT_SECRET_KEY")
    if not GOOGLE_API_KEY:
        missing_keys.append("GOOGLE_API_KEY")
    
    if missing_keys:
        raise ValueError(f"필수 API 키가 설정되지 않았습니다: {', '.join(missing_keys)}")
    
    return True

def get_trading_config():
    """트레이딩 설정 반환"""
    return {
        'symbol': TRADING_SYMBOL,
        'min_amount': MIN_TRADE_AMOUNT,
        'trade_ratio': TRADE_RATIO,
        'fee_rate': FEE_RATE
    }

def get_analysis_config():
    """분석 설정 반환"""
    return {
        'daily_count': DAILY_DATA_COUNT,
        'minute_count': MINUTE_DATA_COUNT,
        'indicators': TECHNICAL_INDICATORS
    }
