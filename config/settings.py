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

# Ollama 설정
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava:7b")

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
VISION_API_TIMEOUT = 300  # Vision API 호출 타임아웃 (초)
VISION_API_MAX_TOKENS = 50  # Vision API 최대 출력 토큰 수
VISION_API_TEMPERATURE = 0.1  # Vision API temperature 설정

# 스크린샷 최적화/대기값 (증가)
SCREENSHOT_WAIT_TIME = 60  # 페이지 로딩 대기 시간 (초)
SCREENSHOT_ADDITIONAL_WAIT = 10  # 추가 대기 시간 (초)
SCREENSHOT_MENU_WAIT = 8  # 메뉴 대기 시간 (초)
SCREENSHOT_CHART_WAIT = 8  # 차트 업데이트 대기 시간 (초)
SCREENSHOT_MAX_SIZE_MB = 2.0  # 스크린샷 최대 크기 (MB)
SCREENSHOT_QUALITY = 85  # 스크린샷 품질 (0-100)

# 실행 설정
ANALYSIS_INTERVAL = 600  # 분석 간격 (초)
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

# 브라우저 최적화 설정 (테스트용: 실제 브라우저 표시 및 렌더링 활성화)
BROWSER_HEADLESS = False  # 헤드리스 비활성화 → 브라우저 창 표시
BROWSER_DISABLE_IMAGES = False  # 이미지 로딩 활성화
BROWSER_DISABLE_JS = False  # JavaScript 활성화
BROWSER_DISABLE_CSS = False  # CSS 활성화
BROWSER_PAGE_LOAD_STRATEGY = 'eager'  # 페이지 로드 전략

# 차트 설정 옵션
ADD_BOLLINGER_BANDS = True  # 볼린저 밴드 추가 (정확한 XPath 사용)

# 스크린샷 타겟 및 동작용 XPath (환경변수로 덮어쓰기 가능)
TIMEFRAME_MENU_BUTTON_XPATH = os.getenv(
    "TIMEFRAME_MENU_BUTTON_XPATH",
    "/html/body/div[1]/div[2]/div[3]/div/section[1]/article[1]/div/span[2]/div/div/div[1]/div[1]/div/cq-menu[1]/span/cq-clickable",
)
TIMEFRAME_1H_ITEM_XPATH = os.getenv(
    "TIMEFRAME_1H_ITEM_XPATH",
    "/html/body/div[1]/div[2]/div[3]/div/section[1]/article[1]/div/span[2]/div/div/div[1]/div[1]/div/cq-menu[1]/cq-menu-dropdown/cq-item[8]",
)
CHART_SETTINGS_BUTTON_XPATH = os.getenv(
    "CHART_SETTINGS_BUTTON_XPATH",
    "/html/body/div[1]/div[2]/div[3]/div/section[1]/article[1]/div/span[2]/div/div/div[1]/div[1]/div/cq-menu[3]/span",
)
BOLLINGER_OPTION_XPATH = os.getenv(
    "BOLLINGER_OPTION_XPATH",
    "/html/body/div[1]/div[2]/div[3]/div/section[1]/article[1]/div/span[2]/div/div/div[1]/div[1]/div/cq-menu[3]/cq-menu-dropdown/cq-scroll/cq-studies/cq-studies-content/cq-item[2]",
)
CHART_XPATH = os.getenv(
    "CHART_XPATH",
    "/html/body/div[1]/div[2]/div[3]/div/section[1]/article[1]/div/span[2]/div/div/div[2]/div[1]",
)
STRICT_CHART_CAPTURE = True  # True면 지정 XPath 미발견 시 오류로 중단

def validate_api_keys():
    """API 키 유효성 검사"""
    missing_keys = []
    
    if not UPBIT_ACCESS_KEY:
        missing_keys.append("UPBIT_ACCESS_KEY")
    if not UPBIT_SECRET_KEY:
        missing_keys.append("UPBIT_SECRET_KEY")
    # Google API 키는 Ollama 사용 시 필요 없음
    # if not GOOGLE_API_KEY:
    #     missing_keys.append("GOOGLE_API_KEY")
    
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
