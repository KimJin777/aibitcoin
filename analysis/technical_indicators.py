"""
기술적 지표 계산 모듈
다양한 기술적 지표들을 계산합니다.
"""

import pandas as pd
import numpy as np
import ta
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator
from ta.momentum import StochasticOscillator, WilliamsRIndicator, RSIIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator
from typing import Optional

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """기술적 지표 계산 함수"""
    if df.empty:
        return df
    
    # 기본 OHLCV 컬럼명 확인 및 통일
    required_columns = ['open', 'high', 'low', 'close', 'volume']
    df_columns = [col.lower() for col in df.columns]
    
    # 컬럼명 매핑
    column_mapping = {}
    for req_col in required_columns:
        for df_col in df.columns:
            if req_col in df_col.lower():
                column_mapping[req_col] = df_col
                break
    
    # 필수 컬럼이 없으면 원본 반환
    if len(column_mapping) < 5:
        print("❌ 필수 OHLCV 컬럼을 찾을 수 없습니다.")
        return df
    
    # 컬럼명 통일
    df_renamed = df.rename(columns={
        column_mapping['open']: 'Open',
        column_mapping['high']: 'High', 
        column_mapping['low']: 'Low',
        column_mapping['close']: 'Close',
        column_mapping['volume']: 'Volume'
    })
    
    try:
        # 1. 이동평균선 (SMA, EMA)
        df_renamed['SMA_20'] = SMAIndicator(close=df_renamed['Close'], window=20).sma_indicator()
        df_renamed['SMA_50'] = SMAIndicator(close=df_renamed['Close'], window=50).sma_indicator()
        df_renamed['EMA_12'] = EMAIndicator(close=df_renamed['Close'], window=12).ema_indicator()
        df_renamed['EMA_26'] = EMAIndicator(close=df_renamed['Close'], window=26).ema_indicator()
        
        # 2. MACD
        macd = MACD(close=df_renamed['Close'])
        df_renamed['MACD'] = macd.macd()
        df_renamed['MACD_Signal'] = macd.macd_signal()
        df_renamed['MACD_Histogram'] = macd.macd_diff()
        
        # 3. RSI
        df_renamed['RSI'] = RSIIndicator(close=df_renamed['Close']).rsi()
        
        # 4. 볼린저 밴드
        bb = BollingerBands(close=df_renamed['Close'])
        df_renamed['BB_Upper'] = bb.bollinger_hband()
        df_renamed['BB_Middle'] = bb.bollinger_mavg()
        df_renamed['BB_Lower'] = bb.bollinger_lband()
        df_renamed['BB_Width'] = bb.bollinger_wband()
        df_renamed['BB_Position'] = bb.bollinger_pband()
        
        # 5. 스토캐스틱
        stoch = StochasticOscillator(high=df_renamed['High'], low=df_renamed['Low'], close=df_renamed['Close'])
        df_renamed['Stoch_K'] = stoch.stoch()
        df_renamed['Stoch_D'] = stoch.stoch_signal()
        
        # 6. 윌리엄스 %R
        df_renamed['Williams_R'] = WilliamsRIndicator(high=df_renamed['High'], low=df_renamed['Low'], close=df_renamed['Close']).williams_r()
        
        # 7. ATR (Average True Range)
        df_renamed['ATR'] = AverageTrueRange(high=df_renamed['High'], low=df_renamed['Low'], close=df_renamed['Close']).average_true_range()
        
        # 8. ADX (Average Directional Index)
        adx = ADXIndicator(high=df_renamed['High'], low=df_renamed['Low'], close=df_renamed['Close'])
        df_renamed['ADX'] = adx.adx()
        df_renamed['ADX_Pos'] = adx.adx_pos()
        df_renamed['ADX_Neg'] = adx.adx_neg()
        
        # 9. 거래량 지표
        df_renamed['OBV'] = OnBalanceVolumeIndicator(close=df_renamed['Close'], volume=df_renamed['Volume']).on_balance_volume()
        
        # 10. 추가 모멘텀 지표
        # ROC (Rate of Change)
        df_renamed['ROC'] = ta.momentum.ROCIndicator(close=df_renamed['Close']).roc()
        
        # CCI (Commodity Channel Index)
        df_renamed['CCI'] = ta.trend.CCIIndicator(high=df_renamed['High'], low=df_renamed['Low'], close=df_renamed['Close']).cci()
        
        print(f"✅ 기술적 지표 계산 완료: {len(df_renamed.columns)}개 컬럼")
        
    except Exception as e:
        print(f"❌ 기술적 지표 계산 중 오류 발생: {e}")
        return df
    
    return df_renamed

def get_latest_indicators(df: pd.DataFrame) -> Optional[dict]:
    """최신 기술적 지표 값들 반환"""
    if df.empty:
        return None
    
    latest = df.iloc[-1] if len(df) > 0 else None
    if latest is None:
        return None
    
    indicators = {}
    
    # 기본 지표들
    basic_indicators = ['SMA_20', 'SMA_50', 'EMA_12', 'EMA_26', 'RSI', 'MACD', 'MACD_Signal']
    for indicator in basic_indicators:
        if indicator in latest:
            indicators[indicator] = float(latest[indicator])
    
    # 볼린저 밴드
    bb_indicators = ['BB_Upper', 'BB_Middle', 'BB_Lower', 'BB_Position']
    for indicator in bb_indicators:
        if indicator in latest:
            indicators[indicator] = float(latest[indicator])
    
    # 기타 지표들
    other_indicators = ['Stoch_K', 'Stoch_D', 'Williams_R', 'ATR', 'ADX', 'CCI', 'ROC']
    for indicator in other_indicators:
        if indicator in latest:
            indicators[indicator] = float(latest[indicator])
    
    return indicators

def analyze_technical_signals(df: pd.DataFrame) -> dict:
    """기술적 신호 분석"""
    if df.empty:
        return {}
    
    latest = df.iloc[-1] if len(df) > 0 else None
    if latest is None:
        return {}
    
    signals = {}
    
    # RSI 신호
    rsi = latest.get('RSI', 50)
    if rsi > 70:
        signals['rsi_signal'] = 'overbought'
    elif rsi < 30:
        signals['rsi_signal'] = 'oversold'
    else:
        signals['rsi_signal'] = 'neutral'
    
    # MACD 신호
    macd = latest.get('MACD', 0)
    macd_signal = latest.get('MACD_Signal', 0)
    if macd > macd_signal:
        signals['macd_signal'] = 'bullish'
    elif macd < macd_signal:
        signals['macd_signal'] = 'bearish'
    else:
        signals['macd_signal'] = 'neutral'
    
    # 볼린저 밴드 신호
    bb_position = latest.get('BB_Position', 0.5)
    if bb_position > 0.8:
        signals['bb_signal'] = 'upper_band'
    elif bb_position < 0.2:
        signals['bb_signal'] = 'lower_band'
    else:
        signals['bb_signal'] = 'middle'
    
    # 트렌드 강도
    adx = latest.get('ADX', 25)
    if adx > 25:
        signals['trend_strength'] = 'strong'
    elif adx > 15:
        signals['trend_strength'] = 'weak'
    else:
        signals['trend_strength'] = 'neutral'
    
    return signals
