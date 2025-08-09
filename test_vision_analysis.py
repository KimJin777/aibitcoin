#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
비전 분석 테스트 통합 모듈
마지막 스크린샷 파일을 사용한 다양한 비전 분석 테스트
"""

import os
import base64
import requests
import json
from datetime import datetime

def load_screenshot_as_base64(image_path):
    """스크린샷 파일을 Base64로 인코딩"""
    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
            print(f"✅ 이미지 로드 완료: {image_path}")
            print(f"📏 파일 크기: {len(image_data) / (1024*1024):.2f} MB")
            return base64_data
    except Exception as e:
        print(f"❌ 이미지 로드 실패: {e}")
        return None

def test_simple_vision():
    """간단한 비전 분석 테스트"""
    print("=" * 60)
    print("🔍 간단한 비전 분석 테스트")
    print("=" * 60)
    
    screenshot_path = "images/upbit_screenshot_20250808_194919.png"
    
    if not os.path.exists(screenshot_path):
        print(f"❌ 스크린샷 파일을 찾을 수 없습니다: {screenshot_path}")
        return
    
    image_base64 = load_screenshot_as_base64(screenshot_path)
    if not image_base64:
        return
    
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": "llava:7b",
        "prompt": "이 비트코인 차트를 간단히 분석해주세요. 현재 가격 추세와 매매 신호를 알려주세요.",
        "images": [image_base64],
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 100
        }
    }
    
    print("\n🤖 Ollama Vision API 호출 중...")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            analysis = result.get('response', '')
            
            print("\n" + "=" * 60)
            print("🎉 간단한 비전 분석 결과")
            print("=" * 60)
            print(analysis)
            print("=" * 60)
        else:
            print(f"❌ API 호출 실패: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ 타임아웃 발생 (30초)")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def test_korean_vision():
    """한국어 비전 분석 테스트"""
    print("\n" + "=" * 60)
    print("🔍 한국어 비전 분석 테스트")
    print("=" * 60)
    
    screenshot_path = "images/upbit_screenshot_20250808_194919.png"
    
    if not os.path.exists(screenshot_path):
        print(f"❌ 스크린샷 파일을 찾을 수 없습니다: {screenshot_path}")
        return
    
    image_base64 = load_screenshot_as_base64(screenshot_path)
    if not image_base64:
        return
    
    url = "http://localhost:11434/api/generate"
    
    korean_prompt = """
    이 비트코인 차트를 한국어로 분석해주세요:

    1. 현재 가격 추세 (상승/하락/횡보)
    2. 볼린저 밴드 위치 (상단/중간/하단)
    3. 주요 지지선과 저항선
    4. 거래량 패턴
    5. 매매 신호 (매수/매도/보유)

    간단하고 명확하게 분석 결과를 한국어로 제공해주세요.
    """
    
    payload = {
        "model": "llava:7b",
        "prompt": korean_prompt,
        "images": [image_base64],
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 200
        }
    }
    
    print("\n🤖 한국어 Ollama Vision API 호출 중...")
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            analysis = result.get('response', '')
            
            print("\n" + "=" * 60)
            print("🎉 한국어 비전 분석 결과")
            print("=" * 60)
            print(analysis)
            print("=" * 60)
        else:
            print(f"❌ API 호출 실패: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ 타임아웃 발생 (60초)")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def analyze_chart_with_vision(image_base64):
    """비전 API를 사용한 차트 분석 (JSON 형태)"""
    url = "http://localhost:11434/api/generate"
    
    vision_prompt = """
    비트코인 차트를 분석하여 다음 정보를 JSON 형태로 제공해주세요:
    
    {
        "trend": "상승/하락/횡보",
        "bollinger_position": "상단/중간/하단",
        "support_level": "주요 지지선 위치",
        "resistance_level": "주요 저항선 위치",
        "volume_pattern": "거래량 패턴",
        "trading_signal": "매수/매도/보유",
        "confidence": "높음/중간/낮음",
        "analysis_summary": "간단한 분석 요약"
    }
    
    한국어로 응답해주세요.
    """
    
    payload = {
        "model": "llava:7b",
        "prompt": vision_prompt,
        "images": [image_base64],
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 300
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            analysis = result.get('response', '')
            return analysis
        else:
            print(f"❌ API 호출 실패: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 비전 분석 중 오류: {e}")
        return None

def test_vision_integration():
    """비전 분석 통합 테스트 (시장 데이터와 함께)"""
    print("\n" + "=" * 60)
    print("🔍 비전 분석 통합 테스트")
    print("=" * 60)
    
    screenshot_path = "images/upbit_screenshot_20250808_194919.png"
    
    if not os.path.exists(screenshot_path):
        print(f"❌ 스크린샷 파일을 찾을 수 없습니다: {screenshot_path}")
        return
    
    image_base64 = load_screenshot_as_base64(screenshot_path)
    if not image_base64:
        return
    
    # 가상의 시장 데이터 생성
    market_data = {
        "current_price": 85000000,
        "price_change_24h": 2.5,
        "volume_24h": 1500000000000,
        "fear_greed_index": 65,
        "technical_indicators": {
            "rsi": 58,
            "macd": "bullish",
            "bollinger_position": 0.6
        }
    }
    
    print(f"\n📊 현재 시장 데이터:")
    print(f"   - 현재 가격: {market_data['current_price']:,}원")
    print(f"   - 24시간 변동률: {market_data['price_change_24h']}%")
    print(f"   - 공포탐욕지수: {market_data['fear_greed_index']}")
    print(f"   - RSI: {market_data['technical_indicators']['rsi']}")
    print(f"   - MACD: {market_data['technical_indicators']['macd']}")
    
    # 비전 분석 실행
    print("\n🤖 비전 분석을 시작합니다...")
    start_time = datetime.now()
    
    vision_analysis = analyze_chart_with_vision(image_base64)
    
    end_time = datetime.now()
    analysis_time = (end_time - start_time).total_seconds()
    
    print(f"\n⏱️ 분석 시간: {analysis_time:.2f}초")
    
    if vision_analysis:
        print("\n" + "=" * 60)
        print("🎉 비전 분석 결과")
        print("=" * 60)
        print(vision_analysis)
        print("=" * 60)
        
        # 통합 분석 결과
        print("\n" + "=" * 60)
        print("🔗 통합 분석 결과")
        print("=" * 60)
        print("📈 시장 데이터 + 비전 분석:")
        print(f"   - 시장 데이터: {market_data['price_change_24h']}% 상승, RSI {market_data['technical_indicators']['rsi']}")
        print(f"   - 비전 분석: {vision_analysis}")
        print("   - 종합 판단: 비전 분석과 시장 데이터를 종합하여 매매 결정")
        print("=" * 60)
        
    else:
        print("❌ 비전 분석에 실패했습니다.")

def test_vision_performance():
    """비전 분석 성능 테스트"""
    print("\n" + "=" * 60)
    print("⚡ 비전 분석 성능 테스트")
    print("=" * 60)
    
    screenshot_path = "images/upbit_screenshot_20250808_194919.png"
    
    if not os.path.exists(screenshot_path):
        print(f"❌ 스크린샷 파일을 찾을 수 없습니다: {screenshot_path}")
        return
    
    image_base64 = load_screenshot_as_base64(screenshot_path)
    if not image_base64:
        return
    
    url = "http://localhost:11434/api/generate"
    
    # 간단한 프롬프트로 빠른 테스트
    simple_prompt = "비트코인 차트 분석: 추세와 매매신호만 간단히 알려주세요."
    
    payload = {
        "model": "llava:7b",
        "prompt": simple_prompt,
        "images": [image_base64],
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 50
        }
    }
    
    print("\n🤖 빠른 비전 분석 테스트 중...")
    
    try:
        start_time = datetime.now()
        response = requests.post(url, json=payload, timeout=30)
        end_time = datetime.now()
        
        response_time = (end_time - start_time).total_seconds()
        
        if response.status_code == 200:
            result = response.json()
            analysis = result.get('response', '')
            
            print(f"\n⏱️ 응답 시간: {response_time:.2f}초")
            print("\n" + "=" * 60)
            print("🎉 빠른 비전 분석 결과")
            print("=" * 60)
            print(analysis)
            print("=" * 60)
            
            # 성능 평가
            if response_time < 10:
                print("✅ 우수한 성능 (10초 미만)")
            elif response_time < 30:
                print("✅ 양호한 성능 (30초 미만)")
            else:
                print("⚠️ 느린 성능 (30초 이상)")
                
        else:
            print(f"❌ API 호출 실패: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ 타임아웃 발생 (30초)")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def main():
    """메인 테스트 함수"""
    print("🚀 비전 분석 테스트 시작")
    print("=" * 60)
    
    # 1. 간단한 비전 분석 테스트
    test_simple_vision()
    
    # 2. 한국어 비전 분석 테스트
    test_korean_vision()
    
    # 3. 비전 분석 통합 테스트
    test_vision_integration()
    
    # 4. 성능 테스트
    test_vision_performance()
    
    print("\n✅ 모든 비전 분석 테스트가 완료되었습니다!")
    print("=" * 60)

if __name__ == "__main__":
    main()
