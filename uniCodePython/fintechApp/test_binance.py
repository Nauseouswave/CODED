#!/usr/bin/env python3

from utils.price_fetcher import get_crypto_price_simple
import time

print('Testing Binance API...')
print()

# Test multiple calls to see if rate limiting works
cryptos = ['bitcoin', 'ethereum', 'solana']
for crypto in cryptos:
    print(f'Fetching {crypto}...')
    price = get_crypto_price_simple(crypto)
    if price:
        print(f'{crypto}: ${price:.2f}')
    else:
        print(f'{crypto}: Failed to fetch')
    print()
    time.sleep(1)
