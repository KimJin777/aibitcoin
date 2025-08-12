"""
계좌 관리 모듈
업비트 계좌 정보 조회, 잔고 확인, 투자 상태 분석 등을 수행합니다.
"""

import pyupbit
from typing import Optional, Dict, Any
from config.settings import TRADING_SYMBOL

def get_total_profit_loss(upbit) -> Optional[Dict[str, Any]]:
    """이익 조회 함수"""
    
    try:
        # 전체 잔고 조회
        balances = upbit.get_balances()
        if balances is None:
            print("❌ 잔고 조회 실패")
            return None
        
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
        

        print(f"₿ 보유 비트코인: {btc_balance:.8f} BTC")
        if btc_avg_price > 0:
            print(f"📈 평균 매수가: {btc_avg_price:,.0f}원")
        
        # 현재 비트코인 가격
        current_price = pyupbit.get_current_price(TRADING_SYMBOL)
        if current_price:
            print(f"📊 현재 비트코인 가격: {current_price:,.0f}원")
            
            # 비트코인 평가금액
            if btc_balance > 0:
                btc_value = btc_balance * current_price
                print(f"💎 비트코인 평가금액: {btc_value:,.2f}원")
                
                # 총 자산
                total_assets = krw_balance + btc_value
                print(f"🏦 총 자산: {total_assets:,.2f}원")
                
                # 비트코인 비중
                btc_ratio = (btc_value / total_assets) * 100
                print(f"📊 비트코인 비중: {btc_ratio:.2f}%")
                
                # 수익률 계산
                if btc_avg_price > 0:
                    profit_loss = current_price - btc_avg_price
                    profit_loss_percent = (profit_loss / btc_avg_price) * 100
                    print(f"📈 수익/손실: {profit_loss:,.0f}원 ({profit_loss_percent:+.2f}%)")
                    
                    # 총 투자금액 (평균 매수가 * 보유 수량)
                    total_investment = btc_avg_price * btc_balance
                    print(f"💼 총 투자금액: {total_investment:,.0f}원")
                    
                    # 총 수익/손실
                    total_profit_loss = btc_value - total_investment
                    total_profit_loss_percent = (total_profit_loss / total_investment) * 100
                    print(f"📊 총 수익/손실: {total_profit_loss:,.0f}원 ({total_profit_loss_percent:+.2f}%)")
                    
        else:
            print("❌ 현재 비트코인 가격 조회 실패")
            current_price = 0
        
        return {
            'krw_balance': krw_balance,
            'btc_balance': btc_balance,
            'btc_avg_price': btc_avg_price,
            'current_price': current_price
        }
        
    except Exception as e:
        print(f"❌ 계좌 상태 확인 실패: {e}")
        print(f"🔍 오류 상세: {type(e).__name__}")
        return total_profit_loss

def get_investment_status(upbit) -> Optional[Dict[str, Any]]:
    """현재 투자 상태 조회 함수"""
    print("=== 투자 상태 조회 중 ===")
    
    try:
        # 전체 잔고 조회
        balances = upbit.get_balances()
        if balances is None:
            print("❌ 잔고 조회 실패")
            return None
        
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
        current_price = pyupbit.get_current_price(TRADING_SYMBOL)
        if current_price:
            print(f"📊 현재 비트코인 가격: {current_price:,.0f}원")
            
            # 비트코인 평가금액
            if btc_balance > 0:
                btc_value = btc_balance * current_price
                print(f"💎 비트코인 평가금액: {btc_value:,.2f}원")
                
                # 총 자산
                total_assets = krw_balance + btc_value
                print(f"🏦 총 자산: {total_assets:,.2f}원")
                
                # 비트코인 비중
                btc_ratio = (btc_value / total_assets) * 100
                print(f"📊 비트코인 비중: {btc_ratio:.2f}%")
                
                # 수익률 계산
                if btc_avg_price > 0:
                    profit_loss = current_price - btc_avg_price
                    profit_loss_percent = (profit_loss / btc_avg_price) * 100
                    print(f"📈 수익/손실: {profit_loss:,.0f}원 ({profit_loss_percent:+.2f}%)")
                    
                    # 총 투자금액 (평균 매수가 * 보유 수량)
                    total_investment = btc_avg_price * btc_balance
                    print(f"💼 총 투자금액: {total_investment:,.0f}원")
                    
                    # 총 수익/손실
                    total_profit_loss = btc_value - total_investment
                    total_profit_loss_percent = (total_profit_loss / total_investment) * 100
                    print(f"📊 총 수익/손실: {total_profit_loss:,.0f}원 ({total_profit_loss_percent:+.2f}%)")
                    
                    # 투자 성과 등급
                    if total_profit_loss_percent >= 20:
                        performance_grade = "A+ (우수)"
                    elif total_profit_loss_percent >= 10:
                        performance_grade = "A (양호)"
                    elif total_profit_loss_percent >= 0:
                        performance_grade = "B (보통)"
                    elif total_profit_loss_percent >= -10:
                        performance_grade = "C (주의)"
                    else:
                        performance_grade = "D (위험)"
                    
                    print(f"🏆 투자 성과 등급: {performance_grade}")
        else:
            print("❌ 현재 비트코인 가격 조회 실패")
            current_price = 0
        
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

def get_pending_orders(upbit) -> list:
    """미체결 주문 조회"""
    try:
        pending_orders = upbit.get_order(TRADING_SYMBOL)
        if pending_orders is None:
            pending_orders = []
    except Exception as e:
        print(f"미체결 주문 조회 실패: {e}")
        pending_orders = []
    
    if pending_orders:
        print(f"\n미체결 주문: {len(pending_orders)}개")
        total_pending_value = 0
        for order in pending_orders:
            try:
                # 주문 데이터 구조 확인 및 안전한 접근
                if isinstance(order, dict):
                    order_type = "매수" if order.get('side') == 'bid' else "매도"
                    price = order.get('price')
                    volume = order.get('volume', 0)
                    
                    if price is not None and price != "시장가":
                        try:
                            order_value = float(price) * float(volume)
                            total_pending_value += order_value
                            print(f"  - {order_type}: {price:,.0f}원, {volume:.8f} BTC (가치: {order_value:,.0f}원)")
                        except (ValueError, TypeError):
                            print(f"  - {order_type}: {price}원, {volume} BTC (가치 계산 실패)")
                    else:
                        print(f"  - {order_type}: 시장가, {volume:.8f} BTC")
                else:
                    print(f"  - 주문 데이터 형식 오류: {order}")
            except Exception as e:
                print(f"  - 주문 데이터 처리 실패: {e}")
        
        if total_pending_value > 0:
            print(f"총 미체결 주문 가치: {total_pending_value:,.0f}원")
    else:
        print("미체결 주문 없음")
    
    return pending_orders

def get_recent_orders(upbit, limit: int = 10) -> list:
    """최근 거래 내역 조회"""
    try:
        print(f"\n=== 최근 거래 내역 ({limit}개) ===")
        recent_orders = upbit.get_order(TRADING_SYMBOL, state="done", limit=limit)
        if recent_orders is None:
            recent_orders = []
        
        if recent_orders:
            for order in recent_orders:
                try:
                    # 주문 데이터 구조 확인 및 안전한 접근
                    if isinstance(order, dict):
                        order_type = "매수" if order.get('side') == 'bid' else "매도"
                        order_time = order.get('created_at', '')[:19] if order.get('created_at') else '시간 없음'
                        volume = order.get('volume', 0)
                        price = order.get('price')
                        fee = order.get('paid_fee', 0)
                        
                        if price is not None and price != "시장가":
                            try:
                                order_value = float(price) * float(volume)
                                print(f"  - {order_time}: {order_type} {volume:.8f} BTC @ {price:,.0f}원 (수수료: {fee:.2f}원)")
                            except (ValueError, TypeError):
                                print(f"  - {order_time}: {order_type} {volume:.8f} BTC @ {price}원 (수수료: {fee:.2f}원)")
                        else:
                            print(f"  - {order_time}: {order_type} {volume:.8f} BTC @ 시장가 (수수료: {fee:.2f}원)")
                    else:
                        print(f"  - 주문 데이터 형식 오류: {order}")
                except Exception as e:
                    print(f"  - 주문 데이터 처리 실패: {e}")
        else:
            print("최근 거래 내역 없음")
    except Exception as e:
        print(f"거래 내역 조회 실패: {e}")
        recent_orders = []
    
    return recent_orders
