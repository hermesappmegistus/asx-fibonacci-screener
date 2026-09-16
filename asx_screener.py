#!/usr/bin/env python3
"""
ASX Fibonacci Retracement Screener

This script identifies ASX stocks that have recently (within last 3 days)
hit the 78.6% Fibonacci retracement support level (based on swing highs/lows)
and bounced or held.

Usage:
    python asx_screener.py
    python asx_screener.py --stocks CBA,BHP,NAB  # Specific stocks
    python asx_screener.py --all-asx              # All ASX stocks (slower)
"""

import yfinance as yf
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from config import (
    ASX_SUFFIX,
    FIB_LEVEL,
    LOOKBACK_DAYS,
    SWING_LENGTH,
    RECENT_DAYS,
    BOUNCE_THRESHOLD,
    OUTPUT_FILE,
    LOG_FILE
)
import argparse
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FibonacciScreener:
    """Screener for identifying Fibonacci retracement bounces based on swing highs/lows"""
    
    def __init__(self):
        self.results = []
        self.failed_stocks = []
    
    def fetch_stock_data(self, ticker, days=LOOKBACK_DAYS):
        """
        Fetch historical price data for a stock
        
        Args:
            ticker: Stock ticker (without .AX suffix)
            days: Number of days of historical data to fetch
            
        Returns:
            DataFrame with OHLC data or None if failed
        """
        try:
            symbol = f"{ticker}{ASX_SUFFIX}"
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            data = yf.download(symbol, start=start_date, end=end_date, progress=False)
            
            if data.empty:
                logger.warning(f"No data fetched for {ticker}")
                return None
            
            return data
        
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {str(e)}")
            self.failed_stocks.append(ticker)
            return None
    
    def identify_swing_highs_lows(self, data, length=SWING_LENGTH):
        """
        Identify swing highs and lows in the price data
        
        A swing high is a candle where the high is higher than the previous 'length' candles
        and higher than the next 'length' candles.
        A swing low is a candle where the low is lower than the previous 'length' candles
        and lower than the next 'length' candles.
        
        Args:
            data: DataFrame with OHLC data
            length: Number of candles to compare (default 5)
            
        Returns:
            Tuple of (swing_highs, swing_lows) - lists of indices and values
        """
        if data is None or len(data) < (length * 2 + 1):
            return None, None
        
        try:
            swing_highs = []
            swing_lows = []
            
            highs = data['High'].values
            lows = data['Low'].values
            
            # Look for swing highs and lows
            for i in range(length, len(data) - length):
                # Check for swing high
                if highs[i] == max(highs[i-length:i+length+1]):
                    swing_highs.append((i, highs[i]))
                
                # Check for swing low
                if lows[i] == min(lows[i-length:i+length+1]):
                    swing_lows.append((i, lows[i]))
            
            return swing_highs, swing_lows
        
        except Exception as e:
            logger.error(f"Error identifying swings: {str(e)}")
            return None, None
    
    def get_most_recent_swing_high_low(self, data):
        """
        Get the most recent significant swing high and low
        
        Args:
            data: DataFrame with OHLC data
            
        Returns:
            Dictionary with most recent swing high and low, or None
        """
        swing_highs, swing_lows = self.identify_swing_highs_lows(data, SWING_LENGTH)
        
        if not swing_highs or not swing_lows:
            return None
        
        try:
            # Get the most recent swing high and low
            most_recent_high = swing_highs[-1]
            most_recent_low = swing_lows[-1]
            
            # Ensure we have a high and low to work with
            swing_high_price = most_recent_high[1]
            swing_low_price = most_recent_low[1]
            
            if swing_high_price <= swing_low_price:
                # If the most recent high is lower than low, find appropriate pair
                swing_high_price = max([h[1] for h in swing_highs])
                swing_low_price = min([l[1] for l in swing_lows])
            
            return {
                'swing_high': swing_high_price,
                'swing_low': swing_low_price,
                'range': swing_high_price - swing_low_price
            }
        
        except Exception as e:
            logger.error(f"Error getting recent swing: {str(e)}")
            return None
    
    def calculate_fibonacci_from_swings(self, swing_info):
        """
        Calculate Fibonacci retracement level from swing high/low
        
        Args:
            swing_info: Dictionary with swing_high and swing_low
            
        Returns:
            Dictionary with 78.6% retracement level or None
        """
        if swing_info is None:
            return None
        
        try:
            high = swing_info['swing_high']
            low = swing_info['swing_low']
            
            if high == low:
                return None
            
            # Calculate 78.6% retracement level (from high down to low)
            fib_78_6 = high - (high - low) * FIB_LEVEL
            
            return {
                'swing_high': high,
                'swing_low': low,
                'fib_78_6': fib_78_6,
                'range': high - low
            }
        
        except Exception as e:
            logger.error(f"Error calculating Fibonacci levels: {str(e)}")
            return None
    
    def check_recent_bounce(self, data, fib_level):
        """
        Check if stock bounced from 78.6% level in last 3 days
        
        Args:
            data: DataFrame with OHLC data
            fib_level: The 78.6% Fibonacci level
            
        Returns:
            Dictionary with bounce details or None
        """
        if data is None or len(data) < RECENT_DAYS:
            return None
        
        try:
            # Get recent data (last N days)
            recent_data = data.tail(RECENT_DAYS)
            
            # Check if price touched or went below fib level
            touched_support = recent_data['Low'].min() <= fib_level
            
            if not touched_support:
                return None
            
            # Check if price bounced (closed above support)
            current_price = data['Close'].iloc[-1]
            bounce_distance = current_price - fib_level
            bounce_percentage = (bounce_distance / fib_level) * 100 if fib_level > 0 else 0
            
            # Check if bounce is significant
            if bounce_percentage >= BOUNCE_THRESHOLD * 100:
                return {
                    'touched_support': True,
                    'bounce_distance': bounce_distance,
                    'bounce_percentage': bounce_percentage,
                    'current_price': current_price,
                    'lowest_price_recent': recent_data['Low'].min()
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Error checking bounce: {str(e)}")
            return None
    
    def screen_stock(self, ticker):
        """
        Screen a single stock for Fibonacci bounce based on swing highs/lows
        
        Args:
            ticker: Stock ticker (without .AX suffix)
            
        Returns:
            Dictionary with results or None
        """
        logger.info(f"Screening {ticker}...")
        
        # Fetch data
        data = self.fetch_stock_data(ticker)
        if data is None:
            return None
        
        # Get most recent swing high and low
        swing_info = self.get_most_recent_swing_high_low(data)
        if swing_info is None:
            logger.debug(f"{ticker}: Could not identify swing highs/lows")
            return None
        
        # Calculate Fibonacci levels from swings
        fib_info = self.calculate_fibonacci_from_swings(swing_info)
        if fib_info is None:
            return None
        
        # Check for recent bounce
        bounce_info = self.check_recent_bounce(data, fib_info['fib_78_6'])
        if bounce_info is None:
            return None
        
        # Compile results
        result = {
            'ticker': ticker,
            'swing_high': round(fib_info['swing_high'], 2),
            'swing_low': round(fib_info['swing_low'], 2),
            'fib_78_6_level': round(fib_info['fib_78_6'], 2),
            'current_price': round(bounce_info['current_price'], 2),
            'lowest_price_3d': round(bounce_info['lowest_price_recent'], 2),
            'bounce_distance': round(bounce_info['bounce_distance'], 2),
            'bounce_percentage': round(bounce_info['bounce_percentage'], 2),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        logger.info(f"✓ {ticker} FOUND: Bounced {result['bounce_percentage']:.2f}% from 78.6 level (swing-based)")
        return result
    
    def screen_multiple(self, tickers):
        """
        Screen multiple stocks
        
        Args:
            tickers: List of stock tickers
        """
        for ticker in tickers:
            try:
                result = self.screen_stock(ticker)
                if result:
                    self.results.append(result)
            except Exception as e:
                logger.error(f"Unexpected error screening {ticker}: {str(e)}")
                self.failed_stocks.append(ticker)
    
    def save_results(self):
        """
        Save results to CSV file
        """
        if not self.results:
            logger.info("No results to save")
            return
        
        df = pd.DataFrame(self.results)
        df = df.sort_values('bounce_percentage', ascending=False)
        df.to_csv(OUTPUT_FILE, index=False)
        logger.info(f"Results saved to {OUTPUT_FILE}")
    
    def print_results(self):
        """
        Print results in a formatted table
        """
        if not self.results:
            logger.info("No stocks matched the criteria")
            return
        
        df = pd.DataFrame(self.results)
        df = df.sort_values('bounce_percentage', ascending=False)
        
        print("\n" + "="*120)
        print(f"ASX FIBONACCI RETRACEMENT SCREENER RESULTS (SWING-BASED) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Criteria: 78.6% Fib Level from Swing High/Low, Bounce within last {RECENT_DAYS} days")
        print("="*120 + "\n")
        
        print(df.to_string(index=False))
        print(f"\nTotal matches: {len(df)}")
        print(f"Failed to fetch: {len(self.failed_stocks)}")
        if self.failed_stocks:
            print(f"Failed stocks: {', '.join(self.failed_stocks)}")


def get_top_asx_stocks():
    """
    Return a list of major ASX stocks to screen
    Includes top 200 by market cap
    """
    # Top ASX stocks (can be expanded)
    top_stocks = [
        'CBA', 'BHP', 'NAB', 'WBC', 'TLS', 'ANZ', 'MQG', 'CSL', 'WES', 'MCD',
        'AMP', 'APA', 'ASX', 'AWC', 'BEN', 'BOQ', 'CAR', 'CCL', 'CIM', 'COL',
        'CPU', 'DHG', 'EZJ', 'FMG', 'GUD', 'IAG', 'IFL', 'ILC', 'JHG', 'KMD',
        'LLC', 'MNW', 'MPL', 'NWH', 'ORA', 'ORE', 'PDN', 'PMV', 'QAN', 'REC',
        'REX', 'RMD', 'RMS', 'SCG', 'SHL', 'STO', 'SUN', 'TAH', 'TCL', 'TYE',
        'VAS', 'VOC', 'WBC', 'WED', 'WES', 'WFE', 'WOR', 'XRO', 'YOW', 'Z1P',
        # Add more as needed
    ]
    return list(set(top_stocks))  # Remove duplicates


def main():
    """
    Main function with argument parsing
    """
    parser = argparse.ArgumentParser(
        description='ASX Fibonacci Retracement Screener (Swing-Based)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python asx_screener.py                    # Screen default top stocks
  python asx_screener.py --stocks CBA,BHP  # Screen specific stocks
  python asx_screener.py --all-asx          # Screen many ASX stocks (slow)
        """
    )
    
    parser.add_argument(
        '--stocks',
        type=str,
        help='Comma-separated list of stock tickers to screen (e.g., CBA,BHP,NAB)'
    )
    parser.add_argument(
        '--all-asx',
        action='store_true',
        help='Screen all major ASX stocks (slower)'
    )
    
    args = parser.parse_args()
    
    screener = FibonacciScreener()
    
    # Determine which stocks to screen
    if args.stocks:
        tickers = [t.strip().upper() for t in args.stocks.split(',')]
    elif args.all_asx:
        logger.info("Fetching all major ASX stocks...")
        tickers = get_top_asx_stocks()
    else:
        tickers = get_top_asx_stocks()
    
    logger.info(f"Starting scan of {len(tickers)} stocks (swing-based analysis)...")
    screener.screen_multiple(tickers)
    
    # Display and save results
    screener.print_results()
    screener.save_results()
    
    return 0 if screener.results else 1


if __name__ == '__main__':
    sys.exit(main())
