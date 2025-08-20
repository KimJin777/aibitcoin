import os
from dotenv import load_dotenv
load_dotenv()

import requests
import json
from datetime import datetime, timedelta
import time
import pandas as pd
from data.market_data import get_market_data

def get_bitcoin_news():
    """
    Google News API를 사용하여 비트코인 관련 뉴스 수집
    """
    print("=== 비트코인 뉴스 수집 중 ===")
    
    # SerpAPI 키 확인
    serp_api_key = os.getenv("SERP_API_KEY")
    if not serp_api_key:
        print("오류: SERP_API_KEY가 설정되지 않았습니다.")
        return None
    
    try:
        # Google News API 요청
        url = "https://serpapi.com/search"
        params = {
            "engine": "google_news",
            "q": "bitcoin cryptocurrency",
            "gl": "kr",  # 한국
            "hl": "ko",  # 한국어
            "api_key": serp_api_key,
            "num": 20  # 최대 20개 뉴스
        }
        
        print("Google News API 요청 중...")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # 검색 상태 확인
        if data.get('search_metadata', {}).get('status') == 'Success':
            news_results = data.get('news_results', [])
            
            if news_results:
                print(f"뉴스 수집 완료: {len(news_results)}개")
                
                # 뉴스 데이터 정리
                processed_news = []
                for news in news_results:
                    try:
                        processed_news.append({
                            'title': news.get('title', ''),
                            'link': news.get('link', ''),
                            'snippet': news.get('snippet', ''),
                            'source': news.get('source', ''),
                            'date': news.get('date', ''),
                            'position': news.get('position', 0)
                        })
                    except Exception as e:
                        print(f"뉴스 데이터 처리 중 오류: {e}")
                        continue
                
                return processed_news
            else:
                print("뉴스 결과가 없습니다.")
                return None
        else:
            print(f"API 요청 실패: {data.get('search_metadata', {}).get('status')}")
            return None
            
    except Exception as e:
        print(f"뉴스 수집 중 오류 발생: {e}")
        return None

def analyze_news_sentiment(news_data, market_data=None):
    """
    뉴스 감정 분석 (가격 데이터 통합)
    """
    print("=== 뉴스 및 시장 데이터 감정 분석 중 ===")
    
    if not news_data:
        return None
        
    # 가격 데이터 분석
    price_trend = "neutral"
    price_change_pct = 0
    
    if market_data and 'daily_df' in market_data:
        df = market_data['daily_df']
        if not df.empty:
            last_prices = df['close'].tail(2).values
            if len(last_prices) >= 2:
                price_change_pct = ((last_prices[1] - last_prices[0]) / last_prices[0]) * 100
                if price_change_pct < -2:  # 2% 이상 하락
                    price_trend = "bearish"
                elif price_change_pct > 2:  # 2% 이상 상승
                    price_trend = "bullish"
                    
        print(f"📊 가격 변동: {price_change_pct:.2f}% ({price_trend})")
    
    # 긍정적/부정적 키워드 정의
    positive_keywords = [
        '상승', '급등', '돌파', '강세', '호재', '긍정', '낙관', '성장', '기대',
        'bullish', 'rally', 'surge', 'breakout', 'positive', 'growth', 'optimistic'
    ]
    
    negative_keywords = [
        '하락', '급락', '폭락', '약세', '악재', '부정', '비관', '위험', '우려',
        'bearish', 'crash', 'drop', 'decline', 'negative', 'risk', 'concern'
    ]
    
    analyzed_news = []
    
    for news in news_data:
        title = news['title'].lower()
        snippet = news['snippet'].lower()
        full_text = f"{title} {snippet}"
        
        # 키워드 매칭
        positive_count = sum(1 for keyword in positive_keywords if keyword in full_text)
        negative_count = sum(1 for keyword in negative_keywords if keyword in full_text)
        
        # 감정 점수 계산 (-1 ~ 1)
        if positive_count > 0 or negative_count > 0:
            sentiment_score = (positive_count - negative_count) / max(positive_count + negative_count, 1)
        else:
            sentiment_score = 0
        
        # 감정 분류
        if sentiment_score > 0.3:
            sentiment = "긍정"
        elif sentiment_score < -0.3:
            sentiment = "부정"
        else:
            sentiment = "중립"
        
        analyzed_news.append({
            **news,
            'sentiment_score': sentiment_score,
            'sentiment': sentiment,
            'positive_keywords': positive_count,
            'negative_keywords': negative_count
        })
    
    return analyzed_news

def display_news_summary(news_data):
    """
    뉴스 요약 표시
    """
    if not news_data:
        print("표시할 뉴스가 없습니다.")
        return
    
    print("\n" + "=" * 80)
    print("📰 비트코인 최신 뉴스 헤드라인")
    print("=" * 80)
    
    # 감정별 통계
    sentiment_stats = {}
    for news in news_data:
        sentiment = news.get('sentiment', '중립')
        sentiment_stats[sentiment] = sentiment_stats.get(sentiment, 0) + 1
    
    print(f"\n📊 뉴스 감정 분석 결과:")
    for sentiment, count in sentiment_stats.items():
        print(f"  {sentiment}: {count}개")
    
    # 뉴스 목록 표시
    print(f"\n📋 상위 {len(news_data)}개 뉴스:")
    for i, news in enumerate(news_data, 1):
        sentiment_emoji = {
            "긍정": "🟢",
            "부정": "🔴", 
            "중립": "🟡"
        }.get(news['sentiment'], "⚪")
        
        print(f"\n{i}. {sentiment_emoji} {news['title']}")
        print(f"   📰 {news['source']} | {news['date']}")
        print(f"   📝 {news['snippet'][:100]}...")
        print(f"   🔗 {news['link']}")
        print(f"   💭 감정: {news['sentiment']} (점수: {news['sentiment_score']:.2f})")

def get_market_impact_analysis(news_data, market_data=None):
    """
    뉴스와 가격 데이터 기반 시장 영향 분석
    """
    print("\n=== 시장 영향 분석 ===")
    
    if not news_data:
        return
        
    # 가격 동향 분석
    price_trend = "neutral"
    current_price = None
    price_change_24h = 0
    
    if market_data:
        if 'current_price' in market_data:
            current_price = market_data['current_price']
            
        if 'daily_df' in market_data and not market_data['daily_df'].empty:
            df = market_data['daily_df']
            last_prices = df['close'].tail(2).values
            if len(last_prices) >= 2:
                price_change_24h = ((last_prices[1] - last_prices[0]) / last_prices[0]) * 100
                if price_change_24h < -2:
                    price_trend = "bearish"
                elif price_change_24h > 2:
                    price_trend = "bullish"
                    
        print(f"\n💰 현재 가격: {current_price:,}원")
        print(f"📈 24시간 변동: {price_change_24h:.2f}% ({price_trend})")
    
    # 감정 점수 평균
    sentiment_scores = [news['sentiment_score'] for news in news_data]
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
    
    # 긍정/부정 뉴스 비율
    positive_news = [news for news in news_data if news['sentiment'] == '긍정']
    negative_news = [news for news in news_data if news['sentiment'] == '부정']
    neutral_news = [news for news in news_data if news['sentiment'] == '중립']
    
    total_news = len(news_data)
    positive_ratio = len(positive_news) / total_news * 100
    negative_ratio = len(negative_news) / total_news * 100
    neutral_ratio = len(neutral_news) / total_news * 100
    
    print(f"📈 전체 뉴스 감정 점수: {avg_sentiment:.2f}")
    print(f"📊 뉴스 분포:")
    print(f"  🟢 긍정적 뉴스: {len(positive_news)}개 ({positive_ratio:.1f}%)")
    print(f"  🔴 부정적 뉴스: {len(negative_news)}개 ({negative_ratio:.1f}%)")
    print(f"  🟡 중립적 뉴스: {len(neutral_news)}개 ({neutral_ratio:.1f}%)")
    
    # 시장 영향 예측
    if avg_sentiment > 0.2:
        market_impact = "🟢 긍정적 - 상승 압력 예상"
    elif avg_sentiment < -0.2:
        market_impact = "🔴 부정적 - 하락 압력 예상"
    else:
        market_impact = "🟡 중립적 - 횡보 예상"
    
    print(f"\n🎯 시장 영향 예측: {market_impact}")
    
    # 주요 키워드 분석
    print(f"\n🔍 주요 키워드 분석:")
    all_titles = " ".join([news['title'] + " " + news['snippet'] for news in news_data]).lower()
    
    keywords = {
        '가격': all_titles.count('가격') + all_titles.count('price'),
        '규제': all_titles.count('규제') + all_titles.count('regulation'),
        '기관': all_titles.count('기관') + all_titles.count('institution'),
        'ETF': all_titles.count('etf'),
        '채택': all_titles.count('채택') + all_titles.count('adoption'),
        '기술': all_titles.count('기술') + all_titles.count('technology')
    }
    
    for keyword, count in sorted(keywords.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {keyword}: {count}회 언급")

def get_trading_recommendation(analyzed_news, market_data=None):
    """
    뉴스와 가격 데이터 기반 매매 추천
    """
    if not analyzed_news:
        return "hold", "데이터 부족"
        
    # 감정 점수 평균
    sentiment_scores = [news['sentiment_score'] for news in analyzed_news]
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
    
    # 가격 동향 분석
    price_trend = "neutral"
    price_change_24h = 0
    price_change_momentum = 0
    
    if market_data and 'daily_df' in market_data and not market_data['daily_df'].empty:
        df = market_data['daily_df']
        # 24시간 가격 변화
        last_prices = df['close'].tail(2).values
        if len(last_prices) >= 2:
            price_change_24h = ((last_prices[1] - last_prices[0]) / last_prices[0]) * 100
            
        # 추세 모멘텀 (3일)
        if len(df) >= 3:
            last_3_prices = df['close'].tail(3).values
            price_change_momentum = ((last_3_prices[2] - last_3_prices[0]) / last_3_prices[0]) * 100
    
    # 매매 추천 로직
    if market_data and price_change_24h < -3 and price_change_momentum < -5:
        # 하락 추세가 강할 때
        if avg_sentiment < -0.2:
            return "sell", "강한 하락 추세와 부정적 뉴스"
        else:
            return "hold", "강한 하락 추세, 뉴스 중립적"
    elif market_data and price_change_24h > 3 and avg_sentiment > 0.3:
        # 상승 추세와 긍정적 뉴스
        return "buy", "상승 추세와 긍정적 뉴스"
    elif avg_sentiment < -0.3:
        # 매우 부정적인 뉴스
        return "sell", "매우 부정적인 뉴스 분위기"
    elif avg_sentiment > 0.3 and price_change_momentum > 0:
        # 긍정적 뉴스와 상승 모멘텀
        return "buy", "긍정적 뉴스와 상승 모멘텀"
    else:
        return "hold", "뚜렷한 신호 없음"

def main_news_cycle():
    """
    메인 뉴스 분석 사이클
    """
    print("=" * 80)
    print("📰 비트코인 뉴스 분석 시스템")
    print("=" * 80)
    
    try:
        # 시장 데이터 수집
        daily_df, minute_df, current_price, orderbook, fear_greed_data = get_market_data()
        market_data = {
            'daily_df': daily_df,
            'minute_df': minute_df,
            'current_price': current_price,
            'orderbook': orderbook,
            'fear_greed_data': fear_greed_data
        }
        
        # 뉴스 수집
        news_data = get_bitcoin_news()
        
        if news_data:
            # 뉴스 감정 분석 (가격 데이터 통합)
            analyzed_news = analyze_news_sentiment(news_data, market_data)
            
            if analyzed_news:
                # 뉴스 요약 표시
                display_news_summary(analyzed_news)
                
                # 시장 영향 분석
                get_market_impact_analysis(analyzed_news, market_data)
                
                # 매매 추천
                recommendation, reason = get_trading_recommendation(analyzed_news, market_data)
                print(f"\n💡 매매 추천: {recommendation.upper()} ({reason})")
                
                # 분석 결과 저장
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"bitcoin_news_analysis_{timestamp}.json"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump({
                        'analysis_time': datetime.now().isoformat(),
                        'total_news': len(analyzed_news),
                        'news_data': analyzed_news
                    }, f, ensure_ascii=False, indent=2)
                
                print(f"\n💾 분석 결과가 {filename}에 저장되었습니다.")
            else:
                print("뉴스 감정 분석 실패")
        else:
            print("뉴스 수집 실패")
            
    except Exception as e:
        print(f"뉴스 분석 중 오류 발생: {e}")

if __name__ == "__main__":
    import time
    
    print("🚀 비트코인 뉴스 분석 시스템을 시작합니다...")
    print("💡 .env 파일에 SERP_API_KEY를 설정해주세요.")
    print("💡 예시: SERP_API_KEY=your_serpapi_key_here")
    print()
    
    while True:
        try:
            # 메인 뉴스 분석 사이클 실행
            main_news_cycle()
            
            print("\n" + "=" * 80)
            print("⏰ 30분 후 다음 뉴스 분석을 시작합니다...")
            print("=" * 80 + "\n")
            time.sleep(60 * 30)  # 30분 대기
            
        except KeyboardInterrupt:
            print("\n👋 뉴스 분석 시스템을 종료합니다.")
            break
        except Exception as e:
            print(f"❌ 예상치 못한 오류 발생: {e}")
            print("🔄 5분 후 재시도합니다...")
            time.sleep(60 * 5)
