"""
반성 시스템 테스트 스크립트
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any

# 프로젝트 루트 디렉토리를 Python 경로에 추가 (tests/의 부모 경로)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import init_database
from analysis.reflection_system import (
	create_immediate_reflection,
	create_periodic_reflection,
	analyze_learning_patterns,
	generate_strategy_improvements
)
from reflection_viewer import (
	view_reflection_summary,
	view_recent_reflections,
	view_performance_metrics,
	view_learning_insights,
	view_strategy_improvements
)

def test_reflection_system():
	"""반성 시스템 테스트"""
	print("=" * 60)
	print("🤔 반성 시스템 테스트 시작")
	print("=" * 60)
	
	try:
		# 데이터베이스 초기화
		print("📊 데이터베이스 초기화...")
		init_database()
		print("✅ 데이터베이스 초기화 완료")
		
		# 테스트용 거래 데이터 생성
		print("\n📝 테스트용 거래 데이터 생성...")
		test_trade_data = {
			'decision': 'buy',
			'confidence': 0.8,
			'reasoning': 'RSI 과매도 구간에서 매수 신호 발생',
			'price': 50000000,
			'amount': 0.001,
			'total_value': 50000,
			'fee': 25,
			'balance_krw': 1000000,
			'balance_btc': 0.002,
			'order_id': 'test_order_123',
			'status': 'executed'
		}
		
		test_market_data = {
			'current_price': 50000000,
			'rsi': 30.5,
			'macd': -0.5,
			'bollinger_upper': 52000000,
			'bollinger_lower': 48000000,
			'fear_greed_index': 25,
			'news_sentiment': 0.6,
			'trend': 'bullish'
		}
		
		# 즉시 반성 생성 테스트
		print("\n🤔 즉시 반성 생성 테스트...")
		reflection_created = create_immediate_reflection(1, test_trade_data, test_market_data)
		if reflection_created:
			print("✅ 즉시 반성 생성 성공")
		else:
			print("❌ 즉시 반성 생성 실패")
		
		# 주기적 회고 테스트
		print("\n📅 주기적 회고 테스트...")
		yesterday = datetime.now() - timedelta(days=1)
		start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
		end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
		
		daily_reflection_created = create_periodic_reflection('daily', start_date, end_date)
		if daily_reflection_created:
			print("✅ 일일 회고 생성 성공")
		else:
			print("❌ 일일 회고 생성 실패")
		
		# 학습 패턴 분석 테스트
		print("\n💡 학습 패턴 분석 테스트...")
		insights = analyze_learning_patterns()
		if insights:
			print(f"✅ 학습 패턴 분석 성공: {len(insights)}개 인사이트 발견")
			for insight in insights:
				print(f"  - {insight.get('insight_title', 'Unknown')}")
		else:
			print("✅ 학습 패턴 분석 완료 (새로운 인사이트 없음)")
		
		# 전략 개선 제안 테스트
		print("\n🔧 전략 개선 제안 테스트...")
		improvements = generate_strategy_improvements()
		if improvements:
			print(f"✅ 전략 개선 제안 성공: {len(improvements)}개 개선안 생성")
			for improvement in improvements:
				print(f"  - {improvement.get('improvement_type', 'Unknown')}: {improvement.get('reason', 'No reason')}")
		else:
			print("✅ 전략 개선 제안 완료 (새로운 개선안 없음)")
		
		# 반성 데이터 뷰어 테스트
		print("\n📊 반성 데이터 뷰어 테스트...")
		view_reflection_summary(7)  # 최근 7일간 데이터
		
		print("\n" + "=" * 60)
		print("🎉 반성 시스템 테스트 완료!")
		print("=" * 60)
		
	except Exception as e:
		print(f"❌ 테스트 중 오류 발생: {e}")
		import traceback
		traceback.print_exc()

def test_reflection_viewer():
	"""반성 뷰어 테스트"""
	print("\n" + "=" * 60)
	print("📊 반성 뷰어 테스트")
	print("=" * 60)
	
	try:
		# 최근 반성 데이터 조회
		print("\n🤔 최근 반성 데이터 조회...")
		view_recent_reflections(3)
		
		# 성과 지표 조회
		print("\n📈 성과 지표 조회...")
		view_performance_metrics('daily', 7)
		
		# 학습 인사이트 조회
		print("\n💡 학습 인사이트 조회...")
		view_learning_insights(limit=5)
		
		# 전략 개선 제안 조회
		print("\n🔧 전략 개선 제안 조회...")
		view_strategy_improvements(limit=5)
		
		print("\n✅ 반성 뷰어 테스트 완료!")
		
	except Exception as e:
		print(f"❌ 뷰어 테스트 중 오류 발생: {e}")
		import traceback
		traceback.print_exc()

if __name__ == "__main__":
	print("🚀 반성 시스템 테스트 시작")
	
	# 기본 반성 시스템 테스트
	test_reflection_system()
	
	# 반성 뷰어 테스트
	test_reflection_viewer()
	
	print("\n🎯 모든 테스트 완료!")
