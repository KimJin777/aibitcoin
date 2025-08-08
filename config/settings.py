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
# Vision API 성능 최적화 설정
VISION_API_TIMEOUT = 20  # Vision API 호출 타임아웃 (초) - 더 짧게
VISION_API_MAX_TOKENS = 200  # Vision API 최대 출력 토큰 수 - 더 적게
VISION_API_TEMPERATURE = 0.2  # Vision API temperature 설정 - 더 낮게

# 스크린샷 최적화 설정
SCREENSHOT_WAIT_TIME = 10  # 페이지 로딩 대기 시간 (초) - 더 짧게
SCREENSHOT_ADDITIONAL_WAIT = 2  # 추가 대기 시간 (초) - 더 짧게
SCREENSHOT_MENU_WAIT = 1  # 메뉴 대기 시간 (초)
SCREENSHOT_CHART_WAIT = 1  # 차트 업데이트 대기 시간 (초) - 더 짧게
SCREENSHOT_MAX_SIZE_MB = 0.5  # 스크린샷 최대 크기 (MB) - 더 작게 설정
SCREENSHOT_QUALITY = 60  # 스크린샷 품질 (0-100) - 더 낮게 설정

# 실행 설정
ANALYSIS_INTERVAL = 300  # 분석 간격 (초)
NEWS_ANALYSIS_INTERVAL = 1800  # 뉴스 분석 간격 (초)

# 데이터베이스 설정
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "gptbitcoin")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "kimjink@@7")

# 전략 개선 적용 설정
STRATEGY_IMPROVEMENT_ENABLED = True  # 전략 개선 적용 비활성화 (성능 최적화)
STRATEGY_IMPROVEMENT_CACHE_TIME = 300  # 전략 개선 캐시 시간 (초)

# 브라우저 최적화 설정
BROWSER_HEADLESS = True  # 헤드리스 모드 활성화
BROWSER_DISABLE_IMAGES = True  # 이미지 로딩 비활성화
BROWSER_DISABLE_JS = True  # JavaScript 비활성화
BROWSER_DISABLE_CSS = True  # CSS 비활성화
BROWSER_PAGE_LOAD_STRATEGY = 'eager'  # 페이지 로드 전략

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
