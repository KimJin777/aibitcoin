"""
매매 실행 모듈
AI 결정에 따른 실제 매매를 실행합니다.
"""

import time
from typing import Optional, Dict, Any
from config.settings import get_trading_config
from database.trade_recorder import save_trade_record, save_market_data_record, save_system_log_record

def execute_trading_decision(upbit, decision: Dict[str, Any], investment_status: Optional[Dict[str, Any]], market_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """AI 결정에 따른 매매 실행"""
    print("=" * 50)
    print("🔄 매매 실행 중")
    print("=" * 50)
    
    execution_result = {
        'action': 'none',
        'price': 0,
        'amount': 0,
        'total_value': 0,
        'fee': 0,
        'order_id': '',
        'status': 'skipped',
        'success': False
    }
    
    if investment_status is None:
        print("❌ 투자 상태 정보가 없어 매매를 건너뜁니다.")
        return execution_result
    
    trading_config = get_trading_config()
    min_trade_amount = trading_config['min_amount']
    trade_ratio = trading_config['trade_ratio']
    fee_rate = trading_config['fee_rate']
    
    krw_balance = investment_status.get('krw_balance', 0)
    btc_balance = investment_status.get('btc_balance', 0)
    current_price = investment_status.get('current_price', 0)
    
    print(f"💰 보유 현금: {krw_balance:,.2f}원")
    print(f"₿ 보유 비트코인: {btc_balance:.8f} BTC")
    print(f"📊 현재 가격: {current_price:,.0f}원")
    
    if decision['decision'] == 'buy':
        print("🟢 매수 신호 감지")
        
        # 최소 거래금액 확인
        if krw_balance < min_trade_amount:
            print(f"❌ 보유 현금이 부족하여 매수 건너뜀")
            print(f"   필요 금액: {min_trade_amount:,}원")
            print(f"   보유 현금: {krw_balance:,.2f}원")
            execution_result['status'] = 'insufficient_balance'
            # 시스템 로그 저장 (DB)
            try:
                save_system_log_record('WARNING', f"매수 건너뜀 - 잔고 부족: 필요 {min_trade_amount}, 보유 {krw_balance:,.2f}", 'trading.execution')
            except Exception:
                pass
            return execution_result
        
        # 매수 금액 계산 (전체 현금의 95% 사용, 수수료 고려)
        buy_amount = krw_balance * trade_ratio
        if buy_amount < min_trade_amount:
            buy_amount = min_trade_amount
        
        print(f"💰 매수 금액: {buy_amount:,.2f}원")
        
        # 수수료 계산 (0.05%)
        fee_amount = buy_amount * fee_rate
        actual_buy_amount = buy_amount - fee_amount
        
        print(f"💸 수수료: {fee_amount:,.2f}원 ({fee_rate*100:.3f}%)")
        print(f"📦 실제 구매 금액: {actual_buy_amount:,.2f}원")
        
        # 예상 구매 수량
        if current_price > 0:
            expected_btc = actual_buy_amount / current_price
            print(f"📊 예상 구매 수량: {expected_btc:.8f} BTC")
        
        # 매수 실행
        print(f"\n🚀 {buy_amount:,.2f}원 비트코인 매수를 실행합니다...")
        print("⚠️ 실제 거래가 발생합니다!")
        
        try:
            result = upbit.buy_market_order("KRW-BTC", buy_amount)
            if result:
                print("✅ 매수 주문 성공!")
                print(f"📋 주문 결과: {result}")
                
                # 거래 결과 정보 업데이트
                execution_result.update({
                    'action': 'buy',
                    'price': current_price,
                    'amount': expected_btc,
                    'total_value': buy_amount,
                    'fee': fee_amount,
                    'order_id': result.get('uuid', ''),
                    'status': 'executed',
                    'success': True
                })
                
                # 주문 후 잠시 대기
                print("⏳ 주문 처리 중... (3초 대기)")
                time.sleep(3)
                
                # 매수 후 계좌 상태 재확인
                print("\n📊 매수 후 계좌 상태:")
                from .account import get_investment_status
                get_investment_status(upbit)
                
                # 거래 기록 저장
                save_trade_record(decision, execution_result, investment_status, market_data)
                
                return execution_result
            else:
                print("❌ 매수 주문 실패")
                execution_result['status'] = 'failed'
                return execution_result
        except Exception as e:
            print(f"❌ 매수 주문 중 오류: {e}")
            execution_result['status'] = 'error'
            return execution_result
            
    elif decision['decision'] == 'sell':
        print("🔴 매도 신호 감지")
        
        # 최소 거래금액 확인
        if btc_balance * current_price < min_trade_amount:
            print(f"❌ 보유 비트코인이 부족하여 매도 건너뜀")
            print(f"   필요 금액: {min_trade_amount:,}원")
            print(f"   보유 비트코인 가치: {btc_balance * current_price:,.2f}원")
            execution_result['status'] = 'insufficient_balance'
            # 시스템 로그 저장 (DB)
            try:
                save_system_log_record('WARNING', f"매도 건너뜀 - 수량 부족: 필요 {min_trade_amount}, 보유가치 {btc_balance * current_price:,.2f}", 'trading.execution')
            except Exception:
                pass
            return execution_result
        
        # 매도 수량 계산 (전체 비트코인의 95% 매도, 수수료 고려)
        sell_amount = btc_balance * trade_ratio
        if sell_amount * current_price < min_trade_amount:
            sell_amount = btc_balance  # 전체 매도
        
        print(f"₿ 매도 수량: {sell_amount:.8f} BTC")
        
        # 예상 매도 금액
        expected_sell_amount = sell_amount * current_price
        print(f"💰 예상 매도 금액: {expected_sell_amount:,.2f}원")
        
        # 매도 실행
        print(f"\n🚀 {sell_amount:.8f} BTC 비트코인 매도를 실행합니다...")
        print("⚠️ 실제 거래가 발생합니다!")
        
        try:
            result = upbit.sell_market_order("KRW-BTC", sell_amount)
            if result:
                print("✅ 매도 주문 성공!")
                print(f"📋 주문 결과: {result}")
                
                # 거래 결과 정보 업데이트
                execution_result.update({
                    'action': 'sell',
                    'price': current_price,
                    'amount': sell_amount,
                    'total_value': expected_sell_amount,
                    'fee': expected_sell_amount * fee_rate,
                    'order_id': result.get('uuid', ''),
                    'status': 'executed',
                    'success': True
                })
                
                # 주문 후 잠시 대기
                print("⏳ 주문 처리 중... (3초 대기)")
                time.sleep(3)
                
                # 매도 후 계좌 상태 재확인
                print("\n📊 매도 후 계좌 상태:")
                from .account import get_investment_status
                get_investment_status(upbit)
                
                # 거래 기록 저장
                save_trade_record(decision, execution_result, investment_status, market_data)
                
                return execution_result
            else:
                print("❌ 매도 주문 실패")
                execution_result['status'] = 'failed'
                return execution_result
        except Exception as e:
            print(f"❌ 매도 주문 중 오류: {e}")
            execution_result['status'] = 'error'
            return execution_result
            
    elif decision['decision'] == 'hold':
        print("🟡 보유 신호 - 현재 포지션 유지")
        print("📈 추가 매수나 매도 없이 현재 상태를 유지합니다.")
        
        execution_result.update({
            'action': 'hold',
            'price': current_price,
            'amount': 0,
            'total_value': 0,
            'fee': 0,
            'status': 'held',
            'success': True
        })
        
        # 보유 기록도 저장
        save_trade_record(decision, execution_result, investment_status, market_data)
        
        return execution_result
    
    else:
        print(f"❓ 알 수 없는 매매 신호: {decision['decision']}")
        execution_result['status'] = 'unknown_decision'
        return execution_result
