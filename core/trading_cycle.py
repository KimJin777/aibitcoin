"""
트레이딩 사이클 관련 코어 기능을 담당하는 모듈
"""

import time
from typing import Dict, Any
import pyupbit
from data.market_data import get_market_data
from data.news_data import get_bitcoin_news, analyze_news_sentiment, get_news_summary
from data.screenshot import capture_upbit_screenshot, create_images_directory
from analysis.technical_indicators import calculate_technical_indicators
from analysis.ai_analysis import create_market_analysis_data, ai_trading_decision_with_indicators, ai_trading_decision_with_vision
from trading.account import get_investment_status, get_total_profit_loss
from trading.execution import execute_trading_decision
from database.trade_recorder import save_market_data_record

def execute_trading_cycle(upbit: pyupbit.Upbit, logger: Any, use_vision: bool = True) -> None:
    """메인 트레이딩 사이클 실행"""
    try:
        # 시장 데이터 수집 및 기술적 지표 계산
        daily_df, minute_df, current_price, orderbook, fear_greed_data = get_market_data()
        
        if daily_df is not None:
            daily_df = calculate_technical_indicators(daily_df)
        if minute_df is not None:
            minute_df = calculate_technical_indicators(minute_df)
        
        # 뉴스 데이터 분석
        analyzed_news = None
        news_data = get_bitcoin_news()
        if news_data:
            analyzed_news = analyze_news_sentiment(news_data)
            if analyzed_news:
                get_news_summary(analyzed_news)
        
        # 투자 상태 조회
        investment_status = get_investment_status(upbit)
        
        # 시장 분석 데이터 생성
        market_data = create_market_analysis_data(
            daily_df, minute_df, current_price, orderbook, 
            fear_greed_data, analyzed_news
        )

        # 데이터 저장
        try:
            save_market_data_record(market_data)
        except Exception as e:
            logger.error(f"시장 데이터 저장 실패: {e}")

        # 매매 결정 (Vision API 또는 기본 분석)
        if use_vision:
            decision = get_vision_based_decision(market_data, logger)
        else:
            decision = ai_trading_decision_with_indicators(market_data)

        # 매매 실행
        execution_result = execute_trading_decision(upbit, decision, investment_status, market_data)
        
        # 손절매 검사 및 실행
        check_and_execute_stop_loss(
            upbit, logger, minute_df, current_price, 
            investment_status, market_data, decision
        )

        # 결과 로깅
        if execution_result and execution_result.get('success', False):
            logger.info(f"매매 실행 성공: {execution_result}")
        else:
            logger.warning(f"매매 실행 실패: {execution_result}")
            
    except Exception as e:
        logger.error(f"트레이딩 사이클 오류: {e}")

def get_vision_based_decision(market_data: Dict, logger: Any) -> Dict:
    """Vision API를 사용한 매매 결정"""
    try:
        create_images_directory()
        screenshot_result = capture_upbit_screenshot()
        
        if screenshot_result:
            filepath, chart_image_base64 = screenshot_result
            return ai_trading_decision_with_vision(market_data, chart_image_base64)
    except Exception as e:
        logger.error(f"Vision API 분석 실패: {e}")
    
    return ai_trading_decision_with_indicators(market_data)

def check_and_execute_stop_loss(
    upbit: pyupbit.Upbit, 
    logger: Any,
    minute_df: Any,
    current_price: float,
    investment_status: Dict,
    market_data: Dict,
    current_decision: Dict
) -> None:
    """손절매 조건 검사 및 실행"""
    try:
        # DataFrame 유효성 검사
        if minute_df is None or (hasattr(minute_df, 'empty') and minute_df.empty) or len(minute_df) < 10:
            logger.info("분봉 데이터 부족: 손절매 검사 건너뜀")
            return

        total_profit_loss = get_total_profit_loss(upbit)
        if not total_profit_loss:
            logger.info("손익 데이터 없음: 손절매 검사 건너뜀")
            return

        # 손절매 조건 계산
        current_btc_value = total_profit_loss['current_price'] * total_profit_loss['btc_balance']
        my_btc_value = total_profit_loss['btc_avg_price'] * total_profit_loss['btc_balance']
        total_profit_loss_value = current_btc_value - my_btc_value
        sell_amount = total_profit_loss['btc_balance'] * 0.95
        recent_high_avg = minute_df['High'][0:10].mean()

        # 손절매 조건 검사
        if should_execute_stop_loss(
            recent_high_avg, current_price,
            total_profit_loss_value, sell_amount,
            current_decision
        ):
            logger.info(f"손절매 실행 - 평균가: {recent_high_avg:,.0f}, 현재가: {current_price:,.0f}")
            decision = {'decision': 'sell'}
            execute_trading_decision(upbit, decision, investment_status, market_data)

    except Exception as e:
        logger.error(f"손절매 검사 오류: {e}")

def should_execute_stop_loss(
    recent_high_avg: float,
    current_price: float,
    total_profit_loss_value: float,
    sell_amount: float,
    decision: Dict
) -> bool:
    """손절매 실행 여부 결정"""
    from database.stop_loss_query import get_yesterday_trade_info
    
    # 전날 0시 이후 또는 최근 구매 정보 조회
    trade_info = get_yesterday_trade_info()
    if not trade_info:
        return False
    
    # 현재 손익 계산
    buy_price = trade_info['buy_price']
    buy_amount = trade_info['buy_amount']
    current_value = current_price * buy_amount
    buy_value = buy_price * buy_amount
    profit = current_value - buy_value
    
    # 손절매 조건 검사
    price_dropping = recent_high_avg > current_price
    profit_sufficient = profit > 0  # 순수익이 0원 이상일 때
    is_hold_signal = isinstance(decision, dict) and decision.get('decision') == 'hold'
    
    if price_dropping and profit_sufficient and is_hold_signal:
        print(f"\n📊 손절매 상세 정보:")
        print(f"  - 구매 시점: {trade_info['buy_time']}")
        print(f"  - 구매 가격: {buy_price:,.0f}원")
        print(f"  - 현재 가격: {current_price:,.0f}원")
        print(f"  - 순수익: {profit:,.0f}원")
    
    return price_dropping and profit_sufficient and is_hold_signal
