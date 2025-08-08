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
    BROWSER_PAGE_LOAD_STRATEGY, ADD_BOLLINGER_BANDS
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
    
    # WebGL 관련 경고 해결
    chrome_options.add_argument("--enable-unsafe-swiftshader")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    
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
        
        # 차트 설정 변경 시도 (선택적 - 실패해도 계속 진행)
        print("⏰ 차트 설정을 최적화합니다...")
        try:
            # 차트가 로드될 때까지 짧게 대기
            time.sleep(SCREENSHOT_CHART_WAIT)  # 설정 파일 값 사용
            
            # 차트 영역이 있는지 확인
            chart_elements = driver.find_elements(By.CSS_SELECTOR, "div[class*='chart'], canvas, svg")
            if chart_elements:
                print("✅ 차트 요소를 발견했습니다.")
                
                # 시간 설정 (1시간으로 변경)
                print("⏰ 차트 시간을 1시간으로 설정합니다...")
                try:
                    # 시간 설정 버튼 클릭 (첫 번째 XPath)
                    time_button_xpath = "/html/body/div[1]/div[2]/div[3]/div/section[1]/article[1]/div/span[2]/div/div/div[1]/div[1]/div/cq-menu[1]/span/cq-clickable"
                    time_button = wait.until(EC.element_to_be_clickable((By.XPATH, time_button_xpath)))
                    time_button.click()
                    print("✅ 시간 설정 버튼을 클릭했습니다.")
                    
                    # 메뉴가 나타날 때까지 대기
                    time.sleep(2)
                    
                    # 1시간 옵션 클릭 (정확한 XPath)
                    one_hour_xpath = "/html/body/div[1]/div[2]/div[3]/div/section[1]/article[1]/div/span[2]/div/div/div[1]/div[1]/div/cq-menu[1]/cq-menu-dropdown/cq-item[8]"
                    one_hour_option = wait.until(EC.element_to_be_clickable((By.XPATH, one_hour_xpath)))
                    one_hour_option.click()
                    print("✅ 1시간 옵션을 선택했습니다.")
                    
                    # 설정 변경 후 차트가 업데이트될 때까지 대기
                    time.sleep(3)
                    
                except Exception as e:
                    print(f"⚠️ 차트 시간 설정 변경 중 오류: {e}")
                    print("기본 설정으로 계속 진행합니다...")
                
                # 볼린저 밴드 추가 시도 (설정에서 제어)
                add_bollinger = ADD_BOLLINGER_BANDS
                if add_bollinger:
                    print("📊 볼린저 밴드를 추가합니다...")
                    try:
                        # XPath를 사용한 볼린저 밴드 추가 (screenshot_capture.py에서 가져온 코드)
                        # 지표 설정 버튼 클릭
                        indicator_button_xpath = "/html/body/div[1]/div[2]/div[3]/div/section[1]/article[1]/div/span[2]/div/div/div[1]/div[1]/div/cq-menu[3]/span"
                        indicator_button = wait.until(EC.element_to_be_clickable((By.XPATH, indicator_button_xpath)))
                        indicator_button.click()
                        print("✅ 지표 설정 버튼을 클릭했습니다.")
                        
                        # 메뉴가 나타날 때까지 대기
                        time.sleep(2)
                        
                        # 볼린저 밴드 옵션 클릭
                        bollinger_xpath = "/html/body/div[1]/div[2]/div[3]/div/section[1]/article[1]/div/span[2]/div/div/div[1]/div[1]/div/cq-menu[3]/cq-menu-dropdown/cq-scroll/cq-studies/cq-studies-content/cq-item[2]"
                        bollinger_option = wait.until(EC.element_to_be_clickable((By.XPATH, bollinger_xpath)))
                        bollinger_option.click()
                        print("✅ 볼린저 밴드를 선택했습니다.")
                        
                        # 설정 변경 후 차트가 업데이트될 때까지 대기
                        time.sleep(3)
                        
                    except Exception as e:
                        print(f"⚠️ XPath 볼린저 밴드 추가 중 오류: {e}")
                        print("CSS 선택자 방법으로 재시도합니다...")
                        
                        # CSS 선택자 방법으로 재시도
                        try:
                            # 방법 1: 지표 설정 버튼 찾기
                            indicator_selectors = [
                                "div[class*='indicator']",
                                "button[class*='indicator']",
                                "span[class*='indicator']",
                                "div[class*='chart'] button",
                                "div[class*='toolbar'] button"
                            ]
                            
                            indicator_button = None
                            for selector in indicator_selectors:
                                try:
                                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                    if elements:
                                        indicator_button = elements[0]
                                        print(f"✅ 지표 버튼 발견: {selector}")
                                        break
                                except:
                                    continue
                            
                            if indicator_button:
                                indicator_button.click()
                                time.sleep(1)
                                
                                # 볼린저 밴드 옵션 찾기
                                bollinger_selectors = [
                                    "div[class*='bollinger']",
                                    "div[class*='Bollinger']",
                                    "li[class*='bollinger']",
                                    "option[class*='bollinger']",
                                    "div[class*='indicator'] div[class*='bollinger']"
                                ]
                                
                                bollinger_option = None
                                for selector in bollinger_selectors:
                                    try:
                                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                        if elements:
                                            bollinger_option = elements[0]
                                            print(f"✅ 볼린저 밴드 옵션 발견: {selector}")
                                            break
                                    except:
                                        continue
                                
                                if bollinger_option:
                                    bollinger_option.click()
                                    print("✅ 볼린저 밴드를 선택했습니다.")
                                    time.sleep(2)
                                else:
                                    print("⚠️ 볼린저 밴드 옵션을 찾을 수 없습니다.")
                                    # JavaScript를 사용한 대안 방법
                                    try:
                                        print("🔄 JavaScript를 사용하여 볼린저 밴드를 추가합니다...")
                                        js_code = """
                                        // 볼린저 밴드 관련 요소들을 찾아서 클릭
                                        var indicators = document.querySelectorAll('[class*="indicator"], [class*="study"], [class*="overlay"]');
                                        for (var i = 0; i < indicators.length; i++) {
                                            if (indicators[i].textContent.toLowerCase().includes('bollinger') || 
                                                indicators[i].textContent.toLowerCase().includes('bb')) {
                                                indicators[i].click();
                                                console.log('볼린저 밴드 추가됨');
                                                break;
                                            }
                                        }
                                        """
                                        driver.execute_script(js_code)
                                        time.sleep(1)
                                        print("✅ JavaScript로 볼린저 밴드 추가 시도 완료")
                                    except Exception as js_error:
                                        print(f"⚠️ JavaScript 방법도 실패: {js_error}")
                            else:
                                print("⚠️ 지표 설정 버튼을 찾을 수 없습니다.")
                                
                        except Exception as css_error:
                            print(f"⚠️ CSS 선택자 방법도 실패: {css_error}")
                            print("기본 설정으로 계속 진행합니다...")
                else:
                    print("ℹ️ 볼린저 밴드 추가가 비활성화되어 있습니다.")
            else:
                print("⚠️ 차트 요소를 찾을 수 없습니다. 기본 스크린샷을 진행합니다.")
                
        except Exception as e:
            print(f"⚠️ 차트 설정 확인 중 오류: {e}")
            print("기본 설정으로 계속 진행합니다...")
        
        # 현재 시간으로 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"upbit_screenshot_{timestamp}.png"
        filepath = os.path.join("images", filename)
        
        # 차트 영역만 스크린샷 캡쳐
        print("📸 차트 영역만 스크린샷을 캡쳐 중입니다...")
        
        try:
            # 차트 영역 찾기 (여러 선택자 시도)
            chart_selectors = [
                "div[class*='chart']",
                "canvas[class*='chart']",
                "div[class*='trading']",
                "div[class*='price']",
                "div[class*='chart-container']",
                "div[class*='trading-view']",
                "div[class*='chart-area']",
                "div[class*='chart-wrapper']",
                "div[class*='price-chart']",
                "div[class*='candlestick']",
                "div[class*='chart-pane']"
            ]
            
            chart_element = None
            for selector in chart_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        # 가장 큰 차트 요소 선택
                        chart_element = max(elements, key=lambda x: x.size['width'] * x.size['height'])
                        print(f"✅ 차트 영역 발견: {selector}")
                        break
                except:
                    continue
            
            # CSS 선택자로 찾지 못한 경우 JavaScript로 시도
            if not chart_element:
                print("🔄 JavaScript로 차트 영역을 찾습니다...")
                try:
                    js_code = """
                    // 차트 관련 요소들을 찾아서 가장 큰 것 반환
                    var chartElements = document.querySelectorAll('[class*="chart"], [class*="trading"], [class*="price"], canvas');
                    var largestElement = null;
                    var maxArea = 0;
                    
                    for (var i = 0; i < chartElements.length; i++) {
                        var element = chartElements[i];
                        var rect = element.getBoundingClientRect();
                        var area = rect.width * rect.height;
                        
                        if (area > maxArea && area > 10000) { // 최소 크기 조건
                            maxArea = area;
                            largestElement = element;
                        }
                    }
                    
                    if (largestElement) {
                        var rect = largestElement.getBoundingClientRect();
                        return {
                            x: rect.x,
                            y: rect.y,
                            width: rect.width,
                            height: rect.height,
                            element: largestElement
                        };
                    }
                    return null;
                    """
                    
                    chart_info = driver.execute_script(js_code)
                    if chart_info:
                        print("✅ JavaScript로 차트 영역을 발견했습니다.")
                        # JavaScript로 찾은 정보를 사용하여 차트 영역 설정
                        chart_element = driver.find_element(By.CSS_SELECTOR, "body")  # 임시 요소
                        # 실제로는 JavaScript에서 반환된 정보를 사용
                        chart_location = {'x': chart_info['x'], 'y': chart_info['y']}
                        chart_size = {'width': chart_info['width'], 'height': chart_info['height']}
                        print(f"📐 차트 영역 크기: {chart_size['width']}x{chart_size['height']}")
                        print(f"📍 차트 영역 위치: ({chart_location['x']}, {chart_location['y']})")
                        
                        # 전체 페이지 스크린샷 촬영
                        driver.save_screenshot(filepath)
                        
                        # 차트 영역만 잘라내기
                        from PIL import Image
                        with Image.open(filepath) as img:
                            # 차트 영역 좌표 계산
                            left = chart_location['x']
                            top = chart_location['y']
                            right = chart_location['x'] + chart_size['width']
                            bottom = chart_location['y'] + chart_size['height']
                            
                            # 차트 영역만 크롭
                            chart_image = img.crop((left, top, right, bottom))
                            
                            # 크롭된 이미지 저장
                            chart_image.save(filepath)
                            
                            print(f"✅ 차트 영역만 크롭하여 저장했습니다.")
                            
                            # Base64 인코딩을 위한 바이트 변환
                            img_buffer = io.BytesIO()
                            chart_image.save(img_buffer, format='PNG')
                            img_buffer.seek(0)
                            image_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                            
                            return filepath, image_base64
                        
                except Exception as js_error:
                    print(f"⚠️ JavaScript 방법도 실패: {js_error}")
            
            if chart_element:
                # 차트 영역의 위치와 크기 가져오기
                location = chart_element.location
                size = chart_element.size
                
                print(f"📐 차트 영역 크기: {size['width']}x{size['height']}")
                print(f"📍 차트 영역 위치: ({location['x']}, {location['y']})")
                
                # 전체 페이지 스크린샷 촬영
                driver.save_screenshot(filepath)
                
                # 차트 영역만 잘라내기
                from PIL import Image
                with Image.open(filepath) as img:
                    # 차트 영역 좌표 계산
                    left = location['x']
                    top = location['y']
                    right = location['x'] + size['width']
                    bottom = location['y'] + size['height']
                    
                    # 차트 영역만 크롭
                    chart_image = img.crop((left, top, right, bottom))
                    
                    # 크롭된 이미지 저장
                    chart_image.save(filepath)
                    
                    print(f"✅ 차트 영역만 크롭하여 저장했습니다.")
                    
                    # Base64 인코딩을 위한 바이트 변환
                    img_buffer = io.BytesIO()
                    chart_image.save(img_buffer, format='PNG')
                    img_buffer.seek(0)
                    image_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                    
                    return filepath, image_base64
            
            else:
                print("⚠️ 차트 영역을 찾을 수 없습니다. 전체 페이지를 캡처합니다.")
                # 전체 페이지 스크린샷 캡쳐 (기존 방식)
                driver.save_screenshot(filepath)
                
                # Base64 인코딩
                with open(filepath, "rb") as f:
                    image_base64 = base64.b64encode(f.read()).decode('utf-8')
                
                return filepath, image_base64
                
        except Exception as e:
            print(f"⚠️ 차트 영역 캡처 중 오류: {e}")
            print("전체 페이지를 캡처합니다.")
            # 전체 페이지 스크린샷 캡쳐 (기존 방식)
            driver.save_screenshot(filepath)
            
            # Base64 인코딩
            with open(filepath, "rb") as f:
                image_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            return filepath, image_base64
        
        print(f"✅ 스크린샷이 성공적으로 저장되었습니다!")
        print(f"📁 저장 위치: {filepath}")
        print(f"📏 파일 크기: {os.path.getsize(filepath) / 1024:.1f} KB")
        print(f"🔗 Base64 인코딩 완료")
        
        return filepath, image_base64
        
    except Exception as e:
        print(f"❌ 스크린샷 캡쳐 중 오류 발생: {e}")
        return None
        
    finally:
        if driver:
            driver.quit()
            print("🔒 브라우저를 종료했습니다.")
