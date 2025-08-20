"""
비트코인 AI 자동매매 시스템 메인 실행 파일
"""

import time
import argparse
import pyupbit
from config.settings import (
    validate_api_keys, 
    UPBIT_ACCESS_KEY, 
    UPBIT_SECRET_KEY, 
    ANALYSIS_INTERVAL
)
from database.connection import init_database
from utils.logger import get_logger
from core.services import start_background_services
from core.trading_cycle import execute_trading_cycle
from core.vision_test import run_vision_test



def main():
    """메인 함수"""
    # 명령행 인수 파싱
    parser = argparse.ArgumentParser(description='비트코인 AI 자동매매 시스템')
    parser.add_argument('--mode', choices=['vision', 'indicators', 'test'], 
                       default='vision', help='실행 모드 선택 (기본값: vision)')
    parser.add_argument('--interval', type=int, default=ANALYSIS_INTERVAL,
                       help=f'분석 간격 (초) (기본값: {ANALYSIS_INTERVAL})')
    
    args = parser.parse_args()
    
    print("🚀 비트코인 AI 자동매매 시스템을 시작합니다...")
    print(f"📋 실행 모드: {args.mode}")
    print(f"⏰ 분석 간격: {args.interval}초 ({args.interval/60:.1f}분)")
    
    # API 키 검증
    try:
        validate_api_keys()
        print("✅ API 키 검증 완료")
    except ValueError as e:
        print(f"❌ API 키 오류: {e}")
        print("💡 .env 파일에 필요한 API 키들을 설정해주세요.")
        return
    
    # 로거 설정
    logger = get_logger()
    
    # 백그라운드 서비스 실행 (스케줄러, 대시보드)
    start_background_services(logger)

    # 데이터베이스 초기화
    print("🗄️ 데이터베이스 초기화 중...")
    if init_database():
        print("✅ 데이터베이스 초기화 완료")
    else:
        print("❌ 데이터베이스 초기화 실패")
        print("💡 MySQL 서버가 실행 중인지 확인해주세요.")
        return
    
    # 업비트 연결
    upbit = pyupbit.Upbit(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)
    
   
    print("🔄 자동매매를 시작합니다...")
    print("💡 Ctrl+C를 눌러서 프로그램을 종료할 수 있습니다.")
    print()
    
    while True:
        try:
            use_vision = args.mode == 'vision'
            mode_msg = "Vision API" if use_vision else "기술적 지표"
            print(f"� {mode_msg} 분석 모드로 실행합니다...")
            execute_trading_cycle(upbit, logger, use_vision)
            
            print("\n" + "=" * 60)
            print(f"⏰ {args.interval/60:.1f}분 후 다음 분석을 시작합니다...")
            print("=" * 60 + "\n")
            time.sleep(args.interval)
            
        except KeyboardInterrupt:
            print("\n👋 프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"❌ 예상치 못한 오류 발생: {e}")
            logger.error(f"예상치 못한 오류: {e}")
            print("🔄 1분 후 재시도합니다...")
            time.sleep(60)

if __name__ == "__main__":
    main()
