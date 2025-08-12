"""
비트코인 AI 자동매매 시스템 메인 실행 파일
"""

import time
import os
import sys
import socket
import subprocess
import argparse
from numpy import average
import pyupbit
from config.settings import validate_api_keys, UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY, ANALYSIS_INTERVAL
from data.market_data import get_market_data
from data.news_data import get_bitcoin_news, analyze_news_sentiment, get_news_summary
from data.screenshot import capture_upbit_screenshot, create_images_directory
from analysis.technical_indicators import calculate_technical_indicators
from analysis.ai_analysis import create_market_analysis_data, ai_trading_decision_with_indicators, ai_trading_decision_with_vision
from trading.account import get_investment_status, get_pending_orders, get_recent_orders, get_total_profit_loss
from trading.execution import execute_trading_decision
from utils.logger import get_logger
from database.connection import init_database
from database.trade_recorder import save_market_data_record, save_system_log_record

def _is_port_open(port: int, host: str = "127.0.0.1", timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

def _start_detached_process(args: list[str], cwd: str | None = None) -> None:
    creationflags = 0
    popen_kwargs = {}
    if os.name == "nt":
        # DETACHED_PROCESS (0x00000008) | CREATE_NEW_PROCESS_GROUP (0x00000200)
        creationflags = 0x00000008 | 0x00000200
        popen_kwargs["creationflags"] = creationflags
    else:
        popen_kwargs["start_new_session"] = True
    # 표준 출력/에러 무시하여 메인 콘솔 오염 방지
    subprocess.Popen(
        args,
        cwd=cwd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
        **popen_kwargs,
    )

def start_background_services(logger):
    """스케줄러와 대시보드를 백그라운드로 실행"""
    project_root = os.path.dirname(os.path.abspath(__file__))

    # 1) 스케줄러 실행 (항상 별도 프로세스 시도)
    try:
        _start_detached_process([sys.executable, "scheduler.py"], cwd=project_root)
        logger.info("스케줄러 백그라운드 실행 요청 완료")
    except Exception as e:
        logger.error(f"스케줄러 실행 실패: {e}")

    # 2) 대시보드 실행 (포트 8501이 열려 있으면 건너뜀)
    try:
        if not _is_port_open(8501):
            _start_detached_process([sys.executable, "-m", "streamlit", "run", "dashboard.py", "--server.headless", "true", "--server.port", "8501"], cwd=project_root)
            logger.info("대시보드 백그라운드 실행 요청 완료 (포트 8501)")
        else:
            logger.info("대시보드가 이미 실행 중으로 감지됨 (포트 8501)")
    except Exception as e:
        logger.error(f"대시보드 실행 실패: {e}")

def main_trading_cycle_with_vision(upbit, logger):
    """Vision API가 포함된 메인 트레이딩 사이클"""
    print("=" * 60)
    print("비트코인 AI 자동매매 시스템 시작 (Vision API + 기술적 지표 + 공포탐욕지수 + 뉴스 분석)")
    print("=" * 60)
    
    try:
        # 시장 데이터 수집 (기술적 지표, 공포탐욕지수 포함)
        print("📊 시장 데이터를 수집합니다...")
        daily_df, minute_df, current_price, orderbook, fear_greed_data = get_market_data()
        # print('데이터 조회2222, 비전포함', daily_df, minute_df, current_price, orderbook, fear_greed_data)
        # print('데이터 조회3333, 분봉', minute_df, current_price)

        # 기술적 지표 계산
        if daily_df is not None:
            daily_df = calculate_technical_indicators(daily_df)
        if minute_df is not None:
            minute_df = calculate_technical_indicators(minute_df)
        
        # 뉴스 데이터 수집 및 분석
        print("📰 뉴스 데이터를 분석합니다...")
        analyzed_news = None
        news_data = get_bitcoin_news()
        if news_data:
            analyzed_news = analyze_news_sentiment(news_data)
            if analyzed_news:
                news_summary = get_news_summary(analyzed_news)
        
        # 투자 상태 조회
        print("💰 투자 상태를 확인합니다...")
        investment_status = get_investment_status(upbit)
        
        # AI 분석용 데이터 생성 (기술적 지표, 공포탐욕지수, 뉴스 포함)
        market_data = create_market_analysis_data(daily_df, minute_df, current_price, orderbook, fear_greed_data, analyzed_news)

        # 시장 데이터 저장
        try:
            save_market_data_record(market_data)
        except Exception as e:
            logger.error(f"시장 데이터 저장 실패: {e}")
        
        # 차트 스크린샷 캡처 및 base64 인코딩
        print("📸 차트 스크린샷을 캡처합니다...")
        screenshot_start_time = time.time()
        try:
            create_images_directory()
            screenshot_result = capture_upbit_screenshot()
            screenshot_time = time.time() - screenshot_start_time
            print(f"⏱️ 스크린샷 캡처 시간: {screenshot_time:.2f}초")
            
            if screenshot_result:
                filepath, chart_image_base64 = screenshot_result
                print(f"✅ 차트 스크린샷 캡처 완료: {filepath}")
                
                # AI 매매 결정 (Vision API 포함)
                print("🤖 Vision API를 사용한 AI 분석을 시작합니다...")
                vision_start_time = time.time()
                decision = ai_trading_decision_with_vision(market_data, chart_image_base64)
                vision_time = time.time() - vision_start_time
                print(f"⏱️ Vision API 분석 시간: {vision_time:.2f}초")
                logger.info(f"Vision API 분석 완료 - 스크린샷: {screenshot_time:.2f}초, 분석: {vision_time:.2f}초")
            else:
                print("⚠️ 차트 스크린샷 캡처 실패, 기존 방식으로 진행합니다.")
                decision = ai_trading_decision_with_indicators(market_data)
        except Exception as e:
            print(f"⚠️ 차트 스크린샷 캡처 중 오류: {e}")
            print("기존 방식으로 진행합니다.")
            decision = ai_trading_decision_with_indicators(market_data)
        
        # 매매 실행
        print("💼 매매 결정을 실행합니다...")
        execution_result = execute_trading_decision(upbit, decision, investment_status, market_data)
        
        # 손절수동매매
        # print('데이터 조회2222, 비전포함', daily_df, minute_df, current_price, orderbook, fear_greed_data)
        
        decisionSelf=False
        total_profit_loss = get_total_profit_loss(upbit)
        
        current_btc_value = total_profit_loss['current_price']*total_profit_loss['btc_balance']
        my_btc_value = total_profit_loss['btc_avg_price']*total_profit_loss['btc_balance']
        total_profit_loss_value = my_btc_value - current_btc_value
        # print('분봉 평균', minute_df['High'][0:10].mean(), current_price)
        # print('분봉 ', (minute_df['High'][0:10]))
        # print('이익', total_profit_loss)
        
        # print('비트코인 보유량', total_profit_loss['btc_balance'])
        # btc_current_value = total_profit_loss['current_price']
        # print('현재가격', btc_current_value)
        # my_btc_value = total_profit_loss['btc_balance']*total_profit_loss['current_price']
        # print('나의 비트코인 가치', my_btc_value)
        # total_profit_loss_value = btc_current_value - my_btc_value
        print('이익', total_profit_loss_value)
        if average(minute_df[0:10]) > current_price and total_profit_loss_value > 50:
            #평균가격이 현재가보다 높다는 것은 가격이 내리고 있다는 증거 
            decisionSelf=True
        if decisionSelf:
            print("💼 손절 수동 매매 결정을 실행합니다...")
            decision = {'decision': 'sell'}
            execution_result = execute_trading_decision(upbit, decision, investment_status, market_data)
        else:
            print("💼 손절 수동 매매 실행 안합니다...")


        if execution_result and execution_result.get('success', False):
            print("✅ 매매 실행 완료")
            logger.info(f"매매 실행 성공: {execution_result}")
        else:
            print("❌ 매매 실행 실패 또는 건너뜀")
            logger.warning(f"매매 실행 실패: {execution_result}")
            
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
        print("📊 시장 데이터를 수집합니다...")
        daily_df, minute_df, current_price, orderbook, fear_greed_data = get_market_data()
        print('데이터 조회1111', daily_df, minute_df, current_price, orderbook, fear_greed_data)


        # 기술적 지표 계산
        if daily_df is not None:
            daily_df = calculate_technical_indicators(daily_df)
        if minute_df is not None:
            minute_df = calculate_technical_indicators(minute_df)
        
        # 뉴스 데이터 수집 및 분석
        print("📰 뉴스 데이터를 분석합니다...")
        analyzed_news = None
        news_data = get_bitcoin_news()
        if news_data:
            analyzed_news = analyze_news_sentiment(news_data)
            if analyzed_news:
                news_summary = get_news_summary(analyzed_news)
        
        # 투자 상태 조회
        print("💰 투자 상태를 확인합니다...")
        investment_status = get_investment_status(upbit)
        
        # AI 분석용 데이터 생성 (기술적 지표, 공포탐욕지수, 뉴스 포함)
        market_data = create_market_analysis_data(daily_df, minute_df, current_price, orderbook, fear_greed_data, analyzed_news)
        
        # AI 매매 결정 (기술적 지표, 공포탐욕지수, 뉴스 포함)
        print("🤖 AI 분석을 시작합니다...")
        decision = ai_trading_decision_with_indicators(market_data)
        
        # 매매 실행
        print("💼 매매 결정을 실행합니다...")
        execution_result = execute_trading_decision(upbit, decision, investment_status, market_data)
        
        # 수동동매매 실행
        decisionSelf=False

        if decisionSelf:
            
            print("💼 매매 결정을 실행합니다...")
            decision = {'decision': 'sell'}
            execution_result = execute_trading_decision(upbit, decision, investment_status, market_data)
        
        if execution_result and execution_result.get('success', False):
            print("✅ 매매 실행 완료")
            logger.info(f"매매 실행 성공: {execution_result}")
        else:
            print("❌ 매매 실행 실패 또는 건너뜀")
            logger.warning(f"매매 실행 실패: {execution_result}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        logger.error(f"메인 트레이딩 사이클 오류: {e}")

def test_vision_analysis():
    """비전 분석 테스트 함수"""
    print("=" * 60)
    print("🔍 비전 분석 테스트 모드")
    print("=" * 60)
    
    try:
        from test_vision_analysis import main as test_main
        test_main()
    except ImportError:
        print("❌ test_vision_analysis.py 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"❌ 비전 분석 테스트 중 오류: {e}")

def main():
    """메인 함수"""
    # 명령행 인수 파싱
    parser = argparse.ArgumentParser(description='비트코인 AI 자동매매 시스템')
    parser.add_argument('--mode', choices=['vision', 'indicators', 'test'], 
                       default='vision', help='실행 모드 선택 (기본값: vision)')
    parser.add_argument('--interval', type=int, default=ANALYSIS_INTERVAL,
                       help=f'분석 간격 (초) (기본값: {ANALYSIS_INTERVAL})')
    
    args = parser.parse_args()
    
    print("🚀 비트코인 AI 자동매매 시스템을 시작합니다...")
    print(f"📋 실행 모드: {args.mode}")
    print(f"⏰ 분석 간격: {args.interval}초 ({args.interval/60:.1f}분)")
    
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
    
    # 백그라운드 서비스 실행 (스케줄러, 대시보드)
    start_background_services(logger)

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
    
    if args.mode == 'test':
        # 비전 분석 테스트 모드
        test_vision_analysis()
        return
    
    print("🔄 자동매매를 시작합니다...")
    print("💡 Ctrl+C를 눌러서 프로그램을 종료할 수 있습니다.")
    print()
    
    while True:
        try:
            if args.mode == 'vision':
                # Vision API 포함 모드
                main_trading_cycle_with_vision(upbit, logger)
            else:
                # 기술적 지표만 사용 모드
                main_trading_cycle_with_indicators(upbit, logger)
            
            print("\n" + "=" * 60)
            print(f"⏰ {args.interval/60:.1f}분 후 다음 분석을 시작합니다...")
            print("=" * 60 + "\n")
            time.sleep(args.interval)
            
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
