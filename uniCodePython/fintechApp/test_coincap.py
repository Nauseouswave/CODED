#!/usr/bin/env python3

from utils.price_fetcher import get_crypto_price_simple, get_crypto_chart_data
import time

print('Testing CoinCap API...')
print()

# Test price fetching
cryptos = ['bitcoin', 'ethereum', 'solana', 'usd-coin', 'tether']
for crypto in cryptos:
    price = get_crypto_price_simple(crypto)
    if price:
        print(f'{crypto}: ${price:,.2f}')
    else:
        print(f'{crypto}: Failed to fetch')
    time.sleep(0.5)

print()
print('Testing chart data...')
chart_data = get_crypto_chart_data('bitcoin', 7)
if chart_data is not None:
    print(f'Bitcoin chart data: {len(chart_data)} points')
    print(chart_data.head())
else:
    print('Chart data failed')
