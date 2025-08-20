#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
비전 분석 디버깅 테스트
"""

import os
import base64
import requests
import json
import time
from datetime import datetime

def test_system_performance():
	"""시스템 성능 확인"""
	print("=" * 60)
	print("🔍 시스템 성능 확인")
	print("=" * 60)
	
	import psutil
	
	# CPU 정보
	cpu_percent = psutil.cpu_percent(interval=1)
	cpu_count = psutil.cpu_count()
	
	# 메모리 정보
	memory = psutil.virtual_memory()
	memory_total = memory.total / (1024**3)  # GB
	memory_available = memory.available / (1024**3)  # GB
	memory_percent = memory.percent
	
	print(f"💻 CPU 사용률: {cpu_percent}%")
	print(f"💻 CPU 코어 수: {cpu_count}")
	print(f"💾 총 메모리: {memory_total:.1f} GB")
	print(f"💾 사용 가능 메모리: {memory_available:.1f} GB")
	print(f"💾 메모리 사용률: {memory_percent}%")
	
	# 디스크 정보
	disk = psutil.disk_usage('/')
	disk_free = disk.free / (1024**3)  # GB
	print(f"💿 사용 가능 디스크: {disk_free:.1f} GB")

def test_image_loading():
	"""이미지 로딩 성능 테스트"""
	print("\n" + "=" * 60)
	print("📸 이미지 로딩 성능 테스트")
	print("=" * 60)
	
	screenshot_path = "images/upbit_screenshot_20250808_194919.png"
	
	if not os.path.exists(screenshot_path):
		print(f"❌ 스크린샷 파일을 찾을 수 없습니다: {screenshot_path}")
		return None
	
	try:
		start_time = time.time()
		
		with open(screenshot_path, "rb") as image_file:
			image_data = image_file.read()
			base64_data = base64.b64encode(image_data).decode('utf-8')
		
		end_time = time.time()
		loading_time = end_time - start_time
		
		print(f"✅ 이미지 로딩 완료")
		print(f"📏 파일 크기: {len(image_data) / (1024*1024):.2f} MB")
		print(f"🔗 Base64 길이: {len(base64_data)} 문자")
		print(f"⏱️ 로딩 시간: {loading_time:.3f}초")
		
		return base64_data
		
	except Exception as e:
		print(f"❌ 이미지 로딩 실패: {e}")
		return None

def test_ollama_connection():
	"""Ollama 연결 테스트"""
	print("\n" + "=" * 60)
	print("🔗 Ollama 연결 테스트")
	print("=" * 60)
	
	try:
		# 간단한 텍스트 요청으로 연결 테스트
		url = "http://localhost:11434/api/generate"
		
		payload = {
			"model": "llama3.1:8b",
			"prompt": "안녕하세요",
			"stream": False,
			"options": {
				"temperature": 0.1,
				"num_predict": 10
			}
		}
		
		print("🤖 Ollama 텍스트 요청 테스트 중...")
		start_time = time.time()
		
		response = requests.post(url, json=payload, timeout=30)
		
		end_time = time.time()
		response_time = end_time - start_time
		
		if response.status_code == 200:
			result = response.json()
			print(f"✅ Ollama 연결 성공")
			print(f"⏱️ 응답 시간: {response_time:.2f}초")
			print(f"📝 응답: {result.get('response', '')}")
		else:
			print(f"❌ Ollama 연결 실패: {response.status_code}")
			
	except requests.exceptions.Timeout:
		print("❌ Ollama 연결 타임아웃 (30초)")
	except Exception as e:
		print(f"❌ Ollama 연결 오류: {e}")

def test_vision_step_by_step():
	"""단계별 비전 분석 테스트"""
	print("\n" + "=" * 60)
	print("🔍 단계별 비전 분석 테스트")
	print("=" * 60)
	
	# 1. 이미지 로딩
	print("1️⃣ 이미지 로딩 중...")
	image_base64 = test_image_loading()
	if not image_base64:
		return
	
	# 2. Ollama 연결 테스트
	print("\n2️⃣ Ollama 연결 테스트 중...")
	test_ollama_connection()
	
	# 3. 간단한 비전 요청
	print("\n3️⃣ 간단한 비전 요청 테스트 중...")
	url = "http://localhost:11434/api/generate"
	
	simple_payload = {
		"model": "llava:7b",
		"prompt": "이 이미지가 무엇인지 한 문장으로 알려주세요.",
		"images": [image_base64],
		"stream": False,
		"options": {
			"temperature": 0.1,
			"num_predict": 20
		}
	}
	
	try:
		print("🤖 간단한 비전 요청 전송 중...")
		start_time = time.time()
		
		response = requests.post(url, json=simple_payload, timeout=60)
		
		end_time = time.time()
		response_time = end_time - start_time
		
		if response.status_code == 200:
			result = response.json()
			analysis = result.get('response', '')
			
			print(f"✅ 간단한 비전 분석 성공")
			print(f"⏱️ 응답 시간: {response_time:.2f}초")
			print(f"📝 분석 결과: {analysis}")
			
			# 성능 평가
			if response_time < 10:
				print("✅ 우수한 성능 (10초 미만)")
			elif response_time < 30:
				print("✅ 양호한 성능 (30초 미만)")
			elif response_time < 60:
				print("⚠️ 느린 성능 (60초 미만)")
			else:
				print("❌ 매우 느린 성능 (60초 이상)")
				
		else:
			print(f"❌ 비전 분석 실패: {response.status_code}")
			print(f"응답: {response.text}")
			
	except requests.exceptions.Timeout:
		print("❌ 비전 분석 타임아웃 (60초)")
	except Exception as e:
		print(f"❌ 비전 분석 오류: {e}")

def test_vision_with_timeout():
	"""타임아웃 설정별 비전 분석 테스트"""
	print("\n" + "=" * 60)
	print("⏱️ 타임아웃 설정별 비전 분석 테스트")
	print("=" * 60)
	
	image_base64 = test_image_loading()
	if not image_base64:
		return
	
	url = "http://localhost:11434/api/generate"
	
	payload = {
		"model": "llava:7b",
		"prompt": "비트코인 차트를 간단히 분석해주세요.",
		"images": [image_base64],
		"stream": False,
		"options": {
			"temperature": 0.3,
			"num_predict": 100
		}
	}
	
	timeouts = [10, 30, 60, 120]
	
	for timeout in timeouts:
		print(f"\n⏱️ {timeout}초 타임아웃으로 테스트 중...")
		
		try:
			start_time = time.time()
			response = requests.post(url, json=payload, timeout=timeout)
			end_time = time.time()
			
			response_time = end_time - start_time
			
			if response.status_code == 200:
				result = response.json()
				analysis = result.get('response', '')
				
				print(f"✅ {timeout}초 타임아웃 성공")
				print(f"⏱️ 실제 응답 시간: {response_time:.2f}초")
				print(f"📝 분석 결과: {analysis[:100]}...")
				break
			else:
				print(f"❌ {timeout}초 타임아웃 실패: {response.status_code}")
				
		except requests.exceptions.Timeout:
			print(f"❌ {timeout}초 타임아웃 발생")
		except Exception as e:
			print(f"❌ {timeout}초 타임아웃 오류: {e}")

def main():
	"""메인 디버깅 함수"""
	print("🚀 비전 분석 디버깅 시작")
	
	# 1. 시스템 성능 확인
	test_system_performance()
	
	# 2. 단계별 비전 분석 테스트
	test_vision_step_by_step()
	
	# 3. 타임아웃 설정별 테스트
	test_vision_with_timeout()
	
	print("\n✅ 비전 분석 디버깅 완료!")
	print("=" * 60)

if __name__ == "__main__":
	main()
