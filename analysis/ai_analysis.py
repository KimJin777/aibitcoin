"""
AI 분석 모듈
"""

import json
import base64
import requests
from datetime import datetime
from typing import Optional, Dict, Any, List
from .models import TradingDecision
from config.settings import (
    OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_VISION_MODEL, VISION_API_TIMEOUT, VISION_API_MAX_TOKENS, 
    VISION_API_TEMPERATURE, STRATEGY_IMPROVEMENT_ENABLED
)

def call_ollama_api(prompt: str, model: str = None, temperature: float = 0.7, max_tokens: int = 1000) -> str:
    """Ollama API 호출"""
    if model is None:
        model = OLLAMA_MODEL
    
    url = f"{OLLAMA_BASE_URL}/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=VISION_API_TIMEOUT)
        response.raise_for_status()
        
        result = response.json()
        return result.get('response', '')
        
    except Exception as e:
        print(f"❌ Ollama API 호출 중 오류: {e}")
        return ""

def call_ollama_vision_api(prompt: str, image_base64: str, model: str = None, temperature: float = 0.7, max_tokens: int = 1000) -> str:
    """Ollama Vision API 호출 (이미지 분석)"""
    if model is None:
        model = OLLAMA_VISION_MODEL
    
    url = f"{OLLAMA_BASE_URL}/api/generate"
    
    # 이미지 데이터 준비 (base64 디코딩)
    import base64
    try:
        image_bytes = base64.b64decode(image_base64)
        image_data = base64.b64encode(image_bytes).decode('utf-8')
    except Exception as e:
        print(f"⚠️ 이미지 데이터 처리 중 오류: {e}")
        return ""
    
    payload = {
        "model": model,
        "prompt": prompt,
        "images": [image_data],
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=VISION_API_TIMEOUT)
        response.raise_for_status()
        
        result = response.json()
        return result.get('response', '')
        
    except Exception as e:
        print(f"❌ Ollama Vision API 호출 중 오류: {e}")
        return ""

def create_market_analysis_data(daily_df, minute_df, current_price, orderbook, fear_greed_data, analyzed_news):
    """AI 분석용 시장 데이터 생성"""
    # 최근 기술적 지표 요약
    technical_summary = {}
    
    if not daily_df.empty:
        # 일봉 데이터의 최근 기술적 지표
        latest_daily = daily_df.iloc[-1] if len(daily_df) > 0 else None
        if latest_daily is not None:
            technical_summary['daily_indicators'] = {
                'sma_20': float(latest_daily.get('SMA_20', 0)),
                'sma_50': float(latest_daily.get('SMA_50', 0)),
                'ema_12': float(latest_daily.get('EMA_12', 0)),
                'ema_26': float(latest_daily.get('EMA_26', 0)),
                'rsi': float(latest_daily.get('RSI', 50)),
                'macd': float(latest_daily.get('MACD', 0)),
                'macd_signal': float(latest_daily.get('MACD_Signal', 0)),
                'bb_upper': float(latest_daily.get('BB_Upper', 0)),
                'bb_lower': float(latest_daily.get('BB_Lower', 0)),
                'bb_position': float(latest_daily.get('BB_Position', 0.5)),
                'stoch_k': float(latest_daily.get('Stoch_K', 50)),
                'stoch_d': float(latest_daily.get('Stoch_D', 50)),
                'williams_r': float(latest_daily.get('Williams_R', -50)),
                'atr': float(latest_daily.get('ATR', 0)),
                'adx': float(latest_daily.get('ADX', 25)),
                'cci': float(latest_daily.get('CCI', 0)),
                'roc': float(latest_daily.get('ROC', 0))
            }
    
    if not minute_df.empty:
        # 분봉 데이터의 최근 기술적 지표
        latest_minute = minute_df.iloc[-1] if len(minute_df) > 0 else None
        if latest_minute is not None:
            technical_summary['minute_indicators'] = {
                'sma_20': float(latest_minute.get('SMA_20', 0)),
                'rsi': float(latest_minute.get('RSI', 50)),
                'macd': float(latest_minute.get('MACD', 0)),
                'bb_position': float(latest_minute.get('BB_Position', 0.5)),
                'stoch_k': float(latest_minute.get('Stoch_K', 50)),
                'williams_r': float(latest_minute.get('Williams_R', -50))
            }
    
    # 뉴스 감정 분석 요약
    news_summary = None
    if analyzed_news:
        sentiment_scores = [news['sentiment_score'] for news in analyzed_news]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        positive_news = [news for news in analyzed_news if news['sentiment'] == '긍정']
        negative_news = [news for news in analyzed_news if news['sentiment'] == '부정']
        
        news_summary = {
            'total_news': len(analyzed_news),
            'average_sentiment': avg_sentiment,
            'positive_count': len(positive_news),
            'negative_count': len(negative_news),
            'neutral_count': len(analyzed_news) - len(positive_news) - len(negative_news),
            'recent_news': analyzed_news[:5]  # 최근 5개 뉴스만
        }
    
    analysis_data = {
        "current_price": current_price,
        "daily_data": daily_df.to_dict('records') if not daily_df.empty else [],
        "minute_data": minute_df.tail(100).to_dict('records') if not minute_df.empty else [],
        "technical_indicators": technical_summary,
        "fear_greed_index": fear_greed_data,
        "news_analysis": news_summary,
        "orderbook": orderbook if orderbook and isinstance(orderbook, dict) else None,
        "analysis_time": datetime.now().isoformat()
    }
    
    return analysis_data

def analyze_market_sentiment(market_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    시장 심리 분석
    
    Args:
        market_data: 시장 데이터
        
    Returns:
        분석 결과
    """
    try:
        # 시장 데이터 요약
        current_price = market_data.get('current_price', 0)
        fear_greed = market_data.get('fear_greed_index', {})
        technical_indicators = market_data.get('technical_indicators', {})
        
        # 분석 요청 메시지
        analysis_prompt = f"""
        비트코인 시장 데이터를 분석하여 시장 심리를 평가해주세요.
        
        현재 가격: {current_price}
        공포탐욕지수: {fear_greed}
        기술적 지표: {technical_indicators}
        
        다음 형식으로 분석해주세요:
        - 시장 심리: (extreme_fear, fear, neutral, greed, extreme_greed)
        - 분석 근거: (상세한 분석 내용)
        - 신뢰도: (0.0-1.0)
        """
        
        # Ollama API 호출
        analysis_text = call_ollama_api(
            prompt=analysis_prompt,
            temperature=0.7,
            max_tokens=500
        )
        
        if not analysis_text:
            # API 호출 실패 시 기본 분석
            fear_greed_value = fear_greed.get('value', 50) if isinstance(fear_greed, dict) else 50
            if fear_greed_value > 70:
                analysis_text = f"Fear & Greed Index가 {fear_greed_value}로 높음. 과매수 상태일 수 있으므로 보수적 접근 권장."
            elif fear_greed_value < 30:
                analysis_text = f"Fear & Greed Index가 {fear_greed_value}로 낮음. 과매도 상태일 수 있으므로 매수 기회 고려."
            else:
                analysis_text = f"Fear & Greed Index가 {fear_greed_value}로 중립. 현재 가격 {current_price:,}원 기준으로 관망."
        
        return {
            'sentiment': 'neutral',  # 기본값
            'analysis': analysis_text,
            'confidence': 0.7,
            'timestamp': '2024-01-01T00:00:00'
        }
        
    except Exception as e:
        return {
            'sentiment': 'neutral',
            'analysis': f'분석 중 오류 발생: {str(e)}',
            'confidence': 0.0,
            'timestamp': '2024-01-01T00:00:00'
        }

def analyze_trading_performance(trades_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    거래 성과 분석
    
    Args:
        trades_data: 거래 데이터 리스트
        
    Returns:
        분석 결과
    """
    try:
        if not trades_data:
            return {
                'analysis': '분석할 거래 데이터가 없습니다.',
                'recommendations': [],
                'confidence': 0.0
            }
        
        # 기본 통계 계산
        total_trades = len(trades_data)
        winning_trades = len([t for t in trades_data if t.get('profit_loss', 0) > 0])
        losing_trades = len([t for t in trades_data if t.get('profit_loss', 0) < 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        analysis_text = f"""
        거래 성과 분석:
        - 총 거래 수: {total_trades}
        - 승리 거래: {winning_trades}
        - 패배 거래: {losing_trades}
        - 승률: {win_rate:.2%}
        """
        
        recommendations = []
        if win_rate < 0.5:
            recommendations.append("승률이 낮습니다. 매매 전략을 재검토하세요.")
        if total_trades < 10:
            recommendations.append("더 많은 거래 데이터가 필요합니다.")
        
        return {
            'analysis': analysis_text,
            'recommendations': recommendations,
            'confidence': 0.8,
            'statistics': {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate
            }
        }
        
    except Exception as e:
        return {
            'analysis': f'분석 중 오류 발생: {str(e)}',
            'recommendations': [],
            'confidence': 0.0
        }

def generate_improvement_suggestions(performance_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    개선 제안 생성
    
    Args:
        performance_analysis: 성과 분석 결과
        
    Returns:
        개선 제안 리스트
    """
    suggestions = []
    
    try:
        stats = performance_analysis.get('statistics', {})
        win_rate = stats.get('win_rate', 0)
        
        if win_rate < 0.4:
            suggestions.append({
                'type': 'risk_management',
                'title': '리스크 관리 강화',
                'description': '승률이 낮으므로 리스크 관리 전략을 강화하세요.',
                'priority': 'high'
            })
        
        if win_rate < 0.5:
            suggestions.append({
                'type': 'strategy',
                'title': '매매 전략 재검토',
                'description': '현재 전략의 효과성을 재검토하고 개선하세요.',
                'priority': 'medium'
            })
        
        suggestions.append({
            'type': 'monitoring',
            'title': '지속적 모니터링',
            'description': '시장 상황과 거래 성과를 지속적으로 모니터링하세요.',
            'priority': 'low'
        })
        
    except Exception as e:
        suggestions.append({
            'type': 'error',
            'title': '분석 오류',
            'description': f'분석 중 오류가 발생했습니다: {str(e)}',
            'priority': 'critical'
        })
    
    return suggestions

def get_active_strategy_improvements() -> List[Dict[str, Any]]:
    """활성화된 전략 개선 제안 조회"""
    try:
        from database.connection import get_db_connection
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT * FROM strategy_improvements 
        WHERE status IN ('implemented', 'validated')
        ORDER BY success_metric DESC, created_at DESC
        LIMIT 10
        """
        
        cursor.execute(query)
        improvements = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return improvements
        
    except Exception as e:
        print(f"❌ 전략 개선 조회 오류: {e}")
        return []

def apply_strategy_improvements(decision: Dict[str, Any], improvements: List[Dict[str, Any]]) -> Dict[str, Any]:
    """전략 개선을 매매 결정에 적용"""
    if not improvements:
        return decision
    
    print("🔧 전략 개선 적용 중...")
    
    # 개선 타입별 적용
    for improvement in improvements:
        improvement_type = improvement.get('improvement_type', '')
        new_value = improvement.get('new_value', '')
        success_metric = improvement.get('success_metric', 0.5)
        
        print(f"  - {improvement_type}: {new_value[:50]}... (성공지표: {success_metric:.2f})")
        
        # 개선 타입별 적용 로직
        if improvement_type == 'condition':
            # 진입 조건 강화
            if decision.get('confidence', 0) < 0.7:
                decision['confidence'] = min(0.9, decision.get('confidence', 0) + 0.1)
                decision['reason'] += f" [전략개선: 진입조건 강화 적용]"
                
        elif improvement_type == 'parameter':
            # 파라미터 최적화
            if decision.get('risk_level') == 'high':
                decision['risk_level'] = 'medium'
                decision['reason'] += f" [전략개선: 리스크 파라미터 조정]"
                
        elif improvement_type == 'risk':
            # 리스크 관리 강화
            if decision.get('decision') == 'buy':
                # 매수 시 더 보수적인 접근
                decision['confidence'] = max(0.6, decision.get('confidence', 0) - 0.1)
                decision['reason'] += f" [전략개선: 리스크 관리 강화]"
                
        elif improvement_type == 'timing':
            # 타이밍 개선
            if decision.get('decision') == 'hold':
                # 보유 결정 시 더 적극적인 모니터링
                decision['reason'] += f" [전략개선: 타이밍 최적화 적용]"
    
    return decision

def ai_trading_decision_with_indicators(market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """기술적 지표를 포함한 AI 매매 결정 함수"""
    print("=== AI 매매 결정 분석 중 (기술적 지표 포함) ===")
    
    # 간소화된 시스템 메시지
    system_message = """
    You are a Bitcoin trading expert. Analyze the market data and provide a trading decision.
    Focus on: RSI, MACD, Bollinger Bands, Fear & Greed Index, news sentiment.
    Decision: buy/sell/hold with brief reasoning.
    """
    
    try:
        # Ollama API 호출 (타임아웃 시 기본 분석 사용)
        prompt = f"{system_message}\n\nAnalyze Bitcoin market data: {json.dumps(market_data, default=str)}"
        
        analysis_text = call_ollama_api(
            prompt=prompt,
            temperature=VISION_API_TEMPERATURE,
            max_tokens=VISION_API_MAX_TOKENS
        )
        
        if not analysis_text:
            # API 호출 실패 시 기본 분석 사용
            current_price = market_data.get('current_price', 0)
            fear_greed_data = market_data.get('fear_greed_index', {})
            fear_greed = fear_greed_data.get('value', 50) if isinstance(fear_greed_data, dict) else 50
            rsi = market_data.get('technical_indicators', {}).get('daily_indicators', {}).get('rsi', 50)
            
            if fear_greed > 70:
                analysis_text = f"Fear & Greed Index가 {fear_greed}로 높음. 과매수 상태일 수 있으므로 보수적 접근 권장."
            elif fear_greed < 30:
                analysis_text = f"Fear & Greed Index가 {fear_greed}로 낮음. 과매도 상태일 수 있으므로 매수 기회 고려."
            else:
                analysis_text = f"Fear & Greed Index가 {fear_greed}로 중립. 현재 가격 {current_price:,}원 기준으로 관망."
        
        print(f"🤖 AI 분석 결과: {analysis_text}")
        
        # 기본 결정 구조 생성
        decision = {
            "decision": "hold",  # 기본값
            "confidence": 0.5,
            "risk_level": "medium",
            "expected_price_range": {
                "min": market_data.get('current_price', 0) * 0.95,
                "max": market_data.get('current_price', 0) * 1.05
            },
            "key_indicators": {
                "rsi_signal": "neutral",
                "macd_signal": "neutral",
                "bb_signal": "neutral",
                "trend_strength": "neutral",
                "market_sentiment": "neutral",
                "news_sentiment": "neutral"
            },
            "reason": analysis_text
        }
        
        # 전략 개선 적용
        if STRATEGY_IMPROVEMENT_ENABLED:
            active_improvements = get_active_strategy_improvements()
            if active_improvements:
                decision = apply_strategy_improvements(decision, active_improvements)
                print(f"✅ {len(active_improvements)}개 전략 개선 적용 완료")
            else:
                print("ℹ️ 적용할 전략 개선이 없습니다.")
        else:
            print("ℹ️ 전략 개선 적용이 비활성화되어 있습니다.")
        
        return decision
            
    except Exception as e:
        print(f"❌ AI 분석 중 오류 발생: {e}")
        return None

def ai_trading_decision_with_vision(market_data: Dict[str, Any], chart_image_base64: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Vision API를 사용한 AI 매매 결정 함수 (개선된 버전)"""
    print("=== AI 매매 결정 분석 중 (Vision API 포함) ===")
    
    try:
        if chart_image_base64:
            # Vision API를 사용한 차트 분석
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
            
            vision_analysis = call_ollama_vision_api(
                prompt=vision_prompt,
                image_base64=chart_image_base64,
                temperature=0.2,
                max_tokens=300
            )
            
            print(f"🤖 Vision API 분석 결과: {vision_analysis}")
            
            # Vision 분석 결과 파싱 시도
            try:
                import json
                # JSON 형태가 아닌 경우 텍스트에서 키워드 추출
                if vision_analysis and '{' in vision_analysis and '}' in vision_analysis:
                    # JSON 부분 추출 시도
                    start = vision_analysis.find('{')
                    end = vision_analysis.rfind('}') + 1
                    json_str = vision_analysis[start:end]
                    vision_data = json.loads(json_str)
                else:
                    # 텍스트에서 키워드 추출
                    vision_data = parse_vision_text(vision_analysis)
            except:
                # 파싱 실패 시 기본값 사용
                vision_data = {
                    "trend": "횡보",
                    "trading_signal": "보유",
                    "confidence": "중간",
                    "analysis_summary": vision_analysis or "차트 분석 완료"
                }
        else:
            # 이미지가 없는 경우 기본 분석
            vision_data = {
                "trend": "횡보",
                "trading_signal": "보유",
                "confidence": "중간",
                "analysis_summary": "차트 이미지 없음"
            }
        
        # 시장 데이터 분석
        current_price = market_data.get('current_price', 0)
        fear_greed_data = market_data.get('fear_greed_index', {})
        fear_greed = fear_greed_data.get('value', 50) if isinstance(fear_greed_data, dict) else 50
        
        # 기술적 지표 분석
        technical_indicators = market_data.get('technical_indicators', {})
        daily_indicators = technical_indicators.get('daily_indicators', {})
        
        rsi = daily_indicators.get('rsi', 50)
        macd = daily_indicators.get('macd', 0)
        bb_position = daily_indicators.get('bb_position', 0.5)
        
        # 종합 분석
        market_analysis = analyze_market_indicators(rsi, macd, bb_position, fear_greed)
        
        # Vision 분석과 시장 데이터 통합
        final_decision = integrate_vision_and_market_analysis(vision_data, market_analysis, current_price)
        
        print(f"🎯 최종 매매 결정: {final_decision['decision']}")
        print(f"📊 신뢰도: {final_decision['confidence']}")
        print(f"⚠️ 위험도: {final_decision['risk_level']}")
        
        return final_decision
            
    except Exception as e:
        print(f"❌ Vision API 분석 중 오류 발생: {e}")
        # 오류 발생 시 기본 분석 사용
        return ai_trading_decision_with_indicators(market_data)

def parse_vision_text(vision_text: str) -> Dict[str, str]:
    """Vision 분석 텍스트에서 키워드 추출"""
    result = {
        "trend": "횡보",
        "trading_signal": "보유",
        "confidence": "중간",
        "analysis_summary": vision_text
    }
    
    # 키워드 추출
    if any(word in vision_text.lower() for word in ['상승', 'up', 'bullish', '매수']):
        result["trend"] = "상승"
    elif any(word in vision_text.lower() for word in ['하락', 'down', 'bearish', '매도']):
        result["trend"] = "하락"
    
    if any(word in vision_text.lower() for word in ['매수', 'buy', 'long']):
        result["trading_signal"] = "매수"
    elif any(word in vision_text.lower() for word in ['매도', 'sell', 'short']):
        result["trading_signal"] = "매도"
    
    if any(word in vision_text.lower() for word in ['높음', 'high', '강함']):
        result["confidence"] = "높음"
    elif any(word in vision_text.lower() for word in ['낮음', 'low', '약함']):
        result["confidence"] = "낮음"
    
    return result

def analyze_market_indicators(rsi: float, macd: float, bb_position: float, fear_greed: int) -> Dict[str, Any]:
    """시장 지표 분석"""
    analysis = {
        "rsi_signal": "neutral",
        "macd_signal": "neutral", 
        "bb_signal": "neutral",
        "market_sentiment": "neutral",
        "overall_signal": "hold"
    }
    
    # RSI 분석
    if rsi > 70:
        analysis["rsi_signal"] = "overbought"
    elif rsi < 30:
        analysis["rsi_signal"] = "oversold"
    
    # MACD 분석
    if macd > 0:
        analysis["macd_signal"] = "bullish"
    else:
        analysis["macd_signal"] = "bearish"
    
    # 볼린저 밴드 분석
    if bb_position > 0.8:
        analysis["bb_signal"] = "upper_band"
    elif bb_position < 0.2:
        analysis["bb_signal"] = "lower_band"
    else:
        analysis["bb_signal"] = "middle"
    
    # 공포탐욕지수 분석
    if fear_greed > 75:
        analysis["market_sentiment"] = "extreme_greed"
    elif fear_greed > 55:
        analysis["market_sentiment"] = "greed"
    elif fear_greed < 25:
        analysis["market_sentiment"] = "extreme_fear"
    elif fear_greed < 45:
        analysis["market_sentiment"] = "fear"
    else:
        analysis["market_sentiment"] = "neutral"
    
    return analysis

def integrate_vision_and_market_analysis(vision_data: Dict[str, Any], market_analysis: Dict[str, Any], current_price: float) -> Dict[str, Any]:
    """Vision 분석과 시장 데이터 통합"""
    
    # 기본 결정 구조
    decision = {
        "decision": "hold",
        "confidence": 0.5,
        "risk_level": "medium",
        "expected_price_range": {
            "min": current_price * 0.95,
            "max": current_price * 1.05
        },
        "key_indicators": market_analysis,
        "vision_analysis": vision_data,
        "reason": f"Vision: {vision_data.get('analysis_summary', '')} | Market: RSI {market_analysis.get('rsi_signal', 'neutral')}"
    }
    
    # Vision 신호와 시장 신호 통합
    vision_signal = vision_data.get('trading_signal', '보유')
    vision_confidence = vision_data.get('confidence', '중간')
    trend = market_analysis.get('trend', 'neutral')
    
    # 신뢰도 계산 (하락 추세에서는 신뢰도 감소)
    confidence_map = {"높음": 0.8, "중간": 0.5, "낮음": 0.3}
    confidence = confidence_map.get(vision_confidence, 0.5)
    
    # 하락 추세에서는 신뢰도 30% 감소
    if trend == "downward":
        confidence *= 0.7
        decision["reason"] += " | 하락 추세로 인한 신중한 접근"
    
    # 매매 결정 로직 (더 엄격한 조건)
    if vision_signal == "매수":
        # 매수 조건: RSI 과매도 + MACD 강세 + 볼린저 밴드 하단 + (상승추세 또는 중립)
        if (market_analysis["rsi_signal"] == "oversold" and 
            market_analysis["macd_signal"] == "bullish" and 
            market_analysis["bb_signal"] == "lower_band" and 
            trend != "downward"):
            decision["decision"] = "buy"
            decision["confidence"] = min(confidence + 0.2, 1.0)
            decision["reason"] += " | 모든 매수 조건 충족"
        else:
            decision["decision"] = "hold"
            decision["confidence"] = max(confidence - 0.1, 0.3)
            decision["reason"] += " | 매수 조건 불충분"
    
    elif vision_signal == "매도":
        # 매도 조건: RSI 과매수 또는 (하락추세 + MACD 약세)
        if (market_analysis["rsi_signal"] == "overbought" or 
            (trend == "downward" and market_analysis["macd_signal"] == "bearish")):
            decision["decision"] = "sell"
            decision["confidence"] = min(confidence + 0.2, 1.0)
            decision["reason"] += " | 매도 조건 충족"
        else:
            decision["decision"] = "hold"
            decision["confidence"] = confidence
    
    else:
        decision["decision"] = "hold"
        decision["confidence"] = confidence
    
    # 위험도 설정
    if decision["confidence"] > 0.7:
        decision["risk_level"] = "low"
    elif decision["confidence"] < 0.4:
        decision["risk_level"] = "high"
    else:
        decision["risk_level"] = "medium"
    
    return decision
