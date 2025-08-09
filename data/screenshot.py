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
    SCREENSHOT_WAIT_TIME, SCREENSHOT_ADDITIONAL_WAIT, SCREENSHOT_MENU_WAIT, SCREENSHOT_CHART_WAIT,
    BROWSER_HEADLESS, BROWSER_DISABLE_IMAGES, BROWSER_DISABLE_JS, BROWSER_DISABLE_CSS,
    BROWSER_PAGE_LOAD_STRATEGY, ADD_BOLLINGER_BANDS, CHART_XPATH, STRICT_CHART_CAPTURE,
    TIMEFRAME_MENU_BUTTON_XPATH, TIMEFRAME_1H_ITEM_XPATH,
    CHART_SETTINGS_BUTTON_XPATH, BOLLINGER_OPTION_XPATH
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
            
            # 이미지 크기 조정 (너무 큰 경우에만)
            max_dimension = 1920
            if original_width > max_dimension or original_height > max_dimension:
                ratio = min(max_dimension / original_width, max_dimension / original_height)
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                print(f"📐 이미지 크기 조정: {new_width}x{new_height}")
            
            # 최적화된 이미지를 메모리에 저장
            output_buffer = io.BytesIO()
            
            # 파일 크기가 목표 크기보다 클 때까지 품질을 낮춤 (더 보수적으로)
            current_quality = quality
            while True:
                output_buffer.seek(0)
                output_buffer.truncate()
                
                img.save(output_buffer, format='JPEG', quality=current_quality, optimize=True)
                
                optimized_size = len(output_buffer.getvalue()) / (1024 * 1024)  # MB
                
                if optimized_size <= max_size_mb or current_quality <= 20:  # 최소 품질을 20으로 설정
                    break
                
                current_quality -= 2  # 더 작은 단위로 품질 감소
            
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
    
    # GPU 없는 환경을 위한 설정
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--enable-unsafe-swiftshader")
    chrome_options.add_argument("--disable-software-rasterizer")
    
    # 안정성 향상 옵션들
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-features=TranslateUI")
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    chrome_options.add_argument("--memory-pressure-off")
    chrome_options.add_argument("--max_old_space_size=4096")
    
    # 설정 파일 기반 최적화 옵션들 (원복)
    if BROWSER_DISABLE_IMAGES:
        chrome_options.add_argument("--disable-images")
    if BROWSER_DISABLE_JS:
        chrome_options.add_argument("--disable-javascript")
    if BROWSER_DISABLE_CSS:
        chrome_options.add_argument("--disable-css")
    
    # 헤드리스 모드 (백그라운드 실행)
    if BROWSER_HEADLESS:
        chrome_options.add_argument("--headless")
    
    # 사용자 에이전트 설정
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # 로그 레벨 최소화
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--silent")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 페이지 로드 전략 설정
    chrome_options.page_load_strategy = BROWSER_PAGE_LOAD_STRATEGY  # DOM이 준비되면 즉시 로드 완료로 간주
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 페이지 로드 타임아웃 설정
        driver.set_page_load_timeout(SCREENSHOT_WAIT_TIME)
        driver.implicitly_wait(10)  # 암시적 대기 시간 증가
        
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
    """업비트 페이지 스크린샷 캡쳐 (차트 영역만)"""
    url = "https://upbit.com/exchange?code=CRIX.UPBIT.KRW-BTC"
    
    print("🚀 업비트 페이지 스크린샷 캡쳐를 시작합니다...")
    
    driver = None
    try:
        # 드라이버 설정
        driver = setup_driver()
        
        # 페이지 로드 (타임아웃 증가)
        print("⏳ 페이지를 로딩 중입니다...")
        driver.get(url)
        
        # 충분한 대기 시간 (원복)
        time.sleep(SCREENSHOT_ADDITIONAL_WAIT)
        
        # 차트 영역 찾기 (원래 XPath 방식)
        print("🔍 차트 영역을 찾는 중입니다...")
        chart_xpath = CHART_XPATH
        chart_element = None
        try:
            chart_element = driver.find_element(By.XPATH, chart_xpath)
            if chart_element.is_displayed():
                print(f"✅ 차트 영역 발견 (XPath): {chart_xpath}")
            else:
                print("⚠️ 차트 영역이 화면에 표시되지 않습니다.")
                chart_element = None
        except Exception as e:
            print(f"⚠️ 차트 영역을 찾을 수 없습니다: {e}")
            chart_element = None
        
        # 1) 시간주기 메뉴 → 1시간 선택 → 2) 차트 설정 버튼 → 볼린저 선택 → 3) 차트 캡쳐
        if ADD_BOLLINGER_BANDS:
            try:
                print("⏱️ 시간 주기 메뉴를 엽니다...")
                tf_menu_btn = driver.find_element(By.XPATH, TIMEFRAME_MENU_BUTTON_XPATH)
                tf_menu_btn.click()
                time.sleep(SCREENSHOT_MENU_WAIT)

                print("🕐 1시간 주기를 선택합니다...")
                tf_1h = driver.find_element(By.XPATH, TIMEFRAME_1H_ITEM_XPATH)
                tf_1h.click()
                time.sleep(SCREENSHOT_CHART_WAIT)

                print("⚙️ 차트 설정(지표) 버튼을 엽니다...")
                indicator_button = driver.find_element(By.XPATH, CHART_SETTINGS_BUTTON_XPATH)
                indicator_button.click()

                time.sleep(SCREENSHOT_MENU_WAIT)

                bollinger_option = driver.find_element(By.XPATH, BOLLINGER_OPTION_XPATH)
                bollinger_option.click()
                print("✅ 볼린저 밴드를 선택했습니다.")

                time.sleep(SCREENSHOT_CHART_WAIT)

            except Exception as e:
                print(f"⚠️ 볼린저 밴드 설정 중 오류: {e}")
        
        if not chart_element:
            if STRICT_CHART_CAPTURE:
                raise Exception("차트 XPath를 찾지 못하여 캡처를 중단합니다. CHART_XPATH를 확인하세요.")
            print("⚠️ 차트 영역을 찾을 수 없어 전체 페이지를 캡처합니다.")
            chart_element = driver.find_element(By.TAG_NAME, "body")
        
        # 현재 시간으로 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"upbit_screenshot_{timestamp}.png"
        filepath = os.path.join("images", filename)
        
        # 차트 영역만 스크린샷 캡쳐
        print("📸 차트 영역만 스크린샷을 캡쳐 중입니다...")
        chart_element.screenshot(filepath)
        
        # Base64 인코딩
        with open(filepath, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        print(f"✅ 차트 스크린샷 완료: {filepath}")
        return filepath, image_base64
        
    except Exception as e:
        print(f"❌ 스크린샷 캡쳐 중 오류: {e}")
        return None
        
    finally:
        if driver:
            driver.quit()
