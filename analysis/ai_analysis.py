"""
AI 분석 모듈
"""

import json
import base64
from datetime import datetime
from typing import Optional, Dict, Any, List
import google.generativeai as genai
from .models import TradingDecision
from config.settings import GOOGLE_API_KEY

# Gemini API 설정
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

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
        client = genai.GenerativeModel('gemini-pro') # Changed from OpenAI to Gemini
        
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
        
        response = client.generate_content(
            prompt=analysis_prompt,
            generation_config=genai.GenerateContentRequest.GenerationConfig(
                max_output_tokens=500,
                temperature=0.7 # Increased temperature for more creative output
            )
        )
        
        analysis_text = response.text
        
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

def ai_trading_decision_with_indicators(market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """기술적 지표를 포함한 AI 매매 결정 함수"""
    print("=== AI 매매 결정 분석 중 (기술적 지표 포함) ===")
    
    client = genai.GenerativeModel('gemini-pro') # Changed from OpenAI to Gemini
    
    # 기술적 지표, 공포탐욕지수, 뉴스를 포함한 개선된 시스템 메시지
    system_message = """
    You are a Bitcoin investment expert with deep knowledge of technical analysis, market psychology, and news sentiment analysis.
    
    Analyze the provided market data including:
    1. 30-day daily OHLCV data with technical indicators
    2. Recent 100-minute OHLCV data with technical indicators
    3. Current price and orderbook information
    4. Technical indicators summary (RSI, MACD, Bollinger Bands, etc.)
    5. Fear and Greed Index data (market sentiment indicator)
    6. Recent news sentiment analysis (positive/negative/neutral news distribution)
    
    Consider these technical analysis factors:
    - Moving Averages (SMA, EMA) trends and crossovers
    - RSI overbought/oversold conditions (RSI > 70 = overbought, RSI < 30 = oversold)
    - MACD signal line crossovers and histogram patterns
    - Bollinger Bands position and width (BB_Position: 0-1, where 0.5 is middle)
    - Stochastic oscillator signals (K and D lines)
    - Williams %R overbought/oversold levels
    - ATR for volatility assessment
    - ADX for trend strength (ADX > 25 = strong trend)
    - CCI for momentum (CCI > 100 = overbought, CCI < -100 = oversold)
    - ROC for momentum confirmation
    
    Fear and Greed Index Analysis:
    - Extreme Fear (0-25): Often indicates oversold conditions, potential buying opportunities
    - Fear (26-45): Market uncertainty, cautious approach recommended
    - Neutral (46-55): Balanced market sentiment
    - Greed (56-75): Market optimism, watch for overbought conditions
    - Extreme Greed (76-100): Often indicates overbought conditions, potential selling opportunities
    
    News Sentiment Analysis:
    - Positive news sentiment: May indicate bullish momentum or positive market sentiment
    - Negative news sentiment: May indicate bearish pressure or negative market sentiment
    - Neutral news sentiment: Balanced market sentiment
    - Consider news sentiment in combination with technical indicators for confirmation
    
    Price trends and momentum patterns
    Volume patterns and OBV trends
    Support/resistance levels from Bollinger Bands
    Market volatility from ATR
    Orderbook depth and spread
    Market sentiment from Fear and Greed Index
    News sentiment impact on market psychology
    
    Be conservative and consider risk management in your recommendations.
    Use technical indicators to confirm signals rather than relying on single indicators.
    Consider market sentiment from Fear and Greed Index for contrarian opportunities.
    Consider news sentiment for additional market psychology insights.
    
    Provide your analysis in JSON format using the structured output function.
    """
    
    try:
        response = client.generate_content(
            prompt=f"Please analyze this Bitcoin market data with technical indicators and provide trading decision: {json.dumps(market_data, default=str)}",
            generation_config=genai.GenerateContentRequest.GenerationConfig(
                max_output_tokens=500,
                temperature=0.3,  # 더 보수적인 결정을 위해 낮은 temperature 사용
                tools=[{
                    "type": "function",
                    "function": {
                        "name": "get_trading_decision",
                        "description": "비트코인 매매 결정을 위한 구조화된 출력",
                        "parameters": TradingDecision.model_json_schema()
                    }
                }],
                tool_choice={"type": "function", "function": {"name": "get_trading_decision"}}
            )
        )
        
        # Structured output 파싱
        tool_calls = response.tool_calls
        if tool_calls and len(tool_calls) > 0:
            arguments = json.loads(tool_calls[0].function.arguments)
            decision = TradingDecision(**arguments)
            
            # 결과 출력
            print(f"📈 AI 결정: {decision.decision}")
            print(f"🎯 신뢰도: {decision.confidence}")
            print(f"⚠️ 위험도: {decision.risk_level}")
            print(f"💰 예상 가격 범위: {decision.expected_price_range.min:,.0f}원 ~ {decision.expected_price_range.max:,.0f}원")
            print(f"📊 주요 지표:")
            print(f"   - RSI 신호: {decision.key_indicators.rsi_signal}")
            print(f"   - MACD 신호: {decision.key_indicators.macd_signal}")
            print(f"   - 볼린저밴드 신호: {decision.key_indicators.bb_signal}")
            print(f"   - 트렌드 강도: {decision.key_indicators.trend_strength}")
            print(f"   - 시장 심리: {decision.key_indicators.market_sentiment}")
            print(f"   - 뉴스 감정: {decision.key_indicators.news_sentiment}")
            print(f"📝 분석 이유: {decision.reason}")
            
            return decision.model_dump()
        else:
            print("❌ Structured output 파싱 실패")
            return None
            
    except Exception as e:
        print(f"❌ AI 분석 중 오류 발생: {e}")
        return None

def ai_trading_decision_with_vision(market_data: Dict[str, Any], chart_image_base64: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Vision API를 사용한 AI 매매 결정 함수"""
    print("=== AI 매매 결정 분석 중 (Vision API 포함) ===")
    
    client = genai.GenerativeModel('gemini-pro') # Changed from OpenAI to Gemini
    
    # Vision API를 위한 시스템 메시지
    system_message = """
    You are a Bitcoin investment expert with deep knowledge of technical analysis, market psychology, and news sentiment analysis.
    
    You will analyze:
    1. Market data including technical indicators, Fear and Greed Index, and news sentiment
    2. A chart screenshot showing the current Bitcoin price chart with technical indicators (1-hour timeframe with Bollinger Bands)
    
    When analyzing the chart image, focus on:
    - Price action patterns and trends
    - Technical indicator positions (Bollinger Bands, moving averages, etc.)
    - Support and resistance levels
    - Volume patterns
    - Chart patterns (head and shoulders, triangles, etc.)
    - Candlestick patterns
    - Overall market structure and momentum
    
    Consider these technical analysis factors:
    - Moving Averages (SMA, EMA) trends and crossovers
    - RSI overbought/oversold conditions (RSI > 70 = overbought, RSI < 30 = oversold)
    - MACD signal line crossovers and histogram patterns
    - Bollinger Bands position and width (BB_Position: 0-1, where 0.5 is middle)
    - Stochastic oscillator signals (K and D lines)
    - Williams %R overbought/oversold levels
    - ATR for volatility assessment
    - ADX for trend strength (ADX > 25 = strong trend)
    - CCI for momentum (CCI > 100 = overbought, CCI < -100 = oversold)
    - ROC for momentum confirmation
    
    Fear and Greed Index Analysis:
    - Extreme Fear (0-25): Often indicates oversold conditions, potential buying opportunities
    - Fear (26-45): Market uncertainty, cautious approach recommended
    - Neutral (46-55): Balanced market sentiment
    - Greed (56-75): Market optimism, watch for overbought conditions
    - Extreme Greed (76-100): Often indicates overbought conditions, potential selling opportunities
    
    News Sentiment Analysis:
    - Positive news sentiment: May indicate bullish momentum or positive market sentiment
    - Negative news sentiment: May indicate bearish pressure or negative market sentiment
    - Neutral news sentiment: Balanced market sentiment
    - Consider news sentiment in combination with technical indicators for confirmation
    
    Be conservative and consider risk management in your recommendations.
    Use technical indicators to confirm signals rather than relying on single indicators.
    Consider market sentiment from Fear and Greed Index for contrarian opportunities.
    Consider news sentiment for additional market psychology insights.
    
    Provide your analysis in JSON format using the structured output function.
    """
    
    try:
        # 메시지 구성
        messages = [
            {
                "role": "system",
                "content": system_message
            }
        ]
        
        # 차트 이미지가 있는 경우 Vision API 사용
        if chart_image_base64:
            user_content = [
                {
                    "type": "text",
                    "text": f"Please analyze this Bitcoin market data with technical indicators and the provided chart image to provide trading decision: {json.dumps(market_data, default=str)}"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{chart_image_base64}"
                    }
                }
            ]
        else:
            # 이미지가 없는 경우 기존 방식 사용
            user_content = f"Please analyze this Bitcoin market data with technical indicators and provide trading decision: {json.dumps(market_data, default=str)}"
        
        messages.append({"role": "user", "content": user_content})
        
        response = client.generate_content(
            prompt=f"Please analyze this Bitcoin market data with technical indicators and the provided chart image to provide trading decision: {json.dumps(market_data, default=str)}",
            generation_config=genai.GenerateContentRequest.GenerationConfig(
                max_output_tokens=500,
                temperature=0.3,
                tools=[{
                    "type": "function",
                    "function": {
                        "name": "get_trading_decision_with_vision",
                        "description": "비트코인 매매 결정을 위한 구조화된 출력 (Vision API 포함)",
                        "parameters": TradingDecision.model_json_schema()
                    }
                }],
                tool_choice={"type": "function", "function": {"name": "get_trading_decision_with_vision"}}
            )
        )
        
        # Structured output 파싱
        tool_calls = response.tool_calls
        if tool_calls and len(tool_calls) > 0:
            arguments = json.loads(tool_calls[0].function.arguments)
            decision = TradingDecision(**arguments)
            
            # 결과 출력
            print(f"📈 AI 결정: {decision.decision}")
            print(f"🎯 신뢰도: {decision.confidence}")
            print(f"⚠️ 위험도: {decision.risk_level}")
            print(f"💰 예상 가격 범위: {decision.expected_price_range.min:,.0f}원 ~ {decision.expected_price_range.max:,.0f}원")
            print(f"📊 주요 지표:")
            print(f"   - RSI 신호: {decision.key_indicators.rsi_signal}")
            print(f"   - MACD 신호: {decision.key_indicators.macd_signal}")
            print(f"   - 볼린저밴드 신호: {decision.key_indicators.bb_signal}")
            print(f"   - 트렌드 강도: {decision.key_indicators.trend_strength}")
            print(f"   - 시장 심리: {decision.key_indicators.market_sentiment}")
            print(f"   - 뉴스 감정: {decision.key_indicators.news_sentiment}")
            
            if decision.chart_analysis:
                print(f"📊 차트 분석:")
                print(f"   - 가격 액션: {decision.chart_analysis.price_action}")
                print(f"   - 지지선: {decision.chart_analysis.support_level}")
                print(f"   - 저항선: {decision.chart_analysis.resistance_level}")
                print(f"   - 차트 패턴: {decision.chart_analysis.chart_pattern}")
                print(f"   - 거래량 분석: {decision.chart_analysis.volume_analysis}")
            
            print(f"📝 분석 이유: {decision.reason}")
            
            return decision.model_dump()
        else:
            print("❌ Structured output 파싱 실패")
            return None
            
    except Exception as e:
        print(f"❌ AI 분석 중 오류 발생: {e}")
        return None
