# Performance Tracker Feature

## Overview
The Performance Tracker allows you to monitor your investment performance over time using real-time data from financial APIs.

## Features

### 📊 Portfolio Overview
- Real-time portfolio metrics (total invested, current value, returns)
- Interactive visualizations (pie charts, bar charts)
- Comprehensive performance table
- Best/worst performer identification

### 🔍 Individual Investment Analysis
- Historical price charts for each investment
- Entry point visualization
- Detailed performance metrics
- Price change tracking since entry

### 🔬 Detailed Analytics
- Portfolio risk analysis (volatility, concentration)
- Performance by holding period
- Investment type analysis
- Win rate calculations

## Data Sources

### Cryptocurrency Data
- **API**: CoinGecko API (free tier)
- **Coverage**: Bitcoin, Ethereum, Litecoin, Dogecoin, Cardano, Solana, and more
- **Data**: Historical prices, current market data

### Stock Data
- **API**: Yahoo Finance via yfinance library
- **Coverage**: All major stocks and ETFs
- **Data**: Historical prices, current market data

## Entry Date Feature

### Manual Entry Date Selection
When adding investments, you can now specify:
- **Entry Date**: The actual date you made the investment
- **Entry Price**: The price you paid per share/unit
- **Total Amount**: Your total investment

### Why Entry Date Matters
1. **Accurate Performance Calculation**: Calculates returns from your actual purchase date
2. **Time-Based Analytics**: Enables holding period analysis
3. **Annualized Returns**: Provides meaningful annualized return calculations
4. **Historical Context**: Shows how your investment performed in market context

### Default Behavior
- Entry date defaults to today's date
- Cannot select future dates
- Can select any past date up to today

## Rate Limiting & Caching

### API Rate Limits
- CoinGecko: 1.1 second delay between requests
- Yahoo Finance: No explicit rate limiting applied
- Automatic retry logic for failed requests

### Caching Strategy
- Portfolio performance data cached for 5 minutes
- Reduces API calls while keeping data reasonably fresh
- Manual refresh option available

## Error Handling

### Graceful Degradation
- If real-time data unavailable, uses entry price as current price
- Continues processing other investments if one fails
- Clear error messages for debugging

### Fallback Strategies
1. Try primary data source (CoinGecko/Yahoo Finance)
2. If historical data unavailable, use current price only
3. If all APIs fail, show entry data with 0% change

## Usage Tips

### Best Practices
1. **Accurate Entry Dates**: Use the actual purchase date for best results
2. **Regular Updates**: Refresh data periodically for latest prices
3. **Portfolio Diversification**: Monitor concentration risk in analytics
4. **Time Horizon**: Use holding period analysis for investment strategy

### Troubleshooting
- If data isn't loading, check internet connection
- Try refreshing data if prices seem outdated
- Verify investment names match standard formats (e.g., "Bitcoin" not "BTC")

## Supported Investments

### Cryptocurrencies
- Bitcoin, Ethereum, Litecoin, Dogecoin
- Cardano, Solana, Chainlink, Polkadot
- Custom crypto names supported

### Stocks
- Apple (AAPL), Microsoft (MSFT), Google (GOOGL)
- Tesla (TSLA), Amazon (AMZN), Meta (META)
- Custom stock symbols supported
- ETFs (SPY, QQQ, VTI, VOO)

### Adding New Assets
The system includes smart name-to-symbol mapping and can handle custom entries for assets not in the predefined lists.
