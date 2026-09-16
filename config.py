# Configuration file for ASX Fibonacci Screener
import os
from dotenv import load_dotenv

load_dotenv()

# ASX Configuration
ASX_SUFFIX = '.AX'  # ASX stocks use .AX suffix on Yahoo Finance

# Fibonacci Retracement Level (78.6%)
FIB_LEVEL = 0.786

# Swing Analysis Configuration
LOOKBACK_DAYS = 120  # Days to analyze for swing identification
SWING_LENGTH = 5     # Number of candles to identify swing highs/lows (5-day comparison)
RECENT_DAYS = 3      # Check if bounce occurred in last 3 days
BOUNCE_THRESHOLD = 0.01  # 1% minimum bounce threshold from support level

# API Configuration
ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY', '')

# Output Configuration
OUTPUT_FILE = 'screener_results.csv'
LOG_FILE = 'screener.log'
