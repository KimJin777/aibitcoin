"""
반성 및 회고 데이터 뷰어
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from database.connection import get_db_connection
from mysql.connector import Error
from utils.logger import get_logger

class ReflectionViewer:
    """반성 및 회고 데이터 뷰어"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.connection = get_db_connection()
    
    def get_recent_reflections(self, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 반성 데이터 조회"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            select_query = """
            SELECT tr.*, t.decision, t.action, t.price, t.amount, t.total_value
            FROM trading_reflections tr
            JOIN trades t ON tr.trade_id = t.id
            ORDER BY tr.created_at DESC
            LIMIT %s
            """
            
            cursor.execute(select_query, (limit,))
            reflections = cursor.fetchall()
            
            cursor.close()
            return reflections
            
        except Error as e:
            self.logger.error(f"최근 반성 데이터 조회 오류: {e}")
            return []
    
    def get_performance_metrics(self, period_type: str = 'daily', days: int = 30) -> List[Dict[str, Any]]:
        """성과 지표 조회"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            select_query = """
            SELECT * FROM performance_metrics
            WHERE period_type = %s
            AND period_start >= DATE_SUB(NOW(), INTERVAL %s DAY)
            ORDER BY period_start DESC
            """
            
            cursor.execute(select_query, (period_type, days))
            metrics = cursor.fetchall()
            
            cursor.close()
            return metrics
            
        except Error as e:
            self.logger.error(f"성과 지표 조회 오류: {e}")
            return []
    
    def get_learning_insights(self, insight_type: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """학습 인사이트 조회"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            if insight_type:
                select_query = """
                SELECT * FROM learning_insights
                WHERE insight_type = %s
                ORDER BY created_at DESC
                LIMIT %s
                """
                cursor.execute(select_query, (insight_type, limit))
            else:
                select_query = """
                SELECT * FROM learning_insights
                ORDER BY created_at DESC
                LIMIT %s
                """
                cursor.execute(select_query, (limit,))
            
            insights = cursor.fetchall()
            
            cursor.close()
            return insights
            
        except Error as e:
            self.logger.error(f"학습 인사이트 조회 오류: {e}")
            return []
    
    def get_strategy_improvements(self, status: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """전략 개선 제안 조회"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            if status:
                select_query = """
                SELECT * FROM strategy_improvements
                WHERE status = %s
                ORDER BY created_at DESC
                LIMIT %s
                """
                cursor.execute(select_query, (status, limit))
            else:
                select_query = """
                SELECT * FROM strategy_improvements
                ORDER BY created_at DESC
                LIMIT %s
                """
                cursor.execute(select_query, (limit,))
            
            improvements = cursor.fetchall()
            
            cursor.close()
            return improvements
            
        except Error as e:
            self.logger.error(f"전략 개선 제안 조회 오류: {e}")
            return []
    
    def get_reflection_summary(self, days: int = 30) -> Dict[str, Any]:
        """반성 요약 정보"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # 전체 반성 수
            cursor.execute("""
                SELECT COUNT(*) as total_reflections
                FROM trading_reflections
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            """, (days,))
            total_reflections = cursor.fetchone()['total_reflections']
            
            # 반성 유형별 통계
            cursor.execute("""
                SELECT reflection_type, COUNT(*) as count
                FROM trading_reflections
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY reflection_type
            """, (days,))
            reflection_types = {row['reflection_type']: row['count'] for row in cursor.fetchall()}
            
            # 평균 성과 점수
            cursor.execute("""
                SELECT AVG(performance_score) as avg_performance_score
                FROM trading_reflections
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            """, (days,))
            avg_performance = cursor.fetchone()['avg_performance_score'] or 0
            
            # 최근 학습 인사이트 수
            cursor.execute("""
                SELECT COUNT(*) as recent_insights
                FROM learning_insights
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            """, (days,))
            recent_insights = cursor.fetchone()['recent_insights']
            
            # 최근 전략 개선 제안 수
            cursor.execute("""
                SELECT COUNT(*) as recent_improvements
                FROM strategy_improvements
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            """, (days,))
            recent_improvements = cursor.fetchone()['recent_improvements']
            
            cursor.close()
            
            return {
                'total_reflections': total_reflections,
                'reflection_types': reflection_types,
                'avg_performance_score': avg_performance,
                'recent_insights': recent_insights,
                'recent_improvements': recent_improvements,
                'period_days': days
            }
            
        except Error as e:
            self.logger.error(f"반성 요약 정보 조회 오류: {e}")
            return {}
    
    def print_reflection_summary(self, days: int = 30):
        """반성 요약 정보 출력"""
        summary = self.get_reflection_summary(days)
        
        print("=" * 60)
        print(f"📊 반성 시스템 요약 ({days}일간)")
        print("=" * 60)
        
        print(f"📈 총 반성 수: {summary.get('total_reflections', 0)}건")
        print(f"📊 평균 성과 점수: {summary.get('avg_performance_score', 0):.2f}")
        print(f"💡 최근 학습 인사이트: {summary.get('recent_insights', 0)}개")
        print(f"🔧 최근 전략 개선 제안: {summary.get('recent_improvements', 0)}개")
        
        print("\n📋 반성 유형별 통계:")
        for reflection_type, count in summary.get('reflection_types', {}).items():
            print(f"  - {reflection_type}: {count}건")
        
        print("=" * 60)
    
    def print_recent_reflections(self, limit: int = 5):
        """최근 반성 데이터 출력"""
        reflections = self.get_recent_reflections(limit)
        
        print("=" * 60)
        print(f"🤔 최근 반성 데이터 ({limit}건)")
        print("=" * 60)
        
        for i, reflection in enumerate(reflections, 1):
            print(f"\n{i}. 거래 ID: {reflection['trade_id']}")
            print(f"   📅 생성일: {reflection['created_at']}")
            print(f"   🔄 반성 유형: {reflection['reflection_type']}")
            print(f"   📊 성과 점수: {reflection['performance_score']:.2f}")
            print(f"   💰 손익: {reflection['profit_loss']:,.0f}원 ({reflection['profit_loss_percentage']:.2f}%)")
            print(f"   🎯 의사결정 품질: {reflection['decision_quality_score']:.2f}")
            print(f"   ⏰ 타이밍 점수: {reflection['timing_score']:.2f}")
            print(f"   🛡️ 리스크 관리: {reflection['risk_management_score']:.2f}")
            
            if reflection['ai_analysis']:
                print(f"   🤖 AI 분석: {reflection['ai_analysis'][:100]}...")
            
            if reflection['improvement_suggestions']:
                print(f"   💡 개선 제안: {reflection['improvement_suggestions'][:100]}...")
        
        print("=" * 60)
    
    def print_performance_metrics(self, period_type: str = 'daily', days: int = 30):
        """성과 지표 출력"""
        metrics = self.get_performance_metrics(period_type, days)
        
        print("=" * 60)
        print(f"📈 성과 지표 ({period_type}, {days}일간)")
        print("=" * 60)
        
        for i, metric in enumerate(metrics, 1):
            print(f"\n{i}. 기간: {metric['period_start']} ~ {metric['period_end']}")
            print(f"   📊 총 거래 수: {metric['total_trades']}건")
            print(f"   ✅ 승리 거래: {metric['winning_trades']}건")
            print(f"   ❌ 패배 거래: {metric['losing_trades']}건")
            print(f"   🎯 승률: {metric['win_rate']:.2%}")
            print(f"   💰 총 손익: {metric['total_profit_loss']:,.0f}원 ({metric['total_profit_loss_percentage']:.2f}%)")
            print(f"   📉 최대 낙폭: {metric['max_drawdown']:.2%}")
            print(f"   📊 샤프 비율: {metric['sharpe_ratio']:.2f}")
        
        print("=" * 60)
    
    def print_learning_insights(self, insight_type: str = None, limit: int = 10):
        """학습 인사이트 출력"""
        insights = self.get_learning_insights(insight_type, limit)
        
        print("=" * 60)
        print(f"💡 학습 인사이트 ({'전체' if insight_type is None else insight_type}, {limit}건)")
        print("=" * 60)
        
        for i, insight in enumerate(insights, 1):
            print(f"\n{i}. {insight['insight_title']}")
            print(f"   📅 생성일: {insight['created_at']}")
            print(f"   🏷️ 유형: {insight['insight_type']}")
            print(f"   🎯 신뢰도: {insight['confidence_level']:.2f}")
            print(f"   ⚡ 우선순위: {insight['priority_level']}")
            print(f"   📝 설명: {insight['insight_description'][:150]}...")
            print(f"   🔧 실행 항목: {insight['action_items'][:100]}...")
        
        print("=" * 60)
    
    def print_strategy_improvements(self, status: str = None, limit: int = 10):
        """전략 개선 제안 출력"""
        improvements = self.get_strategy_improvements(status, limit)
        
        print("=" * 60)
        print(f"🔧 전략 개선 제안 ({'전체' if status is None else status}, {limit}건)")
        print("=" * 60)
        
        for i, improvement in enumerate(improvements, 1):
            print(f"\n{i}. {improvement['improvement_type']} 개선")
            print(f"   📅 생성일: {improvement['created_at']}")
            print(f"   📊 상태: {improvement['status']}")
            print(f"   💡 이유: {improvement['reason'][:100]}...")
            print(f"   🎯 예상 효과: {improvement['expected_impact'][:100]}...")
            print(f"   📈 성공 지표: {improvement['success_metric']:.2f}")
            
            if improvement['old_value']:
                print(f"   🔄 변경: {improvement['old_value'][:50]} → {improvement['new_value'][:50]}")
        
        print("=" * 60)

# 전역 뷰어 객체
viewer = ReflectionViewer()

def view_reflection_summary(days: int = 30):
    """반성 요약 정보 보기 (편의 함수)"""
    viewer.print_reflection_summary(days)

def view_recent_reflections(limit: int = 5):
    """최근 반성 데이터 보기 (편의 함수)"""
    viewer.print_recent_reflections(limit)

def view_performance_metrics(period_type: str = 'daily', days: int = 30):
    """성과 지표 보기 (편의 함수)"""
    viewer.print_performance_metrics(period_type, days)

def view_learning_insights(insight_type: str = None, limit: int = 10):
    """학습 인사이트 보기 (편의 함수)"""
    viewer.print_learning_insights(insight_type, limit)

def view_strategy_improvements(status: str = None, limit: int = 10):
    """전략 개선 제안 보기 (편의 함수)"""
    viewer.print_strategy_improvements(status, limit)

if __name__ == "__main__":
    # 데이터베이스 초기화
    from database.connection import init_database
    init_database()
    
    # 전체 요약 정보 출력
    view_reflection_summary()
    
    # 최근 반성 데이터 출력
    view_recent_reflections()
    
    # 성과 지표 출력
    view_performance_metrics()
    
    # 학습 인사이트 출력
    view_learning_insights()
    
    # 전략 개선 제안 출력
    view_strategy_improvements()
