# 🚀 비트코인 AI 자동매매 시스템

최신 기술적 지표, 공포탐욕지수, 뉴스 분석, **Vision API**를 통합한 고급 비트코인 자동매매 시스템입니다.

## 📋 주요 기능

### 🔧 기술적 분석
- **이동평균선**: SMA(20, 50), EMA(12, 26)
- **모멘텀 지표**: RSI, MACD, 스토캐스틱, 윌리엄스 %R
- **변동성 지표**: 볼린저 밴드, ATR
- **추세 지표**: ADX, CCI, ROC
- **거래량 지표**: OBV

### 🧠 시장 심리 분석
- **공포탐욕지수**: Alternative.me API 연동
- **뉴스 감정 분석**: Google News API + SerpAPI 연동
- **실시간 시장 심리 모니터링**

### 🤖 AI 기반 매매 결정
- **GPT-4o** 기반 지능형 매매 결정
- **GPT Vision API** 차트 이미지 분석
- **Ollama Vision API** 로컬 차트 분석
- **Structured Outputs** 안정적인 JSON 응답
- **다중 지표 종합 분석**
- **리스크 관리** 및 보수적 접근

### 📸 차트 이미지 분석 (NEW!)
- **실시간 차트 스크린샷 캡처**
- **Ollama Vision API** 로컬 이미지 분석
- **Pillow 라이브러리 이미지 최적화**
- **1시간 차트 + 볼린저 밴드 설정**
- **Base64 인코딩으로 AI 전송**
- **Vision + 시장 데이터 통합 분석**

### 🗄️ 데이터베이스 관리
- **MySQL 8.0 데이터베이스 연동**
- **거래 기록 자동 저장**
- **시장 데이터 히스토리 관리**
- **거래 통계 및 수익률 분석**
- **시스템 로그 저장 및 조회**

### 🤔 자동 반성 및 회고 시스템
- **거래 직후 즉시 반성 생성**
- **일/주/월 주기적 회고 분석**
- **AI 기반 성과 분석 및 개선점 도출**
- **학습 패턴 자동 발견**
- **전략 개선 제안 자동 생성**
- **재귀적 성능 향상 시스템**

### 📊 실시간 모니터링 대시보드
- **Streamlit 기반 웹 대시보드**
- **실시간 거래 기록 모니터링**
- **성과 지표 시각화 (승률, 수익률, 샤프 비율)**
- **반성 시스템 데이터 조회**
- **학습 인사이트 및 전략 개선 제안**

## 🚀 빠른 시작

### 1. 환경 설정

#### 필수 요구사항
- Python 3.8+
- MySQL 8.0+
- Ollama (로컬 AI 모델용)

#### Ollama 설치 및 모델 다운로드
```bash
# Ollama 설치 (Windows)
# https://ollama.ai/download 에서 다운로드

# Vision 모델 설치
ollama pull llava:7b

# 텍스트 모델 설치
ollama pull llama3.1:8b
```

#### Python 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 입력하세요:

```env
# Upbit API
UPBIT_ACCESS_KEY=your_upbit_access_key
UPBIT_SECRET_KEY=your_upbit_secret_key

# Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=gptbitcoin
DB_USER=root
DB_PASSWORD=your_password

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_VISION_MODEL=llava:7b

# News API (선택사항)
GOOGLE_API_KEY=your_google_api_key
SERP_API_KEY=your_serp_api_key
```

### 3. 데이터베이스 초기화

애플리케이션 실행 시 자동 초기화됩니다. 별도 수동 초기화가 필요하면 다음을 실행하세요:
```bash
python -c "from database.connection import init_database; print('init:', init_database())"
```

## 🎯 실행 방법

### 기본 실행 (Vision API 포함)
```bash
python main.py
```

### 실행 모드 선택
```bash
# Vision API 포함 모드 (기본값)
python main.py --mode vision

# 기술적 지표만 사용 모드
python main.py --mode indicators

# 비전 분석 테스트 모드
python main.py --mode test
```

### 분석 간격 조정
```bash
# 10분 간격으로 분석
python main.py --interval 600

# 30분 간격으로 분석
python main.py --interval 1800
```

### 스케줄러 실행
- 메인 실행 시 자동으로 백그라운드에서 스케줄러가 시작됩니다.
- 단독 실행이 필요하면:
```bash
python scheduler.py
```
또는 Windows 배치 스크립트:
```bat
scripts\run_scheduler.bat
```

### 대시보드 실행
```bash
python run_dashboard.py
```
웹 브라우저에서 `http://localhost:8501` 접속

## ✅ 테스트 실행 가이드

테스트 파일은 `tests/` 폴더에 정리되어 있습니다.

### 1) 개별 테스트 스크립트 실행
```bash
python tests/test_json_fix.py
python tests/test_trading_with_reflection.py
python tests/test_reflection_system.py
python tests/test_vision_analysis.py
python tests/test_vision_debug.py
```

### 2) pytest로 일괄 실행 (선택)
```bash
pip install pytest
pytest -q
```

pytest 사용을 원할 경우, 테스트 함수/파일 네이밍을 `test_*.py`/`test_*` 함수로 유지하세요.

## 🧹 산출물 정리 규칙

오래된 스크린샷, 로그, 임시 JSON 산출물을 자동/수동으로 정리하는 것을 권장합니다.

- 이미지(`images/`): 최근 N개만 유지 (예: 50개). 나머지는 삭제.
- 로그(`logs/`): 최근 14일만 유지. 오래된 로그 삭제.
- 분석 산출물(`*.json`): 필요 시 수동 삭제.

예시 파워셸 스니펫(Windows):
```powershell
# images/ 폴더에서 최근 50개만 남기고 삭제
Get-ChildItem images -File | Sort-Object LastWriteTime -Descending | Select-Object -Skip 50 | Remove-Item -Force

# logs/ 폴더에서 14일보다 오래된 파일 삭제
Get-ChildItem logs -File | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-14) } | Remove-Item -Force

# 루트의 개별 분석 JSON(패턴 매칭) 삭제
Get-ChildItem -File *.json | Remove-Item -Force
```

배치 스크립트로 주기 실행을 원하면 `Task Scheduler`에 등록하세요.

## 🔧 시스템 구성

### 1. 데이터 수집 모듈
- **시장 데이터**: 30일 일봉 + 24시간 분봉
- **기술적 지표**: 10개 주요 지표 자동 계산
- **시장 심리**: 공포탐욕지수 실시간 수집
- **뉴스 분석**: Google News API 연동

### 2. AI 분석 엔진
- **Ollama Vision API**: 로컬 차트 이미지 분석
- **Ollama Text API**: 시장 데이터 텍스트 분석
- **다중 지표 종합 평가**
- **시장 심리 + 뉴스 감정 통합 분석**

### 3. 이미지 처리 모듈
- **Selenium** 웹 자동화로 차트 캡처
- **Pillow** 라이브러리 이미지 최적화
- **자동 차트 설정** (1시간 + 볼린저 밴드)
- **Base64 인코딩** AI 전송용

### 4. 매매 실행 모듈
- **자동 매수/매도/보유 결정**
- **최소 거래금액 확인**
- **수수료 고려한 거래량 계산**

## 📈 분석 지표

### 기술적 지표
| 지표 | 설명 | 매매 신호 |
|------|------|-----------|
| RSI | 상대강도지수 | 70↑ 과매수, 30↓ 과매도 |
| MACD | 이동평균수렴확산 | 골든크로스/데드크로스 |
| 볼린저밴드 | 변동성 밴드 | 상단/하단 터치 |
| 스토캐스틱 | 모멘텀 지표 | K/D선 교차 |

### 시장 심리 지표
| 지수 범위 | 분류 | 투자 전략 |
|-----------|------|-----------|
| 0-25 | Extreme Fear | 과매도, 매수 기회 |
| 26-45 | Fear | 신중한 접근 |
| 46-55 | Neutral | 균형잡힌 시장 |
| 56-75 | Greed | 과매수 주의 |
| 76-100 | Extreme Greed | 과매수, 매도 기회 |

### Vision API 분석
| 분석 항목 | 설명 | 매매 영향 |
|-----------|------|-----------|
| 가격 추세 | 상승/하락/횡보 | 매수/매도 신호 |
| 볼린저 밴드 위치 | 상단/중간/하단 | 변동성 분석 |
| 지지선/저항선 | 주요 가격 레벨 | 진입/청산 포인트 |
| 거래량 패턴 | 거래량 변화 | 신호 강도 |
| 차트 패턴 | 기술적 패턴 | 추세 예측 |

## 🔧 Vision API 최적화 기능

### 최적화 프로세스
1. **원본 스크린샷 캡처**: Selenium으로 전체 페이지 캡처
2. **이미지 크기 조정**: 최대 1920px로 리사이즈
3. **JPEG 압축**: 품질 85%로 최적화
4. **파일 크기 제한**: 2MB 이하로 압축
5. **Base64 인코딩**: Ollama API 전송용

### 최적화 효과
- **파일 크기 감소**: 평균 20-30% 압축률
- **전송 속도 향상**: 최적화된 이미지로 빠른 API 호출
- **API 비용 절약**: 로컬 모델 사용으로 비용 없음
- **안정성 향상**: 네트워크 오류 위험 감소

## 🔧 Structured Outputs 기능

### 구조화된 응답 모델
- **TradingDecision**: 매매 결정, 신뢰도, 위험도, 예상 가격 범위
- **KeyIndicators**: RSI, MACD, 볼린저 밴드, 트렌드 강도, 시장 심리, 뉴스 감정
- **ChartAnalysis**: 가격 액션, 지지선/저항선, 차트 패턴, 거래량 분석
- **ExpectedPriceRange**: 예상 최저/최고 가격

### Structured Outputs 장점
- **안정적인 JSON 응답**: Pydantic 모델로 타입 안전성 보장
- **일관된 데이터 구조**: 항상 동일한 필드와 형식
- **오류 처리 강화**: 잘못된 응답 구조 자동 감지
- **개발 효율성**: IDE 자동완성 및 타입 힌트 지원

## ⚠️ 주의사항

### 리스크 관리
- **실제 거래 전 충분한 테스트 필요**
- **소액으로 시작하여 점진적 확대**
- **손절매 전략 필수 설정**

### 시스템 요구사항
- **메모리**: 최소 8GB (Vision API 사용 시 16GB 권장)
- **CPU**: 최소 4코어 (Vision API 사용 시 8코어 권장)
- **디스크**: 최소 10GB 여유 공간
- **네트워크**: 안정적인 인터넷 연결

### API 사용량
- **Ollama API**: 로컬 모델로 비용 없음
- **Upbit API**: 거래소 제한 확인 필요
- **뉴스 API**: Google News API 제한 확인

## 🛠️ 문제 해결

### 일반적인 문제
1. **Ollama 연결 실패**: `ollama serve` 명령으로 서버 시작
2. **Vision 모델 로딩 실패**: `ollama pull llava:7b` 재실행
3. **스크린샷 캡처 실패**: Chrome 드라이버 업데이트
4. **데이터베이스 연결 실패**: MySQL 서버 상태 확인

### 성능 최적화
1. **메모리 부족**: 더 작은 모델 사용 (`llava:7b` → `llava:3b`)
2. **응답 시간 지연**: 타임아웃 설정 조정
3. **이미지 크기 문제**: 압축 품질 조정

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 등록해주세요.

---

**⚠️ 투자 경고**: 이 시스템은 교육 및 연구 목적으로 제작되었습니다. 실제 투자에 사용하기 전에 충분한 테스트와 검증이 필요합니다. 투자는 본인의 책임 하에 진행하시기 바랍니다.
