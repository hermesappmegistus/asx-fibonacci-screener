# Configuration file for ASX Fibonacci Screener
import os
from dotenv import load_dotenv

load_dotenv()

# ASX Configuration
ASX_SUFFIX = '.AX'  # ASX stocks use .AX suffix on Yahoo Finance

# Fibonacci Retracement Level (78.6%)
FIB_LEVEL = 0.786

# Analysis Configuration
LOOKBACK_DAYS = 30  # Days to lookback for swing high/low
RECENT_DAYS = 3     # Check if bounce occurred in last 3 days
BOUNCE_THRESHOLD = 0.02  # 2% bounce threshold from support level

# API Configuration
ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY', '')

# Output Configuration
OUTPUT_FILE = 'screener_results.csv'
LOG_FILE = 'screener.log'
