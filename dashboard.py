"""
자동 매매 프로그램 실시간 모니터링 대시보드
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import mysql.connector
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List, Optional
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

def get_db_connection():
    """데이터베이스 연결"""
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return connection
    except Exception as e:
        st.error(f"데이터베이스 연결 오류: {e}")
        return None

def get_initial_investment_estimate():
    """데이터베이스에서 초기 투자금액을 추정하는 함수"""
    try:
        connection = get_db_connection()
        if not connection:
            return None
        
        cursor = connection.cursor(dictionary=True)
        
        # 방법 1: 가장 오래된 거래 기록에서 KRW잔고 확인
        query_oldest = """
        SELECT balance_krw, timestamp 
        FROM trades 
        ORDER BY timestamp ASC 
        LIMIT 1
        """
        cursor.execute(query_oldest)
        oldest_trade = cursor.fetchone()
        
        # 방법 2: 현재 보유 비트코인의 총 투자금액 계산 (평균매수가 * 보유량)
        query_btc_investment = """
        SELECT balance_btc, price, amount, total_value
        FROM trades 
        WHERE action = 'buy' AND balance_btc > 0
        ORDER BY timestamp DESC 
        LIMIT 1
        """
        cursor.execute(query_btc_investment)
        btc_trade = cursor.fetchone()
        
        # 방법 3: 모든 매수 거래의 총합으로 추정
        query_total_buy = """
        SELECT SUM(total_value) as total_buy_amount
        FROM trades 
        WHERE action = 'buy'
        """
        cursor.execute(query_total_buy)
        total_buy_result = cursor.fetchone()
        
        cursor.close()
        
        estimated_investment = None
        
        if oldest_trade and oldest_trade['balance_krw']:
            # 가장 오래된 거래 시점의 KRW잔고가 초기 투자금액일 가능성이 높음
            estimated_investment = oldest_trade['balance_krw']
            print(f"📊 가장 오래된 거래에서 추정된 총투자원금: {estimated_investment:,.0f}원")
        
        if btc_trade and btc_trade['balance_btc'] and btc_trade['price']:
            # 비트코인 보유량이 있다면 평균 매수가로 계산
            btc_investment = btc_trade['balance_btc'] * btc_trade['price']
            if estimated_investment is None or btc_investment > estimated_investment:
                estimated_investment = btc_investment
            print(f"📊 비트코인 보유량 기반 추정 투자금액: {btc_investment:,.0f}원")
        
        if total_buy_result and total_buy_result['total_buy_amount']:
            # 모든 매수 거래의 총합
            total_buy_amount = total_buy_result['total_buy_amount']
            if estimated_investment is None or total_buy_amount > estimated_investment:
                estimated_investment = total_buy_amount
            print(f"📊 총 매수 거래액 기반 추정 투자금액: {total_buy_amount:,.0f}원")
        
        return estimated_investment
        
    except Exception as e:
        print(f"❌ 초기 투자금액 추정 실패: {e}")
        return None

def get_upbit_deposit_history():
    """업비트 API를 통해 입금 내역을 조회하여 초기 투자금액을 추정하는 함수"""
    try:
        import pyupbit
        from config.settings import UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY
        
        if not UPBIT_ACCESS_KEY or not UPBIT_SECRET_KEY:
            print("⚠️ 업비트 API 키가 설정되지 않았습니다.")
            return None
        
        upbit = pyupbit.Upbit(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)
        
        # 방법 1: 업비트 API에서 실제 입금 내역 조회 (가장 정확)
        try:
            print("🔍 업비트 API에서 KRW 입금 내역 조회 시도...")
            # KRW 입금 내역 조회
            krw_deposits = upbit.get_deposit_list("KRW")
            print(f"📊 get_deposit_list 결과: {krw_deposits}")
            
            if krw_deposits:
                print(f"📊 KRW 입금 내역 조회 성공: {len(krw_deposits)}건")
                
                # 입금 내역 정리
                deposit_records = []
                total_deposits = 0
                
                for deposit in krw_deposits:
                    if isinstance(deposit, dict):
                        amount = float(deposit.get('amount', 0))
                        created_at = deposit.get('created_at', '')
                        state = deposit.get('state', '')
                        
                        print(f"📊 입금 내역 항목: amount={amount}, state={state}, created_at={created_at}")
                        
                        # 완료된 입금만 계산 (ACCEPTED도 완료로 인식)
                        if (state == 'done' or state == 'ACCEPTED') and amount > 0:
                            deposit_records.append({
                                'amount': amount,
                                'created_at': created_at,
                                'state': state
                            })
                            total_deposits += amount
                
                if deposit_records:
                    print(f"📊 총 입금 횟수: {len(deposit_records)}회")
                    print(f"📊 총 입금액: {total_deposits:,.0f}원")
                    
                    # 입금 내역 정렬 (최신순)
                    deposit_records.sort(key=lambda x: x['created_at'], reverse=True)
                    
                    # 상세 입금 내역 출력
                    for i, deposit in enumerate(deposit_records[:5]):  # 최근 5건만 출력
                        print(f"  {i+1}. {deposit['amount']:,.0f}원 ({deposit['created_at']})")
                    
                    return {
                        'total_deposits': total_deposits,
                        'deposit_count': len(deposit_records),
                        'deposits': deposit_records,
                        'method': '실제 입금 내역 조회',
                        'total_assets': None,
                        'total_buy_amount': None,
                        'krw_balance': None,
                        'btc_balance': None,
                        'current_btc_price': None
                    }
                else:
                    print("📊 완료된 KRW 입금 내역이 없습니다.")
                    print("📊 모든 입금 내역 상태:", [f"amount={d.get('amount', 0)}, state={d.get('state', 'N/A')}" for d in krw_deposits[:5]])
            else:
                print("📊 KRW 입금 내역을 가져올 수 없습니다.")
                
        except Exception as deposit_error:
            print(f"📊 입금 내역 조회 실패: {deposit_error}")
            print(f"📊 오류 타입: {type(deposit_error).__name__}")
            import traceback
            print(f"📊 상세 오류: {traceback.format_exc()}")
        
        # 방법 2: 기존 추정 방식 (입금 내역 조회 실패 시 백업)
        try:
            print("🔄 백업 추정 방식 사용 (실제 입금 내역 조회 실패)")
            # 계좌 잔고 조회
            balances = upbit.get_balances()
            if not balances:
                print("📊 계좌 잔고 정보를 가져올 수 없습니다.")
                return None
            
            # KRW잔고 확인
            krw_balance = 0
            btc_balance = 0
            btc_avg_price = 0
            
            for balance in balances:
                if isinstance(balance, dict):
                    currency = balance.get('currency', '')
                    if currency == 'KRW':
                        krw_balance = float(balance.get('balance', 0))
                    elif currency == 'BTC':
                        btc_balance = float(balance.get('balance', 0))
                        btc_avg_price = float(balance.get('avg_buy_price', 0))
            
            print(f"📊 KRW 잔고: {krw_balance:,.0f}원")
            print(f"📊 BTC 잔고: {btc_balance:.8f} BTC")
            print(f"📊 BTC 평균 매수가: {btc_avg_price:,.0f}원")
            
            # 현재 비트코인 가격 조회
            current_price = pyupbit.get_current_price("KRW-BTC")
            if not current_price:
                print("📊 현재 비트코인 가격을 가져올 수 없습니다.")
                return None
            
            print(f"📊 현재 BTC 가격: {current_price:,.0f}원")
            
            # 총보유자산 계산
            total_assets = krw_balance + (btc_balance * current_price)
            print(f"📊 계산된 총보유자산: {total_assets:,.0f}원")
            
            # 방법 3: 거래 내역을 통해 입금 추정
            try:
                print("📊 거래 내역을 통한 입금 추정 시도...")
                # 주문 내역 조회
                orders = upbit.get_order_history()
                if orders:
                    print(f"📊 주문 내역 조회 성공: {len(orders)}건")
                    # 매수 거래만 필터링하여 총 투자금액 추정
                    buy_orders = []
                    total_buy_amount = 0
                    
                    for order in orders:
                        if isinstance(order, dict):
                            side = order.get('side', '')
                            price = order.get('price', 0)
                            executed_volume = order.get('executed_volume', 0)
                            state = order.get('state', '')
                            
                            # 완료된 매수 주문만 계산
                            if side == 'bid' and state == 'done' and price > 0 and executed_volume > 0:
                                try:
                                    order_amount = float(price) * float(executed_volume)
                                    buy_orders.append({
                                        'price': float(price),
                                        'volume': float(executed_volume),
                                        'amount': order_amount,
                                        'created_at': order.get('created_at', '')
                                    })
                                    total_buy_amount += order_amount
                                except (ValueError, TypeError):
                                    continue
                    
                    if buy_orders:
                        print(f"📊 총 매수 거래 횟수: {len(buy_orders)}회")
                        print(f"📊 총 매수 금액: {total_buy_amount:,.0f}원")
                        
                        # 매수 거래 내역 정렬 (최신순)
                        buy_orders.sort(key=lambda x: x['created_at'], reverse=True)
                        
                        # 상세 매수 내역 출력
                        for i, order in enumerate(buy_orders[:5]):  # 최근 5건만 출력
                            print(f"  {i+1}. {order['amount']:,.0f}원 (BTC: {order['volume']:.8f} @ {order['price']:,.0f}원)")
                        
                        # 입금 내역으로 추정 (현재 총 자산 + 총 매수 금액)
                        estimated_deposits = total_assets + total_buy_amount
                        print(f"📊 최종 추정 입금액: {total_assets:,.0f}원 + {total_buy_amount:,.0f}원 = {estimated_deposits:,.0f}원")
                        
                        return {
                            'total_deposits': estimated_deposits,
                            'deposit_count': len(buy_orders),
                            'deposits': buy_orders,
                            'method': '거래 내역 기반 추정',
                            'total_assets': total_assets,
                            'total_buy_amount': total_buy_amount,
                            'krw_balance': krw_balance,
                            'btc_balance': btc_balance,
                            'current_btc_price': current_price
                        }
                    else:
                        print("📊 매수 거래 내역이 없습니다.")
                else:
                    print("📊 주문 내역이 없습니다.")
                
            except Exception as order_error:
                print(f"📊 거래 내역 조회 실패: {order_error}")
            
            # 방법 4: 간단한 추정 (현재 총보유자산을 입금액으로 가정)
            print(f"📊 방법 4: 현재 자산 기반 추정 사용")
            print(f"📊 현재 총보유자산: {total_assets:,.0f}원")
            print(f"📊 KRW잔고: {krw_balance:,.0f}원")
            print(f"📊 BTC 잔고: {btc_balance:.8f} BTC")
            print(f"📊 BTC 평균 매수가: {btc_avg_price:,.0f}원")
            print(f"📊 현재 BTC 가격: {current_price:,.0f}원")
            
            return {
                'total_deposits': total_assets,
                'deposit_count': 1,
                'deposits': [{'amount': total_assets, 'created_at': '현재', 'state': '추정'}],
                'method': '현재 자산 기반 추정',
                'total_assets': total_assets,
                'krw_balance': krw_balance,
                'btc_balance': btc_balance,
                'current_btc_price': current_price
            }
            
        except Exception as balance_error:
            print(f"📊 계좌 정보 조회 실패: {balance_error}")
            return None
        
    except Exception as e:
        print(f"❌ 업비트 입금 내역 조회 실패: {e}")
        return None

def get_upbit_account_info():
    """업비트 API를 통해 현재 계좌 정보를 조회하는 함수"""
    try:
        import pyupbit
        from config.settings import UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY
        
        if not UPBIT_ACCESS_KEY or not UPBIT_SECRET_KEY:
            print("⚠️ 업비트 API 키가 설정되지 않았습니다.")
            return None
        
        upbit = pyupbit.Upbit(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)
        
        # 현재 잔고 조회
        balances = upbit.get_balances()
        if not balances:
            return None
        
        account_info = {
            'krw_balance': 0,
            'btc_balance': 0,
            'btc_avg_price': 0
        }
        
        for balance in balances:
            if isinstance(balance, dict):
                currency = balance.get('currency', '')
                if currency == 'KRW':
                    account_info['krw_balance'] = float(balance.get('balance', 0))
                elif currency == 'BTC':
                    account_info['btc_balance'] = float(balance.get('balance', 0))
                    account_info['btc_avg_price'] = float(balance.get('avg_buy_price', 0))
        
        # 현재 비트코인 가격 조회
        current_price = pyupbit.get_current_price("KRW-BTC")
        if current_price and account_info['btc_balance'] > 0:
            # 비트코인 보유량이 있다면 평균 매수가로 총 투자금액 계산
            total_btc_investment = account_info['btc_balance'] * account_info['btc_avg_price']
            account_info['total_btc_investment'] = total_btc_investment
            print(f"📊 업비트 API 기반 추정 총투자원금: {total_btc_investment:,.0f}원")
        
        return account_info
        
    except Exception as e:
        print(f"❌ 업비트 API 조회 실패: {e}")
        return None

class TradingDashboard:
    """거래 대시보드 클래스"""
    
    def __init__(self):
        self.db_config = {
            'host': DB_HOST,
            'port': DB_PORT,
            'database': DB_NAME,
            'user': DB_USER,
            'password': DB_PASSWORD
        }
    
    def get_connection(self):
        """데이터베이스 연결"""
        try:
            connection = mysql.connector.connect(**self.db_config)
            return connection
        except Exception as e:
            st.error(f"데이터베이스 연결 오류: {e}")
            return None
    
    def get_recent_trades(self, limit: int = 50) -> pd.DataFrame:
        """최근 거래 기록 조회"""
        connection = self.get_connection()
        if not connection:
            return pd.DataFrame()
        
        try:
            query = """
            SELECT 
                id, timestamp, decision, action, price, amount, 
                total_value, fee, balance_krw, balance_btc,
                confidence, reasoning, status, created_at
            FROM trades 
            ORDER BY created_at DESC 
            LIMIT %s
            """
            
            df = pd.read_sql(query, connection, params=(limit,))
            connection.close()
            return df
        except Exception as e:
            st.error(f"거래 데이터 조회 오류: {e}")
            return pd.DataFrame()
    
    def get_trading_reflections(self, limit: int = 20) -> pd.DataFrame:
        """거래 반성 데이터 조회"""
        connection = self.get_connection()
        if not connection:
            return pd.DataFrame()
        
        try:
            query = """
            SELECT 
                tr.id, tr.trade_id, tr.reflection_type, tr.performance_score,
                tr.profit_loss, tr.profit_loss_percentage, tr.decision_quality_score,
                tr.timing_score, tr.risk_management_score, tr.ai_analysis,
                tr.improvement_suggestions, tr.lessons_learned, tr.created_at,
                t.decision, t.action, t.price
            FROM trading_reflections tr
            JOIN trades t ON tr.trade_id = t.id
            ORDER BY tr.created_at DESC 
            LIMIT %s
            """
            
            df = pd.read_sql(query, connection, params=(limit,))
            connection.close()
            return df
        except Exception as e:
            st.error(f"반성 데이터 조회 오류: {e}")
            return pd.DataFrame()

    def get_reflection_detail(self, reflection_id: int) -> pd.DataFrame:
        """특정 반성 상세 정보 조회"""
        connection = self.get_connection()
        if not connection:
            return pd.DataFrame()
        
        try:
            query = """
            SELECT 
                tr.id, tr.trade_id, tr.reflection_type, tr.performance_score,
                tr.profit_loss, tr.profit_loss_percentage, tr.decision_quality_score,
                tr.timing_score, tr.risk_management_score, tr.ai_analysis,
                tr.improvement_suggestions, tr.lessons_learned, tr.created_at,
                t.decision, t.action, t.price
            FROM trading_reflections tr
            JOIN trades t ON tr.trade_id = t.id
            WHERE tr.id = %s
            LIMIT 1
            """
            
            df = pd.read_sql(query, connection, params=(reflection_id,))
            connection.close()
            return df
        except Exception as e:
            st.error(f"반성 상세 정보 조회 오류: {e}")
            return pd.DataFrame()
    
    def get_performance_metrics(self, days: int = 7) -> pd.DataFrame:
        """성과 지표 조회"""
        connection = self.get_connection()
        if not connection:
            return pd.DataFrame()
        
        try:
            query = """
            SELECT 
                period_type, period_start, period_end, total_trades,
                winning_trades, losing_trades, win_rate, total_profit_loss,
                total_profit_loss_percentage, max_drawdown, sharpe_ratio,
                average_trade_duration, best_trade_profit, worst_trade_loss,
                created_at
            FROM performance_metrics 
            WHERE period_start >= DATE_SUB(NOW(), INTERVAL %s DAY)
            ORDER BY period_start DESC
            """
            
            df = pd.read_sql(query, connection, params=(days,))
            connection.close()
            return df
        except Exception as e:
            st.error(f"성과 지표 조회 오류: {e}")
            return pd.DataFrame()
    
    def get_learning_insights(self, limit: int = 10) -> pd.DataFrame:
        """학습 인사이트 조회"""
        connection = self.get_connection()
        if not connection:
            return pd.DataFrame()
        
        try:
            query = """
            SELECT 
                id, insight_type, insight_title, insight_description,
                confidence_level, priority_level, status, created_at
            FROM learning_insights 
            ORDER BY created_at DESC 
            LIMIT %s
            """
            
            df = pd.read_sql(query, connection, params=(limit,))
            connection.close()
            return df
        except Exception as e:
            st.error(f"학습 인사이트 조회 오류: {e}")
            return pd.DataFrame()
    
    def get_insight_detail(self, insight_id: int) -> pd.DataFrame:
        """특정 인사이트 상세 정보 조회"""
        connection = self.get_connection()
        if not connection:
            return pd.DataFrame()
        
        try:
            query = """
            SELECT 
                id, insight_type, insight_title, insight_description,
                confidence_level, priority_level, status, created_at
            FROM learning_insights 
            WHERE id = %s
            """
            
            df = pd.read_sql(query, connection, params=(insight_id,))
            connection.close()
            return df
        except Exception as e:
            st.error(f"인사이트 상세 정보 조회 오류: {e}")
            return pd.DataFrame()
    
    def get_strategy_improvements(self, limit: int = 10) -> pd.DataFrame:
        """전략 개선 제안 조회"""
        connection = self.get_connection()
        if not connection:
            return pd.DataFrame()
        
        try:
            query = """
            SELECT 
                id, improvement_type, old_value, new_value, reason,
                expected_impact, success_metric, status, created_at
            FROM strategy_improvements 
            ORDER BY created_at DESC 
            LIMIT %s
            """
            
            df = pd.read_sql(query, connection, params=(limit,))
            connection.close()
            return df
        except Exception as e:
            st.error(f"전략 개선 제안 조회 오류: {e}")
            return pd.DataFrame()
    
    def update_strategy_improvement_status(self, improvement_id: int, new_status: str) -> bool:
        """전략 개선 상태 업데이트"""
        connection = self.get_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            query = """
            UPDATE strategy_improvements 
            SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """
            
            cursor.execute(query, (new_status, improvement_id))
            connection.commit()
            cursor.close()
            connection.close()
            
            return True
        except Exception as e:
            st.error(f"전략 개선 상태 업데이트 오류: {e}")
            return False
    
    def get_market_data(self, limit: int = 100) -> pd.DataFrame:
        """시장 데이터 조회"""
        connection = self.get_connection()
        if not connection:
            return pd.DataFrame()
        
        try:
            query = """
            SELECT 
                id, timestamp, current_price, volume_24h, change_24h,
                rsi, macd, macd_signal, bollinger_upper, bollinger_lower,
                fear_greed_index, fear_greed_value, news_sentiment, created_at
            FROM market_data 
            ORDER BY created_at DESC 
            LIMIT %s
            """
            
            df = pd.read_sql(query, connection, params=(limit,))
            connection.close()
            return df
        except Exception as e:
            st.error(f"시장 데이터 조회 오류: {e}")
            return pd.DataFrame()

def create_price_chart(df: pd.DataFrame) -> go.Figure:
    """가격 차트 생성"""
    if df.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    # 가격 라인
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['current_price'],
        mode='lines',
        name='현재가',
        line=dict(color='#1f77b4', width=2)
    ))
    
    # 볼린저 밴드
    if 'bollinger_upper' in df.columns and 'bollinger_lower' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['bollinger_upper'],
            mode='lines',
            name='볼린저 상단',
            line=dict(color='rgba(255,0,0,0.3)', width=1)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['bollinger_lower'],
            mode='lines',
            name='볼린저 하단',
            line=dict(color='rgba(255,0,0,0.3)', width=1),
            fill='tonexty'
        ))
    
    fig.update_layout(
        title='비트코인 가격 추이',
        xaxis_title='시간',
        yaxis_title='가격 (KRW)',
        height=400
    )
    
    return fig

def create_trading_volume_chart(df: pd.DataFrame) -> go.Figure:
    """거래량 차트 생성"""
    if df.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    # 매수/매도 거래량
    buy_trades = df[df['action'] == 'buy']
    sell_trades = df[df['action'] == 'sell']
    
    if not buy_trades.empty:
        fig.add_trace(go.Bar(
            x=buy_trades['timestamp'],
            y=buy_trades['total_value'],
            name='매수',
            marker_color='green'
        ))
    
    if not sell_trades.empty:
        fig.add_trace(go.Bar(
            x=sell_trades['timestamp'],
            y=sell_trades['total_value'],
            name='매도',
            marker_color='red'
        ))
    
    fig.update_layout(
        title='거래량 분석',
        xaxis_title='시간',
        yaxis_title='거래 금액 (KRW)',
        height=300
    )
    
    return fig

def create_performance_chart(df: pd.DataFrame) -> go.Figure:
    """성과 차트 생성"""
    if df.empty:
        return go.Figure()
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('승률', '수익률', '최대 낙폭', '샤프 비율'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # 승률
    fig.add_trace(
        go.Scatter(x=df['period_start'], y=df['win_rate'], name='승률'),
        row=1, col=1
    )
    
    # 수익률
    fig.add_trace(
        go.Scatter(x=df['period_start'], y=df['total_profit_loss_percentage'], name='수익률'),
        row=1, col=2
    )
    
    # 최대 낙폭
    fig.add_trace(
        go.Scatter(x=df['period_start'], y=df['max_drawdown'], name='최대 낙폭'),
        row=2, col=1
    )
    
    # 샤프 비율
    fig.add_trace(
        go.Scatter(x=df['period_start'], y=df['sharpe_ratio'], name='샤프 비율'),
        row=2, col=2
    )
    
    fig.update_layout(height=500, showlegend=False)
    return fig

def show_insight_detail(dashboard: TradingDashboard, insight_id: int):
    """인사이트 상세 정보 표시"""
    insight_detail = dashboard.get_insight_detail(insight_id)
    
    if insight_detail.empty:
        st.error("인사이트를 찾을 수 없습니다.")
        return
    
    insight = insight_detail.iloc[0]
    
    st.subheader(f"💡 {insight['insight_title']}")
    st.markdown("---")
    
    # 기본 정보
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("인사이트 타입", insight['insight_type'])
        st.metric("신뢰도", f"{insight['confidence_level']:.1f}%")
    
    with col2:
        st.metric("우선순위", insight['priority_level'])
        st.metric("상태", insight['status'])
    
    with col3:
        st.metric("발견일", insight['created_at'].strftime('%Y-%m-%d'))
    
    st.markdown("---")
    
    # 상세 설명
    st.subheader("📝 상세 설명")
    st.write(insight['insight_description'])
    
    # 추가 정보 섹션
    st.subheader("📊 추가 정보")
    
    # 우선순위별 색상 표시
    priority_colors = {
        'high': '🔴',
        'medium': '🟡', 
        'low': '🟢'
    }
    priority_icon = priority_colors.get(insight['priority_level'], '⚪')
    
    # 상태별 아이콘
    status_icons = {
        'pending': '⏳',
        'implemented': '✅',
        'rejected': '❌',
        'in_progress': '🔄'
    }
    status_icon = status_icons.get(insight['status'], '❓')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("우선순위", f"{priority_icon} {insight['priority_level']}")
        st.metric("상태", f"{status_icon} {insight['status']}")
    
    with col2:
        st.metric("인사이트 타입", insight['insight_type'])
        st.metric("신뢰도", f"{insight['confidence_level']:.1f}%")
    
    # 뒤로가기 버튼
    if st.button("← 뒤로가기"):
        st.rerun()

def show_reflection_detail(dashboard: TradingDashboard, reflection_id: int):
    """반성 상세 정보 표시"""
    detail = dashboard.get_reflection_detail(reflection_id)
    if detail.empty:
        st.error("반성을 찾을 수 없습니다.")
        return
    r = detail.iloc[0]

    st.subheader(f"🤔 반성 #{r['id']} (거래ID: {r['trade_id']})")
    st.markdown("---")

    # 상단 핵심 지표
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("성과점수", f"{r.get('performance_score', 0):.2f}")
        st.metric("손익", f"{r.get('profit_loss', 0):,.0f}")
    with c2:
        st.metric("의사결정 품질", f"{r.get('decision_quality_score', 0):.2f}")
        st.metric("타이밍", f"{r.get('timing_score', 0):.2f}")
    with c3:
        st.metric("리스크관리", f"{r.get('risk_management_score', 0):.2f}")
        st.metric("손익률", f"{r.get('profit_loss_percentage', 0):.2f}%")
    with c4:
        st.metric("행동", f"{r.get('action', '')}")
        st.metric("가격", f"{r.get('price', 0):,.0f}")

    st.markdown("---")

    # 텍스트 섹션
    st.subheader("🧠 AI 분석")
    st.write(r.get('ai_analysis', ''))

    st.subheader("🔧 개선 제안")
    st.write(r.get('improvement_suggestions', ''))

    st.subheader("📚 배운 점")
    st.write(r.get('lessons_learned', ''))

    # 뒤로가기
    if st.button("← 뒤로가기"):
        st.rerun()

def main():
    """메인 대시보드"""
    st.set_page_config(
        page_title="GPT Bitcoin 자동매매 대시보드",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 세션 상태 초기화
    if 'show_insight_detail' not in st.session_state:
        st.session_state.show_insight_detail = False
    if 'selected_insight_id' not in st.session_state:
        st.session_state.selected_insight_id = None
    if 'show_reflection_detail' not in st.session_state:
        st.session_state.show_reflection_detail = False
    if 'selected_reflection_id' not in st.session_state:
        st.session_state.selected_reflection_id = None
    
    # 대시보드 객체 생성
    dashboard = TradingDashboard()
    
    # 인사이트 상세 보기 모드
    if st.session_state.show_insight_detail:
        st.title("💡 학습 인사이트 상세보기")
        st.markdown("---")
        
        # 인사이트 목록 표시
        insights = dashboard.get_learning_insights(20)
        if not insights.empty:
            st.subheader("📋 인사이트 목록")
            
            for _, insight in insights.iterrows():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**{insight['insight_title']}**")
                    st.write(f"타입: {insight['insight_type']} | 우선순위: {insight['priority_level']}")
                
                with col2:
                    st.write(f"신뢰도: {insight['confidence_level']:.1f}%")
                
                with col3:
                    if st.button(f"상세보기", key=f"detail_{insight['id']}"):
                        st.session_state.selected_insight_id = insight['id']
                        st.rerun()
                
                st.markdown("---")
            
            # 선택된 인사이트 상세 보기
            if st.session_state.selected_insight_id:
                show_insight_detail(dashboard, st.session_state.selected_insight_id)
        
        # 뒤로가기 버튼
        if st.button("← 대시보드로 돌아가기"):
            st.session_state.show_insight_detail = False
            st.session_state.selected_insight_id = None
            st.rerun()
        
        return

    # 반성 상세 보기 모드
    if st.session_state.show_reflection_detail:
        st.title("🤔 반성 상세보기")
        st.markdown("---")

        reflections = dashboard.get_trading_reflections(50)
        if not reflections.empty:
            st.subheader("📋 반성 목록")
            for _, row in reflections.iterrows():
                c1, c2, c3, c4 = st.columns([3,1,1,1])
                with c1:
                    st.write(f"거래ID: {row['trade_id']} | 유형: {row['reflection_type']}")
                    st.write(f"성과점수: {row.get('performance_score', 0):.2f} | 손익: {row.get('profit_loss', 0):,.0f}")
                with c2:
                    st.write(f"의사결정: {row.get('decision', '')}")
                with c3:
                    st.write(f"행동: {row.get('action', '')}")
                with c4:
                    if st.button("상세보기", key=f"refl_{row['id']}"):
                        st.session_state.selected_reflection_id = row['id']
                        st.rerun()
                st.markdown("---")

            if st.session_state.selected_reflection_id:
                show_reflection_detail(dashboard, st.session_state.selected_reflection_id)

        if st.button("← 대시보드로 돌아가기"):
            st.session_state.show_reflection_detail = False
            st.session_state.selected_reflection_id = None
            st.rerun()

        return
    
    # 제목
    st.title("🤖 GPT Bitcoin 자동매매 실시간 모니터링")
    st.markdown("---")
    
    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # 초기 투자금액 자동 추정
        st.subheader("💰 총투자원금 자동 추정")
        
        # 방법 1: 업비트 입금 내역 조회 (가장 정확)
        deposit_info = get_upbit_deposit_history()
        
        # 방법 2: 데이터베이스 기반 추정
        estimated_investment = get_initial_investment_estimate()
        
        # 방법 3: 업비트 API 기반 추정
        upbit_info = get_upbit_account_info()
        
        # 가장 정확한 추정값 선택 (입금 내역 > 데이터베이스 > 업비트 API 순)
        final_estimate = None
        if deposit_info and deposit_info['total_deposits'] > 0:
            final_estimate = deposit_info['total_deposits']
            st.success(f"🎯 {deposit_info.get('method', '업비트 입금 내역')} 기반: {final_estimate:,.0f}원")
            st.info(f"📊 총 {deposit_info['deposit_count']}회 입금")
            
            # 상세 정보 표시
            if 'total_assets' in deposit_info and deposit_info['total_assets'] is not None:
                st.write(f"💰 현재 총보유자산: {deposit_info['total_assets']:,.0f}원")
            if 'total_buy_amount' in deposit_info and deposit_info['total_buy_amount'] is not None:
                st.write(f"💸 총 매수 금액: {deposit_info['total_buy_amount']:,.0f}원")
            if 'krw_balance' in deposit_info and deposit_info['krw_balance'] is not None:
                st.write(f"💵 KRW잔고: {deposit_info['krw_balance']:,.0f}원")
            if 'btc_balance' in deposit_info and deposit_info['btc_balance'] is not None:
                st.write(f"₿ BTC 잔고: {deposit_info['btc_balance']:.8f} BTC")
            if 'current_btc_price' in deposit_info and deposit_info['current_btc_price'] is not None:
                st.write(f"📈 현재 BTC 가격: {deposit_info['current_btc_price']:,.0f}원")
                
        elif estimated_investment:
            final_estimate = estimated_investment
            st.info(f"📊 데이터베이스 기반 추정: {estimated_investment:,.0f}원")
        elif upbit_info and 'total_btc_investment' in upbit_info:
            final_estimate = upbit_info['total_btc_investment']
            st.info(f"📊 업비트 API 기반 추정: {upbit_info['total_btc_investment']:,.0f}원")
        else:
            final_estimate = 1000000
            st.warning("⚠️ 자동 추정 실패, 기본값 사용")
        
        # 입금 내역 상세 정보 표시
        if deposit_info and deposit_info['deposits']:
            with st.expander("📋 상세 입금 내역"):
                if deposit_info.get('method') == '실제 입금 내역 조회':
                    st.success("✅ 업비트 API에서 실제 입금 내역을 조회했습니다")
                    for i, deposit in enumerate(deposit_info['deposits'][:10]):  # 최근 10건
                        st.write(f"{i+1}. {deposit['amount']:,.0f}원 ({deposit['created_at']})")
                elif deposit_info.get('method') == '거래 내역 기반 추정':
                    st.info("📊 거래 내역을 기반으로 입금액을 추정했습니다")
                    for i, deposit in enumerate(deposit_info['deposits'][:10]):  # 최근 10건
                        if 'volume' in deposit:  # 매수 거래인 경우
                            st.write(f"{i+1}. {deposit['amount']:,.0f}원 (BTC: {deposit['volume']:.8f} @ {deposit['price']:,.0f}원)")
                        else:  # 일반 입금인 경우
                            st.write(f"{i+1}. {deposit['amount']:,.0f}원 ({deposit['created_at']})")
                else:
                    for i, deposit in enumerate(deposit_info['deposits'][:10]):  # 최근 10건
                        st.write(f"{i+1}. {deposit['amount']:,.0f}원 ({deposit['created_at']})")
        
        # 수동 새로고침 버튼
        if st.button("🔄 총투자원금 새로고침", type="secondary"):
            st.rerun()
        
        # 디버깅 정보 표시
        if st.checkbox("🔍 디버깅 정보 표시"):
            st.write("**현재 추정 방법:**")
            if deposit_info:
                st.write(f"- 방법: {deposit_info.get('method', '알 수 없음')}")
                st.write(f"- 총 입금액: {deposit_info['total_deposits']:,.0f}원")
                st.write(f"- 입금 횟수: {deposit_info['deposit_count']}회")
                
                if deposit_info.get('method') == '실제 입금 내역 조회':
                    st.success("✅ 실제 입금 내역 기반으로 정확한 총투자원금을 계산했습니다")
                elif deposit_info.get('method') == '거래 내역 기반 추정':
                    if 'total_assets' in deposit_info and deposit_info['total_assets'] is not None:
                        st.write(f"- 현재 총보유자산: {deposit_info['total_assets']:,.0f}원")
                    if 'total_buy_amount' in deposit_info and deposit_info['total_buy_amount'] is not None:
                        st.write(f"- 총 매수 금액: {deposit_info['total_buy_amount']:,.0f}원")
                    st.info("📊 거래 내역을 기반으로 추정한 값입니다")
                elif deposit_info.get('method') == '현재 자산 기반 추정':
                    if 'total_assets' in deposit_info and deposit_info['total_assets'] is not None:
                        st.write(f"- 현재 총보유자산: {deposit_info['total_assets']:,.0f}원")
                    st.warning("⚠️ 현재 자산을 기반으로 추정한 값입니다")
            else:
                st.write("- 입금 내역 정보 없음")
        
        # 초기 투자금액 입력
        initial_investment = st.number_input(
            "총투자원금 (원)", 
            min_value=100000, 
            max_value=100000000, 
            value=int(final_estimate), 
            step=100000,
            help="업비트에 현금으로 입금한 총 금액을 입력하세요"
        )
        
        # 수동으로 정확한 입금액 입력 옵션
        if st.checkbox("✏️ 수동으로 정확한 입금액 입력"):
            manual_investment = st.number_input(
                "정확한 총투자원금 (원)",
                min_value=100000,
                max_value=100000000,
                value=100229,  # 사용자가 언급한 정확한 값
                step=1000,
                help="정확한 입금액을 알고 있다면 여기에 입력하세요"
            )
            initial_investment = manual_investment
            st.success(f"✅ 수동 입력된 총투자원금: {manual_investment:,.0f}원")
        
        # 업비트 계좌 정보 표시
        if upbit_info:
            st.subheader("📊 업비트 계좌 현황")
            st.metric("KRW잔고", f"{upbit_info['krw_balance']:,.0f}원")
            st.metric("비트코인 보유량", f"{upbit_info['btc_balance']:.8f} BTC")
            if upbit_info['btc_avg_price'] > 0:
                st.metric("평균 매수가", f"{upbit_info['btc_avg_price']:,.0f}원")
            
            # 현재 비트코인 가격
            try:
                import pyupbit
                current_price = pyupbit.get_current_price("KRW-BTC")
                if current_price:
                    st.metric("현재 BTC 가격", f"{current_price:,.0f}원")
                    
                    # 비트코인 평가금액
                    if upbit_info['btc_balance'] > 0:
                        btc_value = upbit_info['btc_balance'] * current_price
                        st.metric("BTC가치", f"{btc_value:,.0f}원")
            except:
                pass
    
    refresh_interval = st.sidebar.slider("새로고침 간격 (초)", 5, 60, 30)
    
    # 자동 새로고침
    if st.sidebar.button("🔄 새로고침"):
        st.rerun()
    
    # 재정 상태 요약 섹션
    st.subheader("💰 재정 상태 요약")
    finance_col1, finance_col2, finance_col3, finance_col4 = st.columns(4)
    
    # 최근 거래 데이터로 재정 상태 계산
    recent_trades = dashboard.get_recent_trades(100)
    if not recent_trades.empty:
        # 현재 잔고 정보 (가장 최근 거래 기준)
        latest_trade = recent_trades.iloc[0]
        current_krw = latest_trade.get('balance_krw', 0)  # KRW잔고: 원화보유잔고
        current_btc = latest_trade.get('balance_btc', 0)
        current_btc_price = latest_trade.get('price', 0)
        btc_value = current_btc * current_btc_price  # BTC가치: 비트코인투자자산가치
        
        # 총보유자산 = KRW잔고 + BTC가치
        total_assets = current_krw + btc_value
        
        # 수익/손실 = 총투자원금 - 총보유자산
        profit_loss = total_assets-initial_investment 
        
        # 수익률 = (수익손실) / 총투자원금
        profit_rate = (profit_loss / initial_investment) * 100 if initial_investment > 0 else 0
        
        with finance_col1:
            st.metric("💰 총보유자산", f"{total_assets:,.0f}원")
            st.metric("💵 KRW잔고", f"{current_krw:,.0f}원")
        
        with finance_col2:
            st.metric("₿ BTC 보유량", f"{current_btc:.8f}")
            st.metric("📊 BTC가치", f"{btc_value:,.0f}원")
        
        with finance_col3:
            st.metric("📈 수익/손실", f"{profit_loss:+,.0f}원")
            st.metric("📊 수익률", f"{profit_rate:+.2f}%")
        
        with finance_col4:
            st.metric("💼 총투자원금", f"{initial_investment:,.0f}원")
            st.metric("🎯 투자 성과", "📈" if profit_loss > 0 else "📉")
    
    st.markdown("---")
    
    # 메인 컨텐츠
    col1, col2, col3, col4 = st.columns(4)
    
    # 1. 실시간 통계
    with col1:
        st.subheader("📊 실시간 통계")
        
        # 최근 거래 데이터
        recent_trades = dashboard.get_recent_trades(10)
        if not recent_trades.empty:
            total_trades = len(recent_trades)
            buy_trades = len(recent_trades[recent_trades['action'] == 'buy'])
            sell_trades = len(recent_trades[recent_trades['action'] == 'sell'])
            
            st.metric("총 거래 수", total_trades)
            st.metric("매수 거래", buy_trades)
            st.metric("매도 거래", sell_trades)
            
            if total_trades > 0:
                win_rate = (buy_trades / total_trades) * 100
                st.metric("매수 비율", f"{win_rate:.1f}%")
    
    # 2. 성과 지표
    with col2:
        st.subheader("🎯 성과 지표")
        
        performance = dashboard.get_performance_metrics(7)
        if not performance.empty:
            latest = performance.iloc[0]
            st.metric("승률", f"{latest.get('win_rate', 0):.1f}%")
            st.metric("수익률", f"{latest.get('total_profit_loss_percentage', 0):.2f}%")
            st.metric("최대 낙폭", f"{latest.get('max_drawdown', 0):.2f}%")
            st.metric("샤프 비율", f"{latest.get('sharpe_ratio', 0):.2f}")
    
    # 3. 반성 시스템
    with col3:
        st.subheader("🤔 반성 시스템")
        
        reflections = dashboard.get_trading_reflections(5)
        if not reflections.empty:
            avg_score = reflections['performance_score'].mean()
            st.metric("평균 성과 점수", f"{avg_score:.2f}")
            
            reflection_types = reflections['reflection_type'].value_counts()
            st.metric("즉시 반성", reflection_types.get('immediate', 0))
            st.metric("주기적 반성", reflection_types.get('daily', 0) + 
                     reflection_types.get('weekly', 0) + 
                     reflection_types.get('monthly', 0))

            # 반성 상세보기 진입 버튼
            if st.button("🔍 반성 상세보기", key="reflection_detail_btn"):
                st.session_state.show_reflection_detail = True
    
    # 4. 학습 인사이트
    with col4:
        st.subheader("💡 학습 인사이트")
        
        insights = dashboard.get_learning_insights(5)
        if not insights.empty:
            st.metric("발견된 인사이트", len(insights))
            
            high_priority = len(insights[insights['priority_level'] == 'high'])
            st.metric("높은 우선순위", high_priority)
            
            implemented = len(insights[insights['status'] == 'implemented'])
            st.metric("구현된 인사이트", implemented)
            
            # 클릭 가능한 인사이트 목록
            if st.button("🔍 인사이트 상세보기", key="insight_detail_btn"):
                st.session_state.show_insight_detail = True
    
    st.markdown("---")
    
    # 차트 섹션
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 가격 차트")
        market_data = dashboard.get_market_data(50)
        if not market_data.empty:
            price_fig = create_price_chart(market_data)
            st.plotly_chart(price_fig, use_container_width=True)
        else:
            st.info("시장 데이터가 없습니다.")
    
    with col2:
        st.subheader("📊 거래량 분석")
        trades_data = dashboard.get_recent_trades(20)
        if not trades_data.empty:
            volume_fig = create_trading_volume_chart(trades_data)
            st.plotly_chart(volume_fig, use_container_width=True)
        else:
            st.info("거래 데이터가 없습니다.")
    
    # 성과 차트
    st.subheader("📊 성과 분석")
    performance_data = dashboard.get_performance_metrics(30)
    if not performance_data.empty:
        perf_fig = create_performance_chart(performance_data)
        st.plotly_chart(perf_fig, use_container_width=True)
    else:
        st.info("성과 데이터가 없습니다.")
    
    # 상세 데이터 테이블
    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["💰 재정 상세", "📋 최근 거래", "🤔 반성 데이터", "💡 학습 인사이트", "🔧 전략 개선"])
    
    with tab1:
        st.subheader("💰 재정 상세 정보")
        
        # 재정 요약 카드
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 자산 구성")
            if not recent_trades.empty:
                latest_trade = recent_trades.iloc[0]
                current_krw = latest_trade.get('balance_krw', 0)  # KRW잔고: 원화보유잔고
                current_btc = latest_trade.get('balance_btc', 0)
                btc_value = current_btc * latest_trade.get('price', 0)  # BTC가치: 비트코인투자자산가치
                total_assets = current_krw + btc_value  # 총보유자산 = KRW잔고 + BTC가치
                
                # 자산 구성 파이 차트
                if total_assets > 0:
                    fig = go.Figure(data=[go.Pie(
                        labels=['KRW잔고', 'BTC가치'],
                        values=[current_krw, btc_value],
                        hole=0.3,
                        marker_colors=['#00D4AA', '#FF6B6B']
                    )])
                    fig.update_layout(title="자산 구성 비율", height=300)
                    st.plotly_chart(fig, use_container_width=True)
                
                # 자산 상세 정보
                st.markdown("#### 자산 세부사항")
                st.write(f"**총보유자산**: {total_assets:,.0f}원")
                st.write(f"**KRW잔고**: {current_krw:,.0f}원 ({(current_krw/total_assets*100):.1f}%)")
                st.write(f"**BTC가치**: {btc_value:,.0f}원 ({(btc_value/total_assets*100):.1f}%)")
        
        with col2:
            st.markdown("### 📈 투자 성과")
            if not recent_trades.empty:
                # 수익/손실 = 총투자원금 - 총보유자산
                profit_loss = total_assets - initial_investment
                # 수익률 = (수익손실) / 총투자원금
                profit_rate = (profit_loss / initial_investment) * 100 if initial_investment > 0 else 0
                
                # 성과 지표
                st.metric("💰 총투자원금", f"{initial_investment:,.0f}원")
                st.metric("📊 총보유자산", f"{total_assets:,.0f}원")
                st.metric("📈 수익/손실", f"{profit_loss:+,.0f}원")
                st.metric("🎯 수익률", f"{profit_rate:+.2f}%")
                
                # 투자 성과 등급
                if profit_rate >= 20:
                    grade = "🟢 A+ (우수)"
                elif profit_rate >= 10:
                    grade = "🟢 A (양호)"
                elif profit_rate >= 0:
                    grade = "🟡 B (보통)"
                elif profit_rate >= -10:
                    grade = "🟠 C (주의)"
                else:
                    grade = "🔴 D (위험)"
                
                st.markdown(f"#### 투자 성과 등급: {grade}")
        
        # 투자 내역 테이블
        st.markdown("### 📋 투자 내역")
        if not recent_trades.empty:
            # 투자 내역 데이터 준비
            investment_df = recent_trades[['timestamp', 'action', 'price', 'amount', 'total_value', 'balance_krw', 'balance_btc']].copy()
            investment_df['timestamp'] = pd.to_datetime(investment_df['timestamp'])
            investment_df['action_kr'] = investment_df['action'].map({'buy': '매수', 'sell': '매도'})
            investment_df['btc_value'] = investment_df['balance_btc'] * investment_df['price']
            investment_df['total_portfolio'] = investment_df['balance_krw'] + investment_df['btc_value']
            
            # 컬럼명 한글화
            display_df = investment_df[['timestamp', 'action_kr', 'price', 'amount', 'total_value', 'balance_krw', 'balance_btc', 'btc_value', 'total_portfolio']].copy()
            display_df.columns = ['시간', '행동', 'BTC가격', '수량', '거래금액', 'KRW잔고', 'BTC잔고', 'BTC가치', '총보유자산']
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("투자 내역이 없습니다.")
    
    with tab2:
        st.subheader("📋 최근 거래 기록")
        recent_trades = dashboard.get_recent_trades(20)
        if not recent_trades.empty:
            # 시간 포맷팅
            recent_trades['timestamp'] = pd.to_datetime(recent_trades['timestamp'])
            recent_trades['created_at'] = pd.to_datetime(recent_trades['created_at'])
            
            # 컬럼명 한글화
            display_df = recent_trades.copy()
            display_df.columns = ['ID', '시간', '결정', '행동', '가격', '수량', '총액', '수수료', 
                                'KRW 잔고', 'BTC 잔고', '신뢰도', '이유', '상태', '생성일']
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("거래 기록이 없습니다.")
    
    with tab3:
        st.subheader("🤔 거래 반성 데이터")
        reflections = dashboard.get_trading_reflections(10)
        if not reflections.empty:
            # 시간 포맷팅
            reflections['created_at'] = pd.to_datetime(reflections['created_at'])
            
            # 컬럼명 한글화
            display_df = reflections[['trade_id', 'reflection_type', 'performance_score', 
                                    'profit_loss', 'decision_quality_score', 'timing_score', 
                                    'risk_management_score', 'created_at']].copy()
            display_df.columns = ['거래ID', '반성유형', '성과점수', '손익', '의사결정품질', 
                                '타이밍점수', '리스크관리', '생성일']
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("반성 데이터가 없습니다.")
    
    with tab4:
        st.subheader("💡 학습 인사이트")
        insights = dashboard.get_learning_insights(10)
        if not insights.empty:
            # 시간 포맷팅
            insights['created_at'] = pd.to_datetime(insights['created_at'])
            
            # 컬럼명 한글화
            display_df = insights[['insight_type', 'insight_title', 'confidence_level', 
                                 'priority_level', 'status', 'created_at']].copy()
            display_df.columns = ['유형', '제목', '신뢰도', '우선순위', '상태', '생성일']
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("학습 인사이트가 없습니다.")
    
    with tab5:
        st.subheader("🔧 전략 개선 제안")
        improvements = dashboard.get_strategy_improvements(10)
        if not improvements.empty:
            # 시간 포맷팅
            improvements['created_at'] = pd.to_datetime(improvements['created_at'])
            
            # 컬럼명 한글화
            display_df = improvements[['improvement_type', 'reason', 'expected_impact', 
                                     'success_metric', 'status', 'created_at']].copy()
            display_df.columns = ['개선유형', '이유', '예상효과', '성공지표', '상태', '생성일']
            
            st.dataframe(display_df, use_container_width=True)
            
            # 전략 개선 상태 변경 기능
            st.subheader("🔧 전략 개선 상태 관리")
            
            for _, improvement in improvements.iterrows():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**{improvement['improvement_type']}**: {improvement['reason'][:50]}...")
                    st.write(f"현재 상태: {improvement['status']} | 성공지표: {improvement['success_metric']:.2f}")
                
                with col2:
                    if improvement['status'] == 'proposed':
                        if st.button(f"적용", key=f"apply_{improvement['id']}"):
                            if dashboard.update_strategy_improvement_status(improvement['id'], 'implemented'):
                                st.success("✅ 전략 개선이 적용되었습니다!")
                                st.rerun()
                            else:
                                st.error("❌ 적용 실패")
                
                with col3:
                    if improvement['status'] == 'implemented':
                        if st.button(f"검증", key=f"validate_{improvement['id']}"):
                            if dashboard.update_strategy_improvement_status(improvement['id'], 'validated'):
                                st.success("✅ 전략 개선이 검증되었습니다!")
                                st.rerun()
                            else:
                                st.error("❌ 검증 실패")
                
                st.markdown("---")
        else:
            st.info("전략 개선 제안이 없습니다.")
    
    # 푸터
    st.markdown("---")
    st.markdown("🔄 자동 새로고침: 30초마다 데이터가 업데이트됩니다.")
    st.markdown("📊 마지막 업데이트: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # 개발용: 테스트 전략 개선 생성 (나중에 제거 가능)
    if st.sidebar.button("🧪 테스트 전략 개선 생성"):
        try:
            connection = dashboard.get_connection()
            cursor = connection.cursor()
            
            test_improvements = [
                ("condition", "기존 진입 조건", "강화된 진입 조건", "승률 개선을 위한 조건 강화", "승률 10% 향상 예상", 0.7, "proposed"),
                ("risk", "기존 리스크 관리", "강화된 리스크 관리", "최대 낙폭 감소를 위한 리스크 관리 강화", "최대 낙폭 20% 감소 예상", 0.8, "proposed"),
                ("parameter", "기존 파라미터", "AI 최적화 파라미터", "AI 분석을 통한 파라미터 최적화", "수익률 15% 향상 예상", 0.75, "proposed")
            ]
            
            for improvement in test_improvements:
                query = """
                INSERT INTO strategy_improvements 
                (improvement_type, old_value, new_value, reason, expected_impact, success_metric, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, improvement)
            
            connection.commit()
            cursor.close()
            connection.close()
            
            st.success("✅ 테스트 전략 개선이 생성되었습니다!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ 테스트 데이터 생성 실패: {e}")

if __name__ == "__main__":
    main()
