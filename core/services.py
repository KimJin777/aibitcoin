"""
백그라운드 서비스 관리 모듈
"""

import os
import sys
import socket
import subprocess
from typing import Any, List, Optional, Dict

def start_detached_process(args: List[str], cwd: Optional[str] = None) -> None:
    """백그라운드 프로세스 실행"""
    creationflags = 0
    popen_kwargs: Dict = {}
    
    if os.name == "nt":
        # DETACHED_PROCESS (0x00000008) | CREATE_NEW_PROCESS_GROUP (0x00000200)
        creationflags = 0x00000008 | 0x00000200
        popen_kwargs["creationflags"] = creationflags
    else:
        popen_kwargs["start_new_session"] = True
    
    # 표준 출력/에러 무시하여 메인 콘솔 오염 방지
    subprocess.Popen(
        args,
        cwd=cwd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
        **popen_kwargs,
    )

def is_port_open(port: int, host: str = "127.0.0.1", timeout: float = 0.5) -> bool:
    """포트 열림 여부 확인"""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

def start_background_services(logger: Any) -> None:
    """스케줄러와 대시보드 백그라운드 실행"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    try:
        # 스케줄러 실행
        start_detached_process([sys.executable, "scheduler.py"], cwd=project_root)
        logger.info("스케줄러 백그라운드 실행 요청 완료")
    except Exception as e:
        logger.error(f"스케줄러 실행 실패: {e}")

    try:
        # 대시보드 실행 (포트 8501이 열려있지 않은 경우만)
        if not is_port_open(8501):
            start_detached_process(
                [sys.executable, "-m", "streamlit", "run", "dashboard.py", 
                 "--server.headless", "true", "--server.port", "8501"],
                cwd=project_root
            )
            logger.info("대시보드 백그라운드 실행 요청 완료 (포트 8501)")
        else:
            logger.info("대시보드가 이미 실행 중으로 감지됨 (포트 8501)")
    except Exception as e:
        logger.error(f"대시보드 실행 실패: {e}")
