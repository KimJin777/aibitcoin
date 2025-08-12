"""
업비트 입금 내역 조회 테스트 (프롬프트 버전)
"""

import pyupbit
from config.settings import UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY

def get_deposit_history():
    """업비트 API를 통해 입금 내역을 조회하는 함수"""
    try:
        if not UPBIT_ACCESS_KEY or not UPBIT_SECRET_KEY:
            print("⚠️ 업비트 API 키가 설정되지 않았습니다.")
            return None
        
        upbit = pyupbit.Upbit(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)
        
        print("🔍 업비트 API에서 KRW 입금 내역 조회 시도...")
        
        # KRW 입금 내역 조회
        krw_deposits = upbit.get_deposit_list("KRW")
        
        if krw_deposits:
            print(f"✅ KRW 입금 내역 조회 성공: {len(krw_deposits)}건")
            
            # 모든 입금 내역 상태 먼저 확인
            print("\n📋 모든 입금 내역 상태:")
            print("-" * 80)
            for i, deposit in enumerate(krw_deposits, 1):
                try:
                    amount = float(deposit.get('amount', 0))
                    state = deposit.get('state', 'N/A')
                    created_at = deposit.get('created_at', 'N/A')
                    txid = deposit.get('txid', 'N/A')
                    print(f"{i:2d}. {amount:>10,.0f}원 | {created_at} | {state} | {txid}")
                except (ValueError, TypeError):
                    amount_raw = deposit.get('amount', 'N/A')
                    state = deposit.get('state', 'N/A')
                    created_at = deposit.get('created_at', 'N/A')
                    txid = deposit.get('txid', 'N/A')
                    print(f"{i:2d}. {str(amount_raw):>10} | {created_at} | {state} | {txid}")
            
            # 입금 내역 정리
            deposit_records = []
            total_deposits = 0
            
            for deposit in krw_deposits:
                if isinstance(deposit, dict):
                    amount = float(deposit.get('amount', 0))
                    created_at = deposit.get('created_at', '')
                    state = deposit.get('state', '')
                    txid = deposit.get('txid', '')
                    
                    # 완료된 입금만 계산 (ACCEPTED도 완료로 인식)
                    if (state == 'done' or state == 'ACCEPTED') and amount > 0:
                        deposit_records.append({
                            'amount': amount,
                            'created_at': created_at,
                            'state': state,
                            'txid': txid
                        })
                        total_deposits += amount
            
            if deposit_records:
                print(f"\n💰 총 입금액: {total_deposits:,.0f}원")
                print(f"📊 완료된 입금: {len(deposit_records)}건")
                
                # 입금 내역 정렬 (최신순)
                deposit_records.sort(key=lambda x: x['created_at'], reverse=True)
                
                # 상세 입금 내역을 텍스트 리스트로 표시
                print("\n📋 완료된 입금 내역:")
                print("-" * 80)
                for i, deposit in enumerate(deposit_records, 1):
                    print(f"{i:2d}. {deposit['amount']:>10,.0f}원 | {deposit['created_at']} | {deposit['state']} | {deposit['txid']}")
                
                return {
                    'total_deposits': total_deposits,
                    'deposit_count': len(deposit_records),
                    'deposits': deposit_records
                }
            else:
                print(f"\n📊 완료된 KRW 입금 내역이 없습니다.")
                print("📊 모든 입금의 상태가 'done'이 아닙니다.")
                
                # 상태별 통계
                state_counts = {}
                for deposit in krw_deposits:
                    state = deposit.get('state', 'N/A')
                    state_counts[state] = state_counts.get(state, 0) + 1
                
                print("\n📊 상태별 통계:")
                for state, count in state_counts.items():
                    print(f"  {state}: {count}건")
                
                return None
        else:
            print("❌ KRW 입금 내역을 가져올 수 없습니다.")
            return None
            
    except Exception as e:
        print(f"❌ 입금 내역 조회 실패: {e}")
        import traceback
        print(f"📊 상세 오류: {traceback.format_exc()}")
        return None

def main():
    print("💰 업비트 입금 내역 조회 테스트")
    print("=" * 50)
    
    # 입금 내역 조회
    deposit_info = get_deposit_history()
    
    if deposit_info:
        print("\n" + "=" * 50)
        print("📊 요약 정보:")
        print(f"총 입금액: {deposit_info['total_deposits']:,.0f}원")
        print(f"입금 횟수: {deposit_info['deposit_count']}회")
        
        if deposit_info['deposit_count'] > 0:
            avg_deposit = deposit_info['total_deposits'] / deposit_info['deposit_count']
            print(f"평균 입금액: {avg_deposit:,.0f}원")
        
        # 디버깅 정보
        print("\n🔍 디버깅 정보:")
        if deposit_info['deposits']:
            print("API 응답 구조 (첫 번째 항목):")
            sample = deposit_info['deposits'][0]
            for key, value in sample.items():
                print(f"  {key}: {value}")
    
    else:
        print("\n⚠️ 입금 내역을 가져올 수 없습니다.")
        
        # API 키 확인
        print("\n🔑 API 키 상태:")
        if UPBIT_ACCESS_KEY and UPBIT_SECRET_KEY:
            print("✅ API 키가 설정되어 있습니다.")
            print(f"Access Key: {UPBIT_ACCESS_KEY[:10]}...")
            print(f"Secret Key: {UPBIT_SECRET_KEY[:10]}...")
        else:
            print("❌ API 키가 설정되지 않았습니다.")
            print("config/settings.py 파일에서 UPBIT_ACCESS_KEY와 UPBIT_SECRET_KEY를 확인하세요.")

if __name__ == "__main__":
    main()
