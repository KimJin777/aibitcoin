"""
거래 시스템과 반성 시스템 통합 테스트
"""

import sys
import os
from datetime import datetime, timedelta
import numpy as np

# 프로젝트 루트를 Python 경로에 추가 (tests/ 부모)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import init_database
from database.trade_recorder import TradeRecorder
from analysis.reflection_system import create_immediate_reflection
from utils.json_cleaner import clean_json_data

def test_trading_with_reflection():
	"""거래 시스템과 반성 시스템 통합 테스트"""
	print("🚀 거래 시스템과 반성 시스템 통합 테스트 시작")
	print("=" * 60)
	
	# 1. 데이터베이스 초기화
	print("📊 데이터베이스 초기화...")
	try:
		init_database()
		print("✅ 데이터베이스 초기화 완료")
	except Exception as e:
		print(f"❌ 데이터베이스 초기화 실패: {e}")
		return
	
	# 2. 거래 기록기 생성
	recorder = TradeRecorder()
	
	# 3. 테스트용 거래 데이터 생성
	print("\n📝 테스트용 거래 데이터 생성...")
	
	# 시장 데이터 (NaN, Infinity 포함)
	market_data = {
		'current_price': 50000000.0,
		'technical_indicators': {
			'rsi': 65.5,
			'macd': np.nan,  # 문제가 될 수 있는 값
			'sma_20': 48000000.0,
			'ema_12': np.inf,  # 문제가 될 수 있는 값
			'bb_position': 0.7,
			'stoch_k': 75.0
		},
		'fear_greed_index': {
			'value': 45,
			'classification': 'Fear'
		},
		'news_analysis': {
			'sentiment': 'neutral',
			'positive_count': 3,
			'negative_count': 2
		}
	}
	
	# 거래 결정
	decision = {
		'decision': 'buy',
		'confidence': 0.75,
		'reason': 'RSI가 중립 구간이고, 볼린저 밴드 중간 위치에서 매수 신호',
		'risk_level': 'medium'
	}
	
	# 실행 결과
	execution_result = {
		'action': 'buy',
		'price': 50000000.0,
		'amount': 0.001,
		'total_value': 50000.0,
		'fee': 25.0,
		'order_id': 'test_order_123',
		'status': 'executed'
	}
	
	# 투자 상태
	investment_status = {
		'krw_balance': 1000000.0,
		'btc_balance': 0.005,
		'total_value': 1250000.0
	}
	
	print("✅ 테스트 데이터 생성 완료")
	
	# 4. 거래 기록 저장 테스트
	print("\n💾 거래 기록 저장 테스트...")
	try:
		success = recorder.save_trade(decision, execution_result, investment_status, market_data)
		if success:
			print("✅ 거래 기록 저장 성공")
		else:
			print("❌ 거래 기록 저장 실패")
			return
	except Exception as e:
		print(f"❌ 거래 기록 저장 중 오류: {e}")
		return
	
	# 5. 즉시 반성 생성 테스트
	print("\n🤔 즉시 반성 생성 테스트...")
	try:
		# 최근 거래 ID 조회 (간단한 방법으로)
		trade_id = 1  # 테스트용으로 첫 번째 거래로 가정
		
		# 거래 데이터 준비
		trade_data = {
			'decision': decision,
			'execution_result': execution_result,
			'investment_status': investment_status
		}
		
		success = create_immediate_reflection(trade_id, trade_data, market_data)
		if success:
			print("✅ 즉시 반성 생성 성공")
		else:
			print("❌ 즉시 반성 생성 실패")
	except Exception as e:
		print(f"❌ 즉시 반성 생성 중 오류: {e}")
	
	print("\n🎉 통합 테스트 완료!")
	print("=" * 60)

if __name__ == "__main__":
	test_trading_with_reflection()
