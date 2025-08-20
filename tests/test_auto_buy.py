import os
import time
import pyupbit
from dotenv import load_dotenv
from openai import OpenAI

# 환경 변수 로드
load_dotenv()

def get_upbit_instance():
	"""
	업비트 인스턴스 생성
	"""
	access_key = os.getenv('UPBIT_ACCESS_KEY')
	secret_key = os.getenv('UPBIT_SECRET_KEY')
	
	if not access_key or not secret_key:
		print("❌ 업비트 API 키가 설정되지 않았습니다.")
		print("📝 .env 파일에 UPBIT_ACCESS_KEY와 UPBIT_SECRET_KEY를 설정해주세요.")
		return None
	
	try:
		upbit = pyupbit.Upbit(access_key, secret_key)
		return upbit
	except Exception as e:
		print(f"❌ 업비트 인스턴스 생성 실패: {e}")
		return None

def show_account_info(upbit):
	"""
	계좌 정보 표시
	"""
	print("=" * 60)
	print("📊 현재 계좌 상태")
	print("=" * 60)
	
	try:
		# 전체 잔고 조회
		balances = upbit.get_balances()
		if balances is None:
			print("❌ 잔고 조회 실패")
			return None
		
		print(f"🔍 잔고 데이터 구조 확인: {type(balances)}")
		if balances:
			print(f"🔍 첫 번째 잔고 데이터: {balances[0] if isinstance(balances, list) else balances}")
		
		# KRW 잔고
		krw_balance = 0
		btc_balance = 0
		btc_avg_price = 0
		
		# balances가 리스트인 경우
		if isinstance(balances, list):
			for balance in balances:
				if isinstance(balance, dict):
					currency = balance.get('currency', '')
					if currency == 'KRW':
						krw_balance = float(balance.get('balance', 0))
					elif currency == 'BTC':
						btc_balance = float(balance.get('balance', 0))
						btc_avg_price = float(balance.get('avg_buy_price', 0))
		# balances가 딕셔너리인 경우
		elif isinstance(balances, dict):
			for currency, balance_data in balances.items():
				if currency == 'KRW':
					krw_balance = float(balance_data.get('balance', 0))
				elif currency == 'BTC':
					btc_balance = float(balance_data.get('balance', 0))
					btc_avg_price = float(balance_data.get('avg_buy_price', 0))
		
		print(f"💰 보유 현금: {krw_balance:,.2f}원")
		print(f"₿ 보유 비트코인: {btc_balance:.8f} BTC")
		if btc_avg_price > 0:
			print(f"📈 평균 매수가: {btc_avg_price:,.0f}원")
		
		# 현재 비트코인 가격
		current_price = pyupbit.get_current_price("KRW-BTC")
		if current_price:
			print(f"📊 현재 비트코인 가격: {current_price:,.0f}원")
			
			# 비트코인 평가금액
			if btc_balance > 0:
				btc_value = btc_balance * current_price
				print(f"💎 비트코인 평가금액: {btc_value:,.2f}원")
				
				# 총 자산
				total_assets = krw_balance + btc_value
				print(f"🏦 총 자산: {total_assets:,.2f}원")
				
				# 수익률 계산
				if btc_avg_price > 0:
					profit_loss = current_price - btc_avg_price
					profit_loss_percent = (profit_loss / btc_avg_price) * 100
					print(f"📈 수익/손실: {profit_loss:,.0f}원 ({profit_loss_percent:+.2f}%)")
		
		return {
			'krw_balance': krw_balance,
			'btc_balance': btc_balance,
			'btc_avg_price': btc_avg_price,
			'current_price': current_price
		}
		
	except Exception as e:
		print(f"❌ 계좌 정보 조회 실패: {e}")
		print(f"🔍 오류 상세: {type(e).__name__}")
		return None

def auto_buy_50000(upbit):
	"""
	무조건 5만원 비트코인 구매
	"""
	print("=" * 60)
	print("🛒 5만원 비트코인 자동 구매")
	print("=" * 60)
	
	buy_amount = 50000  # 5만원
	
	try:
		# 구매 전 계좌 상태 확인
		print("📊 구매 전 계좌 상태:")
		account_info = show_account_info(upbit)
		if account_info is None:
			return False
		
		krw_balance = account_info['krw_balance']
		current_price = account_info['current_price']
		
		# 잔고 확인
		if krw_balance < buy_amount:
			print(f"\n❌ 잔고 부족으로 구매를 건너뜁니다.")
			print(f"   필요 금액: {buy_amount:,}원")
			print(f"   보유 현금: {krw_balance:,.2f}원")
			return False
		
		print(f"\n✅ 잔고 확인 완료: {krw_balance:,.2f}원")
		print(f"💰 구매 금액: {buy_amount:,}원")
		
		# 수수료 계산 (0.05%)
		fee_rate = 0.0005
		fee_amount = buy_amount * fee_rate
		actual_buy_amount = buy_amount - fee_amount
		
		print(f"💸 수수료: {fee_amount:,.2f}원 (0.05%)")
		print(f"📦 실제 구매 금액: {actual_buy_amount:,.2f}원")
		
		# 예상 구매 수량
		if current_price:
			expected_btc = actual_buy_amount / current_price
			print(f"📊 예상 구매 수량: {expected_btc:.8f} BTC")
		
		# 구매 실행
		print(f"\n🚀 {buy_amount:,}원 비트코인 구매를 실행합니다...")
		print("⚠️ 실제 거래가 발생합니다!")
		
		# 3초 카운트다운
		for i in range(3, 0, -1):
			print(f"⏳ {i}초 후 구매 실행...")
			time.sleep(1)
		
		result = upbit.buy_market_order("KRW-BTC", buy_amount)
		
		if result:
			print("✅ 구매 주문 성공!")
			print(f"📋 주문 결과: {result}")
			
			# 주문 후 잠시 대기
			print("⏳ 주문 처리 중... (5초 대기)")
			time.sleep(5)
			
			# 구매 후 계좌 상태 재확인
			print("\n📊 구매 후 계좌 상태:")
			show_account_info(upbit)
			
			return True
		else:
			print("❌ 구매 주문 실패")
			return False
			
	except Exception as e:
		print(f"❌ 구매 실행 중 오류: {e}")
		return False

if __name__ == "__main__":
	# 수동 실행용 (pytest가 아닌 직접 실행)
	upbit = get_upbit_instance()
	if upbit:
		auto_buy_50000(upbit)
