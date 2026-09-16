# ASX Fibonacci Screener

A Python screener that identifies ASX stocks hitting the 78.6% Fibonacci retracement support level and bouncing or holding within the last 3 days.

## Features

- ✅ Fetches real ASX stock data via Yahoo Finance
- ✅ Calculates Fibonacci retracement levels (78.6%)
- ✅ Identifies recent bounces from support levels
- ✅ Supports screening single stocks, multiple stocks, or all major ASX stocks
- ✅ Generates CSV reports with detailed metrics
- ✅ Comprehensive logging

## Requirements

- Python 3.7+
- See `requirements.txt` for dependencies

## Installation

1. Clone the repository:
```bash
git clone https://github.com/hermesappmegistus/asx-fibonacci-screener.git
cd asx-fibonacci-screener
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) Configure Alpha Vantage API:
```bash
cp .env.example .env
# Edit .env and add your Alpha Vantage API key
```

## Usage

### Screen default top ASX stocks:
```bash
python asx_screener.py
```

### Screen specific stocks:
```bash
python asx_screener.py --stocks CBA,BHP,NAB,WBC,TLS
```

### Screen all major ASX stocks (takes longer):
```bash
python asx_screener.py --all-asx
```

## Output

Results are saved to `screener_results.csv` and displayed in the console.

**Output columns:**
- `ticker`: Stock symbol
- `swing_high`: Highest price in lookback period
- `swing_low`: Lowest price in lookback period
- `fib_78_6_level`: The 78.6% retracement level
- `current_price`: Current/latest price
- `lowest_price_3d`: Lowest price in last 3 days
- `bounce_distance`: Price distance from support level
- `bounce_percentage`: Percentage bounce from support
- `timestamp`: When the scan was run

## Configuration

Edit `config.py` to customize:

- `FIB_LEVEL`: Fibonacci level (default: 0.786 = 78.6%)
- `LOOKBACK_DAYS`: Days to analyze for swing high/low (default: 30)
- `RECENT_DAYS`: Days to check for recent bounce (default: 3)
- `BOUNCE_THRESHOLD`: Minimum bounce % (default: 0.02 = 2%)

## How It Works

1. **Fetch Data**: Downloads historical price data for each stock
2. **Find Swing High/Low**: Identifies the highest and lowest prices in the lookback period
3. **Calculate 78.6% Level**: Computes the Fibonacci retracement at 78.6%
4. **Check Recent Bounce**: Verifies if price touched the level in the last 3 days and bounced
5. **Report Results**: Displays and saves stocks that match criteria

## Data Source

This screener uses **Yahoo Finance** via the `yfinance` library, which provides comprehensive ASX data.

- ASX stocks use the `.AX` suffix in Yahoo Finance (e.g., `CBA.AX` for Commonwealth Bank)
- Data is free and updated daily

## Logging

Logs are saved to `screener.log` and printed to console.

## Limitations & Notes

- The screener requires internet connectivity to fetch data
- Yahoo Finance data may have slight delays
- Past performance does not guarantee future results
- Use this as a screening tool only; not financial advice
- Always verify signals with your own analysis

## Future Enhancements

- [ ] Add more Fibonacci levels (23.6%, 38.2%, 50%, 61.8%)
- [ ] Add email/webhook notifications for matches
- [ ] Add RSI, MACD confirmation filters
- [ ] Real-time monitoring with schedule
- [ ] Support for multiple timeframes
- [ ] Integration with MT5 via API

## License

MIT License - see LICENSE file

## Disclaimer

This tool is for educational and research purposes. Always conduct your own due diligence and consult a financial advisor before trading.
