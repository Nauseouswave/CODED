# Portfolio App - Modular Structure

This portfolio tracking application has been refactored into a clean, modular structure for better maintainability and understanding.

## Project Structure

```
uniCodePython/
├── main.py                    # Main Streamlit application
├── portfolio.py              # Original monolithic file (kept for reference)
├── data/
│   ├── __init__.py
│   └── constants.py          # Stock and crypto symbol mappings
├── utils/
│   ├── __init__.py
│   ├── price_fetcher.py      # Price fetching logic (Yahoo Finance, CoinGecko)
│   ├── storage.py            # Data persistence utilities
│   └── analytics.py          # Portfolio calculations and metrics
├── components/
│   ├── __init__.py
│   └── ui_components.py      # Streamlit UI components
└── README.md                 # This file
```

## Module Descriptions

### `main.py`
The main entry point for the Streamlit application. Orchestrates all components and handles the overall app flow.

### `data/constants.py`
Contains static data like popular stock and cryptocurrency mappings used throughout the application.

### `utils/price_fetcher.py`
Handles all price fetching functionality:
- Stock prices via Yahoo Finance (multiple fallback methods)
- Cryptocurrency prices via CoinGecko API
- Symbol resolution and price lookup logic

### `utils/storage.py`
Manages data persistence using browser localStorage:
- Save portfolio data to URL parameters
- Load portfolio data on app startup

### `utils/analytics.py`
Portfolio analysis and visualization:
- Performance calculations (P&L, percentages)
- Portfolio metrics aggregation
- Chart generation (pie charts, etc.)

### `components/ui_components.py`
Streamlit UI components:
- Investment input forms
- Performance tables
- Edit forms
- Portfolio summaries

## Running the Application

To run the modular version:

```bash
streamlit run main.py
```

To run the original version:

```bash
streamlit run portfolio.py
```

## Benefits of This Structure

1. **Separation of Concerns**: Each module has a specific responsibility
2. **Easier Testing**: Individual components can be tested in isolation
3. **Better Maintainability**: Changes to one area don't affect others
4. **Code Reusability**: Components can be reused across different parts of the app
5. **Cleaner Code**: Smaller, focused files are easier to understand and modify

## Next Steps

- Add unit tests for each module
- Implement error handling improvements
- Add configuration management
- Consider adding a database backend for persistence
