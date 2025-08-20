"""
JSON 정리 함수 테스트
"""

import numpy as np
from utils.json_cleaner import clean_json_data
import json

def test_json_cleaner():
	"""JSON 정리 함수 테스트"""
	print("🧪 JSON 정리 함수 테스트 시작")
	print("=" * 50)
	
	# 테스트 데이터 생성 (NaN, Infinity 포함)
	test_data = {
		'price': 100.0,
		'rsi': np.nan,
		'macd': np.inf,
		'normal_value': 50.0,
		'nested': {
			'sma': np.nan,
			'ema': 25.5,
			'volume': np.inf
		},
		'list_data': [1.0, np.nan, 3.0, np.inf, 5.0],
		'string_value': 'test',
		'none_value': None
	}
	
	print("📊 원본 데이터:")
	print(test_data)
	print()
	
	# JSON 직렬화 시도 (오류 발생 예상)
	try:
		json_str = json.dumps(test_data, ensure_ascii=False)
		print("❌ 원본 데이터 JSON 직렬화 성공 (예상과 다름)")
	except Exception as e:
		print(f"✅ 원본 데이터 JSON 직렬화 실패 (예상됨): {e}")
	
	print()
	
	# 정리된 데이터 생성
	cleaned_data = clean_json_data(test_data)
	
	print("🧹 정리된 데이터:")
	print(cleaned_data)
	print()
	
	# 정리된 데이터 JSON 직렬화 시도
	try:
		json_str = json.dumps(cleaned_data, ensure_ascii=False)
		print("✅ 정리된 데이터 JSON 직렬화 성공!")
		print(f"📝 JSON 문자열 길이: {len(json_str)}")
	except Exception as e:
		print(f"❌ 정리된 데이터 JSON 직렬화 실패: {e}")
	
	print()
	print("🎉 JSON 정리 함수 테스트 완료!")

if __name__ == "__main__":
	test_json_cleaner()
