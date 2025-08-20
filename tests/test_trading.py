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

def check_account_status(upbit):
	"""
	계좌 상태 확인 (현금, 비트코인 보유량)
	"""
	print("=" * 50)
	print("📊 계좌 상태 확인")
	print("=" * 50)
	
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
		print(f"❌ 계좌 상태 확인 실패: {e}")
		print(f"🔍 오류 상세: {type(e).__name__}")
		return None

def buy_bitcoin_test(upbit, amount_krw=50000):
	"""
	지정된 금액만큼 비트코인 구매 테스트
	"""
	print("=" * 50)
	print(f"🛒 {amount_krw:,}원 비트코인 구매 테스트")
	print("=" * 50)
	
	try:
		# 현재 계좌 상태 확인
		account_status = check_account_status(upbit)
		if account_status is None:
			return False
		
		krw_balance = account_status['krw_balance']
		current_price = account_status['current_price']
		
		# 잔고 확인
		if krw_balance < amount_krw:
			print(f"❌ 잔고 부족: {krw_balance:,.2f}원 < {amount_krw:,}원")
			return False
		
		print(f"✅ 잔고 확인 완료: {krw_balance:,.2f}원")
		print(f"💰 구매 금액: {amount_krw:,}원")
		
		# 수수료 계산 (0.05%)
		fee_rate = 0.0005
		fee_amount = amount_krw * fee_rate
		actual_buy_amount = amount_krw - fee_amount
		
		print(f"💸 수수료: {fee_amount:,.2f}원 (0.05%)")
		print(f"📦 실제 구매 금액: {actual_buy_amount:,.2f}원")
		
		# 예상 구매 수량
		if current_price:
			expected_btc = actual_buy_amount / current_price
			print(f"📊 예상 구매 수량: {expected_btc:.8f} BTC")
		
		# 구매 실행
		print("\n🚀 구매 주문을 실행합니다...")
		result = upbit.buy_market_order("KRW-BTC", amount_krw)
		
		if result:
			print("✅ 구매 주문 성공!")
			print(f"📋 주문 결과: {result}")
			
			# 주문 후 잠시 대기
			print("⏳ 주문 처리 중... (3초 대기)")
			time.sleep(3)
			
			# 구매 후 계좌 상태 재확인
			print("\n📊 구매 후 계좌 상태:")
			check_account_status(upbit)
			
			return True
		else:
			print("❌ 구매 주문 실패")
			return False
			
	except Exception as e:
		print(f"❌ 구매 실행 중 오류: {e}")
		return False

def main():
	"""
	메인 실행 함수
	"""
	print("🚀 비트코인 구매 테스트 프로그램")
	print("=" * 50)
	
	# 업비트 인스턴스 생성
	upbit = get_upbit_instance()
	if upbit is None:
		return
	
	try:
		# 계좌 상태 확인
		account_status = check_account_status(upbit)
		if account_status is None:
			return
		
		# 사용자 입력
		print("\n" + "=" * 50)
		print("🛒 구매 테스트 옵션")
		print("=" * 50)
		print("1. 5만원 구매 테스트")
		print("2. 사용자 지정 금액 구매")
		print("3. 계좌 상태만 확인")
		
		choice = input("\n선택하세요 (1-3): ").strip()
		
		if choice == "1":
			# 5만원 구매 테스트
			buy_bitcoin_test(upbit, 50000)
			
		elif choice == "2":
			# 사용자 지정 금액
			try:
				amount = int(input("구매 금액을 입력하세요 (원): "))
				if amount >= 5000:  # 최소 거래금액
					buy_bitcoin_test(upbit, amount)
				else:
					print("❌ 최소 거래금액은 5,000원입니다.")
			except ValueError:
				print("❌ 올바른 금액을 입력해주세요.")
				
		elif choice == "3":
			# 계좌 상태만 확인
			print("✅ 계좌 상태 확인 완료")
			
		else:
			print("❌ 올바른 선택을 해주세요.")
			
	except KeyboardInterrupt:
		print("\n\n⏹️ 프로그램이 중단되었습니다.")
	except Exception as e:
		print(f"\n❌ 프로그램 실행 중 오류: {e}")

if __name__ == "__main__":
	main()
