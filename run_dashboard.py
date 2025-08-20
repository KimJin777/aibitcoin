"""
대시보드 실행 스크립트
깔끔하고 직관적인 UI를 제공하는 Streamlit 대시보드를 실행합니다.
"""

import subprocess
import sys
import os
import time
from typing import Optional

class DashboardManager:
    """대시보드 관리 클래스"""
    
    def __init__(self, port: int = 8501):
        self.port = port
        self.process: Optional[subprocess.Popen] = None
    
    def _print_header(self):
        """헤더 출력"""
        print("\n" + "=" * 60)
        print("🚀 GPT Bitcoin 자동매매 대시보드")
        print("=" * 60)
        print(f"📊 접속 주소: http://localhost:{self.port}")
        print("� Ctrl+C를 누르면 대시보드가 종료됩니다")
        print("-" * 60 + "\n")
    
    def _check_dependencies(self) -> bool:
        """의존성 체크"""
        try:
            import streamlit
            return True
        except ImportError:
            print("❌ Streamlit이 설치되어 있지 않습니다.")
            print("💡 다음 명령어로 설치해주세요:")
            print("   pip install streamlit")
            return False
    
    def _run_dashboard(self):
        """대시보드 실행"""
        try:
            # Streamlit 설정으로 깔끔한 UI 제공
            self.process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run",
                "dashboard.py",
                "--server.port", str(self.port),
                "--server.address", "localhost",
                "--server.headless", "true",
                "--theme.base", "light",
                "--theme.primaryColor", "#FF4B4B",
                "--theme.backgroundColor", "#FFFFFF",
                "--theme.secondaryBackgroundColor", "#F0F2F6",
                "--theme.textColor", "#262730",
                "--server.maxUploadSize", "10"
            ])
            
            # 대시보드가 실행되는 동안 대기
            while True:
                if self.process.poll() is not None:
                    break
                time.sleep(1)
                
        except KeyboardInterrupt:
            self._cleanup()
            print("\n� 대시보드를 종료합니다.")
        except Exception as e:
            print(f"\n❌ 대시보드 실행 중 오류 발생: {e}")
            self._cleanup()
    
    def _cleanup(self):
        """프로세스 정리"""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
    
    def start(self):
        """대시보드 시작"""
        if not self._check_dependencies():
            return
        
        self._print_header()
        self._run_dashboard()

def main():
    """메인 함수"""
    dashboard = DashboardManager()
    dashboard.start()

if __name__ == "__main__":
    main()
