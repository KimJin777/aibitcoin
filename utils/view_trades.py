"""
거래 기록 조회 스크립트
데이터베이스에 저장된 거래 기록을 조회하고 표시합니다.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.query import get_recent_trades, get_trade_statistics, get_market_data_history
from database.connection import init_database
from datetime import datetime

def print_trade_record(trade):
    """거래 기록을 보기 좋게 출력"""
    print(f"📅 {trade['timestamp']}")
    print(f"   결정: {trade['decision']} | 액션: {trade['action']}")
    print(f"   가격: {trade['price']:,.0f}원 | 수량: {trade['amount']:.8f} BTC")
    print(f"   총액: {trade['total_value']:,.2f}원 | 수수료: {trade['fee']:,.2f}원")
    print(f"   잔고: {trade['balance_krw']:,.2f}원 | {trade['balance_btc']:.8f} BTC")
    print(f"   상태: {trade['status']} | 신뢰도: {trade['confidence']:.2f}")
    if trade['reasoning']:
        print(f"   이유: {trade['reasoning'][:100]}...")
    print("-" * 60)

def print_statistics(stats):
    """통계 정보를 보기 좋게 출력"""
    print("📊 거래 통계")
    print(f"   기간: {stats['period_days']}일")
    print(f"   총 거래 수: {stats['total_trades']}회")
    print(f"   거래 유형: {stats['decision_counts']}")
    print(f"   총 거래 금액: {stats['total_value']:,.2f}원")
    print(f"   총 수수료: {stats['total_fee']:,.2f}원")
    print(f"   매수 총액: {stats['buy_total']:,.2f}원")
    print(f"   매도 총액: {stats['sell_total']:,.2f}원")
    print(f"   수익: {stats['profit']:,.2f}원 ({stats['profit_rate']:.2f}%)")
    print("-" * 60)

def main():
    """메인 함수"""
    print("🗄️ 거래 기록 조회 시스템")
    print("=" * 60)
    
    # 데이터베이스 초기화
    if not init_database():
        print("❌ 데이터베이스 연결 실패")
        return
    
    print("✅ 데이터베이스 연결 성공")
    print()
    
    while True:
        print("\n📋 메뉴를 선택하세요:")
        print("1. 최근 거래 기록 조회")
        print("2. 거래 통계 조회")
        print("3. 시장 데이터 히스토리")
        print("4. 종료")
        
        choice = input("\n선택: ").strip()
        
        if choice == "1":
            print("\n📈 최근 거래 기록")
            print("=" * 60)
            trades = get_recent_trades(10)
            if trades:
                for trade in trades:
                    print_trade_record(trade)
            else:
                print("❌ 거래 기록이 없습니다.")
        
        elif choice == "2":
            print("\n📊 거래 통계")
            print("=" * 60)
            days = input("조회 기간 (일, 기본값: 30): ").strip()
            try:
                days = int(days) if days else 30
            except ValueError:
                days = 30
            
            stats = get_trade_statistics(days)
            if stats:
                print_statistics(stats)
            else:
                print("❌ 통계 데이터가 없습니다.")
        
        elif choice == "3":
            print("\n📈 시장 데이터 히스토리")
            print("=" * 60)
            limit = input("조회 개수 (기본값: 10): ").strip()
            try:
                limit = int(limit) if limit else 10
            except ValueError:
                limit = 10
            
            market_data = get_market_data_history(limit)
            if market_data:
                for data in market_data:
                    print(f"📅 {data['timestamp']}")
                    print(f"   가격: {data['current_price']:,.0f}원")
                    print(f"   RSI: {data['rsi']:.2f}")
                    print(f"   MACD: {data['macd']:.4f}")
                    print(f"   공포탐욕지수: {data['fear_greed_value']:.2f}")
                    print(f"   뉴스 감정: {data['news_sentiment']:.2f}")
                    print("-" * 40)
            else:
                print("❌ 시장 데이터가 없습니다.")
        
        elif choice == "4":
            print("👋 프로그램을 종료합니다.")
            break
        
        else:
            print("❌ 잘못된 선택입니다.")

if __name__ == "__main__":
    main()
