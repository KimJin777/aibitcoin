"""
뉴스 데이터 수집 및 분석 모듈
Google News API를 통해 비트코인 관련 뉴스를 수집하고 감정 분석을 수행합니다.
"""

import requests
from typing import Optional, List, Dict, Any
from config.settings import SERP_API_KEY, NEWS_COUNT, NEWS_LANGUAGE, NEWS_REGION
import datetime
from database.connection import get_db_connection
import json

def save_news_to_db(news_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now()
    
    # 리스트를 JSON 문자열로 변환
    news_json = json.dumps(news_data)
    
    cursor.execute(
        "INSERT INTO news (data, fetched_at) VALUES (%s, %s)",
        (news_json, now)
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_cached_news_from_db():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
    
    cursor.execute(
        "SELECT * FROM news WHERE fetched_at >= %s ORDER BY fetched_at DESC LIMIT 1",
        (one_hour_ago,)
    )
    
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if result:
        # JSON 문자열을 파이썬 객체로 변환
        return {'data': json.loads(result['data'])}
    return None

def get_bitcoin_news() -> Optional[List[Dict[str, Any]]]:
    """Google News API를 사용하여 비트코인 관련 뉴스 수집"""
    print("=== 비트코인 뉴스 수집 중 ===")
    
    if not SERP_API_KEY:
        print("⚠️ SERP_API_KEY가 설정되지 않아 뉴스 분석을 건너뜁니다.")
        return None
    
    news = get_cached_news_from_db()
    if news:
        return news['data']
    
    try:
        url = "https://serpapi.com/search"
        params = {
            "engine": "google_news",
            "q": "bitcoin cryptocurrency",
            "gl": NEWS_REGION,
            "hl": NEWS_LANGUAGE,
            "api_key": SERP_API_KEY,
            "num": NEWS_COUNT
        }
        
        print("📰 Google News API 요청 중...")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('search_metadata', {}).get('status') == 'Success':
            news_results = data.get('news_results', [])
            
            if news_results:
                print(f"✅ 뉴스 수집 완료: {len(news_results)}개")
                
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
                        print(f"⚠️ 뉴스 데이터 처리 중 오류: {e}")
                        continue
                
                save_news_to_db(processed_news)
                
                return processed_news
            else:
                print("❌ 뉴스 결과가 없습니다.")
                return None
        else:
            print(f"❌ API 요청 실패: {data.get('search_metadata', {}).get('status')}")
            return None
            
    except Exception as e:
        print(f"❌ 뉴스 수집 중 오류 발생: {e}")
        return None

def analyze_news_sentiment(news_data: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
    """뉴스 감정 분석 (키워드 기반)"""
    if not news_data:
        return None
    
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

def get_news_summary(analyzed_news: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """뉴스 요약 정보 생성"""
    if not analyzed_news:
        return None
    
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
    
    # 뉴스 요약 출력
    print(f"\n📰 최신 뉴스 분석 결과:")
    sentiment_stats = {}
    for news in analyzed_news:
        sentiment = news.get('sentiment', '중립')
        sentiment_stats[sentiment] = sentiment_stats.get(sentiment, 0) + 1
    
    for sentiment, count in sentiment_stats.items():
        print(f"  {sentiment}: {count}개")
    
    return news_summary
