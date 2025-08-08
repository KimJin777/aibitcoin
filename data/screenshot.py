"""
스크린샷 캡처 모듈
업비트 차트 페이지의 스크린샷을 캡처하고 최적화합니다.
"""

import os
import time
import base64
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import io
from typing import Optional, Tuple
from config.settings import (
    SCREENSHOT_WINDOW_SIZE, SCREENSHOT_MAX_SIZE_MB, SCREENSHOT_QUALITY,
    SCREENSHOT_WAIT_TIME, SCREENSHOT_ADDITIONAL_WAIT, SCREENSHOT_CHART_WAIT,
    BROWSER_HEADLESS, BROWSER_DISABLE_IMAGES, BROWSER_DISABLE_JS, BROWSER_DISABLE_CSS,
    BROWSER_PAGE_LOAD_STRATEGY
)

def optimize_image(image_path: str, max_size_mb: float = SCREENSHOT_MAX_SIZE_MB, quality: int = SCREENSHOT_QUALITY) -> Tuple[bytes, dict]:
    """이미지를 최적화하여 파일 크기를 줄이고 품질을 유지"""
    try:
        with Image.open(image_path) as img:
            original_size = os.path.getsize(image_path) / (1024 * 1024)  # MB
            original_width, original_height = img.size
            
            print(f"📏 원본 이미지 크기: {original_size:.2f} MB ({original_width}x{original_height})")
            
            # RGB 모드로 변환 (JPEG 최적화를 위해)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 이미지 크기 조정 (너무 큰 경우)
            max_dimension = 1920
            if original_width > max_dimension or original_height > max_dimension:
                ratio = min(max_dimension / original_width, max_dimension / original_height)
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                print(f"📐 이미지 크기 조정: {new_width}x{new_height}")
            
            # 최적화된 이미지를 메모리에 저장
            output_buffer = io.BytesIO()
            
            # 파일 크기가 목표 크기보다 클 때까지 품질을 낮춤
            current_quality = quality
            while True:
                output_buffer.seek(0)
                output_buffer.truncate()
                
                img.save(output_buffer, format='JPEG', quality=current_quality, optimize=True)
                
                optimized_size = len(output_buffer.getvalue()) / (1024 * 1024)  # MB
                
                if optimized_size <= max_size_mb or current_quality <= 10:
                    break
                
                current_quality -= 5
            
            optimized_bytes = output_buffer.getvalue()
            optimized_size = len(optimized_bytes) / (1024 * 1024)  # MB
            
            optimization_info = {
                'original_size_mb': original_size,
                'optimized_size_mb': optimized_size,
                'compression_ratio': (1 - optimized_size / original_size) * 100,
                'final_quality': current_quality,
                'width': img.size[0],
                'height': img.size[1]
            }
            
            print(f"✅ 이미지 최적화 완료:")
            print(f"   📏 원본 크기: {original_size:.2f} MB")
            print(f"   📏 최적화 크기: {optimized_size:.2f} MB")
            print(f"   📊 압축률: {optimization_info['compression_ratio']:.1f}%")
            print(f"   🎨 최종 품질: {current_quality}")
            
            return optimized_bytes, optimization_info
            
    except Exception as e:
        print(f"⚠️ 이미지 최적화 중 오류: {e}")
        # 오류 발생 시 원본 파일을 그대로 사용
        with open(image_path, "rb") as f:
            return f.read(), {'error': str(e)}

def setup_driver() -> webdriver.Chrome:
    """Chrome 드라이버 설정 (최적화된 버전)"""
    chrome_options = Options()
    
    # 창 크기 설정
    chrome_options.add_argument(f"--window-size={SCREENSHOT_WINDOW_SIZE[0]},{SCREENSHOT_WINDOW_SIZE[1]}")
    
    # 성능 최적화 옵션들
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    
    # 설정 파일 기반 최적화 옵션들
    if BROWSER_DISABLE_IMAGES:
        chrome_options.add_argument("--disable-images")  # 이미지 로딩 비활성화로 속도 향상
    if BROWSER_DISABLE_JS:
        chrome_options.add_argument("--disable-javascript")  # JavaScript 비활성화 (차트는 이미 로드됨)
    if BROWSER_DISABLE_CSS:
        chrome_options.add_argument("--disable-css")  # CSS 비활성화
    
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-features=TranslateUI")
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    chrome_options.add_argument("--memory-pressure-off")
    chrome_options.add_argument("--max_old_space_size=4096")
    
    # 헤드리스 모드 (백그라운드 실행)
    if BROWSER_HEADLESS:
        chrome_options.add_argument("--headless")
    
    # 사용자 에이전트 설정
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # 로그 레벨 최소화
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # 페이지 로드 전략 설정
    chrome_options.page_load_strategy = BROWSER_PAGE_LOAD_STRATEGY  # DOM이 준비되면 즉시 로드 완료로 간주
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 페이지 로드 타임아웃 설정
        driver.set_page_load_timeout(SCREENSHOT_WAIT_TIME)
        driver.implicitly_wait(5)
        
        return driver
        
    except Exception as e:
        print(f"❌ Chrome 드라이버 설정 중 오류: {e}")
        raise e

def create_images_directory():
    """images 디렉토리 생성"""
    if not os.path.exists("images"):
        os.makedirs("images")
        print("📁 images 디렉토리를 생성했습니다.")

def capture_upbit_screenshot() -> Optional[Tuple[str, str]]:
    """업비트 페이지 스크린샷 캡쳐 (최적화된 버전)"""
    url = "https://upbit.com/exchange?code=CRIX.UPBIT.KRW-BTC"
    
    print("🚀 업비트 페이지 스크린샷 캡쳐를 시작합니다...")
    print(f"📄 대상 URL: {url}")
    
    driver = None
    try:
        # 드라이버 설정
        driver = setup_driver()
        
        # 페이지 로드
        print("⏳ 페이지를 로딩 중입니다...")
        driver.get(url)
        
        # 페이지가 완전히 로드될 때까지 대기 (시간 단축)
        wait = WebDriverWait(driver, SCREENSHOT_WAIT_TIME)  # 설정 파일 값 사용
        
        # 메인 콘텐츠가 로드될 때까지 대기
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            print("✅ 페이지 로딩이 완료되었습니다.")
        except Exception as e:
            print(f"⚠️ 페이지 로딩 대기 중 오류: {e}")
            print("계속 진행합니다...")
        
        # 최소한의 대기 시간 (동적 콘텐츠 로딩을 위해)
        time.sleep(SCREENSHOT_ADDITIONAL_WAIT)  # 설정 파일 값 사용
        
        # 차트 설정 변경 시도 (실패해도 계속 진행)
        print("⏰ 차트 설정을 최적화합니다...")
        try:
            # 차트가 로드될 때까지 짧게 대기
            time.sleep(SCREENSHOT_CHART_WAIT)  # 설정 파일 값 사용
            
            # 차트 영역이 있는지 확인
            chart_elements = driver.find_elements(By.CSS_SELECTOR, "div[class*='chart'], canvas, svg")
            if chart_elements:
                print("✅ 차트 요소를 발견했습니다.")
            else:
                print("⚠️ 차트 요소를 찾을 수 없습니다. 기본 스크린샷을 진행합니다.")
                
        except Exception as e:
            print(f"⚠️ 차트 설정 확인 중 오류: {e}")
            print("기본 설정으로 계속 진행합니다...")
        
        # 현재 시간으로 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"upbit_screenshot_{timestamp}.png"
        filepath = os.path.join("images", filename)
        
        # 전체 페이지 스크린샷 캡쳐
        print("📸 전체 페이지 스크린샷을 캡쳐 중입니다...")
        
        # 페이지 전체 높이 계산 (최적화)
        try:
            total_height = driver.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);")
            driver.set_window_size(1920, min(total_height, 3000))  # 최대 높이 제한
        except:
            driver.set_window_size(1920, 1080)  # 기본 크기
        
        # 스크린샷 촬영
        driver.save_screenshot(filepath)
        
        # 이미지 최적화 (더 강한 압축)
        print("🔧 이미지를 최적화합니다...")
        optimized_bytes, optimization_info = optimize_image(filepath, SCREENSHOT_MAX_SIZE_MB * 0.3, SCREENSHOT_QUALITY - 15)  # 더 작은 크기, 더 낮은 품질
        
        # 최적화된 이미지를 Base64 인코딩
        image_base64 = base64.b64encode(optimized_bytes).decode('utf-8')
        
        print(f"✅ 스크린샷이 성공적으로 저장되었습니다!")
        print(f"📁 저장 위치: {filepath}")
        print(f"📏 원본 파일 크기: {os.path.getsize(filepath) / 1024:.1f} KB")
        print(f"🔗 최적화된 Base64 인코딩 완료")
        
        return filepath, image_base64
        
    except Exception as e:
        print(f"❌ 스크린샷 캡쳐 중 오류 발생: {e}")
        return None
        
    finally:
        if driver:
            driver.quit()
            print("🔒 브라우저를 종료했습니다.")
