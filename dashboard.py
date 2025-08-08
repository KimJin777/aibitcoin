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
    
    # 제목
    st.title("🤖 GPT Bitcoin 자동매매 실시간 모니터링")
    st.markdown("---")
    
    # 사이드바 설정
    st.sidebar.title("📊 설정")
    refresh_interval = st.sidebar.slider("새로고침 간격 (초)", 5, 60, 30)
    
    # 자동 새로고침
    if st.sidebar.button("🔄 새로고침"):
        st.rerun()
    
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
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 최근 거래", "🤔 반성 데이터", "💡 학습 인사이트", "🔧 전략 개선"])
    
    with tab1:
        st.subheader("최근 거래 기록")
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
    
    with tab2:
        st.subheader("거래 반성 데이터")
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
    
    with tab3:
        st.subheader("학습 인사이트")
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
    
    with tab4:
        st.subheader("전략 개선 제안")
        improvements = dashboard.get_strategy_improvements(10)
        if not improvements.empty:
            # 시간 포맷팅
            improvements['created_at'] = pd.to_datetime(improvements['created_at'])
            
            # 컬럼명 한글화
            display_df = improvements[['improvement_type', 'reason', 'expected_impact', 
                                     'success_metric', 'status', 'created_at']].copy()
            display_df.columns = ['개선유형', '이유', '예상효과', '성공지표', '상태', '생성일']
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("전략 개선 제안이 없습니다.")
    
    # 푸터
    st.markdown("---")
    st.markdown("🔄 자동 새로고침: 30초마다 데이터가 업데이트됩니다.")
    st.markdown("📊 마지막 업데이트: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    main()
