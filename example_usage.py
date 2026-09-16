#!/usr/bin/env python3
"""
Example usage of the ASX Fibonacci Screener

This script demonstrates how to use the screener programmatically
in your own applications.
"""

from asx_screener import FibonacciScreener
import logging

logging.basicConfig(level=logging.INFO)

# Example 1: Screen a single stock
print("\n" + "="*50)
print("Example 1: Screen a single stock")
print("="*50)

screener = FibonacciScreener()
result = screener.screen_stock('CBA')

if result:
    print(f"\nFound match!")
    print(f"Ticker: {result['ticker']}")
    print(f"78.6% Fib Level: ${result['fib_78_6_level']}")
    print(f"Current Price: ${result['current_price']}")
    print(f"Bounce: {result['bounce_percentage']:.2f}%")
else:
    print("No match found for CBA")


# Example 2: Screen multiple specific stocks
print("\n" + "="*50)
print("Example 2: Screen multiple stocks")
print("="*50)

screener2 = FibonacciScreener()
tickers = ['CBA', 'BHP', 'NAB', 'WBC', 'TLS']
screener2.screen_multiple(tickers)
screener2.print_results()
screener2.save_results()


# Example 3: Access results programmatically
print("\n" + "="*50)
print("Example 3: Work with results programmatically")
print("="*50)

if screener2.results:
    print(f"Found {len(screener2.results)} stocks matching criteria:\n")
    
    for result in screener2.results:
        print(f"{result['ticker']:6} - Bounce: {result['bounce_percentage']:6.2f}% | "
              f"Price: ${result['current_price']:8.2f} | "
              f"Support: ${result['fib_78_6_level']:8.2f}")
    
    # Get the best bounce
    best = max(screener2.results, key=lambda x: x['bounce_percentage'])
    print(f"\nBest bounce: {best['ticker']} with {best['bounce_percentage']:.2f}%")
