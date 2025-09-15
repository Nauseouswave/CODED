# FinSight - AI-Powered Portfolio Tracker

A comprehensive AI-powered portfolio tracking application built with Streamlit that allows users to monitor their investment performance in real-time with intelligent insights.

## Features

✨ **Investment Tracking**
- Add stocks, bonds, real estate, and cryptocurrency investments
- Input total amount invested and entry price (automatically calculates shares)
- Live price fetching for stocks (Yahoo Finance) and crypto (Binance API)
- Real-time profit/loss calculations

📊 **Portfolio Analytics**
- Performance tracking with P&L metrics
- Portfolio distribution pie charts
- Risk level categorization
- Summary metrics and insights

💾 **Data Persistence**
- Browser-based storage using URL parameters
- No database required - data persists across sessions

🎨 **Modern UI**
- Clean, intuitive Streamlit interface
- Live price previews
- Interactive editing capabilities
- Responsive design

## Project Structure

```
fintechApp/
├── main.py                    # Main application entry point
├── data/
│   ├── __init__.py
│   └── constants.py          # Stock and crypto symbol mappings
├── utils/
│   ├── __init__.py
│   ├── price_fetcher.py      # Price fetching (Yahoo Finance, CoinGecko)
│   ├── storage.py            # Data persistence utilities
│   └── analytics.py          # Portfolio calculations and metrics
├── components/
│   ├── __init__.py
│   └── ui_components.py      # Streamlit UI components
├── logo.png                  # App logo
├── kfhLogo.png              # KFH logo
└── README.md                 # This file
```

## Installation

1. **Clone or download this directory**
2. **Install required packages:**
   ```bash
   pip install streamlit pandas matplotlib yfinance requests
   ```

## Usage

Run the application:
```bash
streamlit run main.py
```

### Adding Investments

1. **Select Investment Type**: Choose from Stocks, Bonds, Real Estate, or Cryptocurrency
2. **Choose Investment**: Select from popular options or enter custom details
3. **Enter Details**: 
   - Entry price per share/unit
   - Total amount invested (shares calculated automatically)
   - Risk level
4. **Live Price Preview**: For supported assets, see current market price
5. **Add to Portfolio**: Click "Add Investment" to save

### Portfolio Management

- **Edit Investments**: Click the pencil icon to modify existing investments
- **Delete Investments**: Click the trash icon to remove investments
- **View Performance**: See real-time P&L calculations and percentages
- **Portfolio Summary**: View total metrics and distribution charts

## Supported Assets

### Stocks (via Yahoo Finance)
- Major US stocks (AAPL, MSFT, GOOGL, AMZN, TSLA, etc.)
- ETFs (SPY, QQQ, etc.)
- Custom stock symbols

### Cryptocurrencies (via CoinGecko)
- Major cryptocurrencies (BTC, ETH, BNB, XRP, SOL, etc.)
- Real-time price updates
- Custom crypto entries

### Other Assets
- Bonds, Real Estate, and other investment types
- Manual price entry (no live price fetching)

## Key Changes in This Version

🔄 **Input Method Change**: Instead of entering number of shares, users now enter:
- Total amount invested
- Entry price per share/unit
- Shares are automatically calculated

This makes it more intuitive for users who know how much they invested rather than the exact number of shares.

## Technical Features

- **Modular Architecture**: Clean separation of concerns across multiple files
- **Caching**: Efficient price fetching with 5-minute cache
- **Error Handling**: Robust fallback mechanisms for price fetching
- **Responsive Design**: Works well on different screen sizes
- **Real-time Updates**: Live price previews and calculations

## Future Enhancements

- Historical performance charts
- Portfolio rebalancing suggestions
- Export/import functionality
- Advanced analytics and reporting
- Mobile app version

## Contributing

This app is part of a learning project. Feel free to suggest improvements or report issues!

## License

Educational use - part of the CODED programming course.
