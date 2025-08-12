"""
입금 내역 테스트 실행 스크립트
"""

import subprocess
import sys
import os

def run_deposit_test():
    """입금 내역 테스트 실행"""
    print("🔍 업비트 입금 내역 테스트 시작...")
    print("=" * 50)
    
    try:
        # Python 스크립트 직접 실행
        subprocess.run([sys.executable, "deposit_test.py"])
    except Exception as e:
        print(f"❌ 테스트 실행 오류: {e}")

if __name__ == "__main__":
    run_deposit_test()
