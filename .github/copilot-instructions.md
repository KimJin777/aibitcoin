# Bitcoin Trading System - AI Agent Guide

## Core Architecture

```
data/ → analysis/ → trading/
├── market_data.py    → technical_indicators.py → execution.py
├── news_data.py      → ai_analysis.py         → account.py
└── screenshot.py     → models.py
```

## Essential Patterns

### 1. News Data Caching (Hourly)
```python
# data/news_data.py
def get_bitcoin_news():
    if cached := get_cached_news_from_db():  # Last hour
        return cached
    news = fetch_from_serpapi()
    save_news_to_db(news)
    return news
```

### 2. Trading Decisions
```python
# analysis/ai_analysis.py
def make_trading_decision():
    market_data = get_market_data()
    news = get_bitcoin_news()
    indicators = calculate_technical_indicators()
    return ai_trading_decision_with_indicators(
        market_data, news, indicators
    )
```

### 3. Background Services
- Dashboard: Streamlit on port 8501
- Scheduler: Runs hourly news updates
- Both run as detached processes via `_start_detached_process()`

## Quick Start

1. Configure:
   ```
   .env:                 # API keys (Upbit, SerpAPI)
   config/settings.py:   # Trading parameters
   database/connection.py: # MySQL settings
   ```

2. Run:
   ```bash
   python main.py --mode vision --interval 600  # Full system
   python main.py --mode indicators  # No vision
   ```

3. Monitor:
   - http://localhost:8501 for dashboard
   - `logs/` for detailed logs
   - MySQL DB for trade history

## Common Tasks

1. Add Technical Indicator:
   - Add to `analysis/technical_indicators.py`
   - Update `create_market_analysis_data()`
   - Modify AI logic in `ai_analysis.py`

2. Modify Trading Rules:
   - Edit `ai_trading_decision_with_indicators()`
   - Test with `test_trading.py`

3. Debug Vision Analysis:
   - Check `images/` for screenshots
   - Use `test_vision_analysis.py`
