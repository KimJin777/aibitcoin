"""
비트코인 AI 자동매매 시스템 메인 실행 파일
"""

import time
import pyupbit
from config.settings import validate_api_keys, UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY, ANALYSIS_INTERVAL
from data.market_data import get_market_data
from data.news_data import get_bitcoin_news, analyze_news_sentiment, get_news_summary
from data.screenshot import capture_upbit_screenshot, create_images_directory
from analysis.technical_indicators import calculate_technical_indicators
from analysis.ai_analysis import create_market_analysis_data, ai_trading_decision_with_indicators, ai_trading_decision_with_vision
from trading.account import get_investment_status, get_pending_orders, get_recent_orders
from trading.execution import execute_trading_decision
from utils.logger import get_logger
from database.connection import init_database
from database.trade_recorder import save_market_data_record, save_system_log_record

def main_trading_cycle_with_vision(upbit, logger):
    """Vision API가 포함된 메인 트레이딩 사이클"""
    print("=" * 60)
    print("비트코인 AI 자동매매 시스템 시작 (Vision API + 기술적 지표 + 공포탐욕지수 + 뉴스 분석)")
    print("=" * 60)
    
    try:
        # 시장 데이터 수집 (기술적 지표, 공포탐욕지수 포함)
        daily_df, minute_df, current_price, orderbook, fear_greed_data = get_market_data()
        
        # 기술적 지표 계산
        if daily_df is not None:
            daily_df = calculate_technical_indicators(daily_df)
        if minute_df is not None:
            minute_df = calculate_technical_indicators(minute_df)
        
        # 뉴스 데이터 수집 및 분석
        analyzed_news = None
        news_data = get_bitcoin_news()
        if news_data:
            analyzed_news = analyze_news_sentiment(news_data)
            if analyzed_news:
                news_summary = get_news_summary(analyzed_news)
        
        # 투자 상태 조회
        investment_status = get_investment_status(upbit)
        
        # AI 분석용 데이터 생성 (기술적 지표, 공포탐욕지수, 뉴스 포함)
        market_data = create_market_analysis_data(daily_df, minute_df, current_price, orderbook, fear_greed_data, analyzed_news)
        
        # 차트 스크린샷 캡처 및 base64 인코딩
        print("📸 차트 스크린샷을 캡처합니다...")
        try:
            create_images_directory()
            screenshot_result = capture_upbit_screenshot()
            if screenshot_result:
                filepath, chart_image_base64 = screenshot_result
                print(f"✅ 차트 스크린샷 캡처 완료: {filepath}")
                
                # AI 매매 결정 (Vision API 포함)
                decision = ai_trading_decision_with_vision(market_data, chart_image_base64)
            else:
                print("⚠️ 차트 스크린샷 캡처 실패, 기존 방식으로 진행합니다.")
                decision = ai_trading_decision_with_indicators(market_data)
        except Exception as e:
            print(f"⚠️ 차트 스크린샷 캡처 중 오류: {e}")
            print("기존 방식으로 진행합니다.")
            decision = ai_trading_decision_with_indicators(market_data)
        
        # 매매 실행
        execution_result = execute_trading_decision(upbit, decision, investment_status, market_data)
        
        if execution_result and execution_result.get('success', False):
            print("✅ 매매 실행 완료")
        else:
            print("❌ 매매 실행 실패 또는 건너뜀")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        logger.error(f"메인 트레이딩 사이클 오류: {e}")

def main_trading_cycle_with_indicators(upbit, logger):
    """기술적 지표가 포함된 메인 트레이딩 사이클 (기존 방식)"""
    print("=" * 60)
    print("비트코인 AI 자동매매 시스템 시작 (기술적 지표 + 공포탐욕지수 + 뉴스 분석 포함)")
    print("=" * 60)
    
    try:
        # 시장 데이터 수집 (기술적 지표, 공포탐욕지수 포함)
        daily_df, minute_df, current_price, orderbook, fear_greed_data = get_market_data()
        
        # 기술적 지표 계산
        if daily_df is not None:
            daily_df = calculate_technical_indicators(daily_df)
        if minute_df is not None:
            minute_df = calculate_technical_indicators(minute_df)
        
        # 뉴스 데이터 수집 및 분석
        analyzed_news = None
        news_data = get_bitcoin_news()
        if news_data:
            analyzed_news = analyze_news_sentiment(news_data)
            if analyzed_news:
                news_summary = get_news_summary(analyzed_news)
        
        # 투자 상태 조회
        investment_status = get_investment_status(upbit)
        
        # AI 분석용 데이터 생성 (기술적 지표, 공포탐욕지수, 뉴스 포함)
        market_data = create_market_analysis_data(daily_df, minute_df, current_price, orderbook, fear_greed_data, analyzed_news)
        
        # AI 매매 결정 (기술적 지표, 공포탐욕지수, 뉴스 포함)
        decision = ai_trading_decision_with_indicators(market_data)
        
        # 매매 실행
        execution_result = execute_trading_decision(upbit, decision, investment_status, market_data)
        
        if execution_result and execution_result.get('success', False):
            print("✅ 매매 실행 완료")
        else:
            print("❌ 매매 실행 실패 또는 건너뜀")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        logger.error(f"메인 트레이딩 사이클 오류: {e}")

def main():
    """메인 함수"""
    print("🚀 비트코인 AI 자동매매 시스템을 시작합니다...")
    
    # API 키 검증
    try:
        validate_api_keys()
        print("✅ API 키 검증 완료")
    except ValueError as e:
        print(f"❌ API 키 오류: {e}")
        print("💡 .env 파일에 필요한 API 키들을 설정해주세요.")
        return
    
    # 로거 설정
    logger = get_logger()
    
    # 데이터베이스 초기화
    print("🗄️ 데이터베이스 초기화 중...")
    if init_database():
        print("✅ 데이터베이스 초기화 완료")
    else:
        print("❌ 데이터베이스 초기화 실패")
        print("💡 MySQL 서버가 실행 중인지 확인해주세요.")
        return
    
    # 업비트 연결
    upbit = pyupbit.Upbit(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)
    
    print(f"⏰ 분석 간격: {ANALYSIS_INTERVAL}초 ({ANALYSIS_INTERVAL/60:.1f}분)")
    print("🔄 자동매매를 시작합니다...")
    print("💡 Ctrl+C를 눌러서 프로그램을 종료할 수 있습니다.")
    print()
    
    while True:
        try:
            # 메인 트레이딩 사이클 실행 (Vision API 포함)
            main_trading_cycle_with_vision(upbit, logger)
            
            print("\n" + "=" * 60)
            print(f"⏰ {ANALYSIS_INTERVAL/60:.1f}분 후 다음 분석을 시작합니다...")
            print("=" * 60 + "\n")
            time.sleep(ANALYSIS_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n👋 프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"❌ 예상치 못한 오류 발생: {e}")
            logger.error(f"예상치 못한 오류: {e}")
            print("🔄 1분 후 재시도합니다...")
            time.sleep(60)

if __name__ == "__main__":
    main()
