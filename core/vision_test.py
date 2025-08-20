"""
비전 분석 테스트 모듈
"""

def run_vision_test():
    """비전 분석 테스트 실행"""
    print("=" * 60)
    print("🔍 비전 분석 테스트 모드")
    print("=" * 60)
    
    try:
        from tests.test_vision_analysis import main as test_main
        test_main()
    except ImportError:
        print("❌ test_vision_analysis.py 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"❌ 비전 분석 테스트 중 오류: {e}")
