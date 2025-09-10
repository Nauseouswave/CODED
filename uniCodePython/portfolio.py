import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import base64
import requests
from datetime import datetime
import yfinance as yf

# Fintech Portfolio App: Track and visualize your investments

# Popular stocks and crypto data
POPULAR_STOCKS = {
    "Apple Inc. (AAPL)": "AAPL",
    "Microsoft Corp. (MSFT)": "MSFT", 
    "Alphabet Inc. (GOOGL)": "GOOGL",
    "Amazon.com Inc. (AMZN)": "AMZN",
    "Tesla Inc. (TSLA)": "TSLA",
    "Meta Platforms Inc. (META)": "META",
    "NVIDIA Corp. (NVDA)": "NVDA",
    "Netflix Inc. (NFLX)": "NFLX",
    "Berkshire Hathaway (BRK-B)": "BRK-B",
    "JPMorgan Chase & Co. (JPM)": "JPM",
    "Johnson & Johnson (JNJ)": "JNJ",
    "Visa Inc. (V)": "V",
    "Procter & Gamble Co. (PG)": "PG",
    "UnitedHealth Group Inc. (UNH)": "UNH",
    "Mastercard Inc. (MA)": "MA",
    "Home Depot Inc. (HD)": "HD",
    "Coca-Cola Co. (KO)": "KO",
    "Pfizer Inc. (PFE)": "PFE",
    "Walt Disney Co. (DIS)": "DIS",
    "Intel Corp. (INTC)": "INTC",
    "Salesforce Inc. (CRM)": "CRM",
    "Adobe Inc. (ADBE)": "ADBE",
    "Cisco Systems Inc. (CSCO)": "CSCO",
    "Verizon Communications (VZ)": "VZ",
    "Walmart Inc. (WMT)": "WMT",
    "S&P 500 ETF (SPY)": "SPY",
    "QQQ Nasdaq ETF (QQQ)": "QQQ",
    "SPDR S&P 500 ETF Trust (SPUS)": "SPUS"
}

POPULAR_CRYPTO = {
    "Bitcoin (BTC)": "bitcoin",
    "Ethereum (ETH)": "ethereum", 
    "Binance Coin (BNB)": "binancecoin",
    "XRP (XRP)": "ripple",
    "Solana (SOL)": "solana",
    "Cardano (ADA)": "cardano",
    "Dogecoin (DOGE)": "dogecoin",
    "Avalanche (AVAX)": "avalanche-2",
    "Polkadot (DOT)": "polkadot",
    "Polygon (MATIC)": "matic-network",
    "Chainlink (LINK)": "chainlink",
    "Litecoin (LTC)": "litecoin",
    "Bitcoin Cash (BCH)": "bitcoin-cash",
    "Uniswap (UNI)": "uniswap",
    "Stellar (XLM)": "stellar",
    "VeChain (VET)": "vechain",
    "Filecoin (FIL)": "filecoin",
    "TRON (TRX)": "tron",
    "Ethereum Classic (ETC)": "ethereum-classic",
    "Monero (XMR)": "monero"
}

# Price fetching functions
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_price(symbol):
    """Get current stock price with multiple fallback methods"""
    
    # Method 1: yfinance library (most reliable)
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if 'currentPrice' in info:
            return float(info['currentPrice'])
        elif 'regularMarketPrice' in info:
            return float(info['regularMarketPrice'])
        elif 'previousClose' in info:
            return float(info['previousClose'])
    except Exception as e:
        print(f"yfinance failed: {e}")
    
    # Method 2: Yahoo Finance v7 API
    try:
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if 'quoteResponse' in data and data['quoteResponse']['result']:
            result = data['quoteResponse']['result'][0]
            if 'regularMarketPrice' in result:
                return float(result['regularMarketPrice'])
    except Exception as e:
        print(f"Yahoo v7 API failed: {e}")
    
    # Method 3: Yahoo Finance v8 API
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if 'chart' in data and data['chart']['result']:
            price = data['chart']['result'][0]['meta']['regularMarketPrice']
            return float(price)
    except Exception as e:
        print(f"Yahoo v8 API failed: {e}")
    
    return None

@st.cache_data(ttl=300)  # Cache for 5 minutes  
def get_crypto_price(symbol):
    """Get current crypto price from CoinGecko API"""
    try:
        # CoinGecko API (free, no API key needed)
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        
        if symbol in data and 'usd' in data[symbol]:
            return float(data[symbol]['usd'])
    except:
        pass
    return None

def get_symbol_from_selection(investment_name, investment_type):
    """Extract the API symbol from the selected investment"""
    if investment_type == "Stocks":
        return POPULAR_STOCKS.get(investment_name)
    elif investment_type == "Cryptocurrency":
        return POPULAR_CRYPTO.get(investment_name)
    return None

def get_current_price(investment_name, investment_type):
    """Get current price based on investment type and name"""
    # First try to get symbol from our predefined lists
    symbol = get_symbol_from_selection(investment_name, investment_type)
    
    if symbol:
        if investment_type == "Cryptocurrency":
            return get_crypto_price(symbol)
        elif investment_type == "Stocks":
            return get_stock_price(symbol)
    
    # Fallback to old logic for custom entries
    if investment_type == "Cryptocurrency":
        name_lower = investment_name.lower().replace(' ', '')
        crypto_fallback = {
            'bitcoin': 'bitcoin', 'btc': 'bitcoin',
            'ethereum': 'ethereum', 'eth': 'ethereum',
            'dogecoin': 'dogecoin', 'doge': 'dogecoin',
            'cardano': 'cardano', 'ada': 'cardano'
        }
        
        for key, value in crypto_fallback.items():
            if key in name_lower:
                return get_crypto_price(value)
                
    elif investment_type == "Stocks":
        # Try the name as symbol directly if it's short
        clean_name = investment_name.upper().replace('STOCK', '').replace('SHARES', '').strip()
        if len(clean_name) <= 5:
            return get_stock_price(clean_name)
    
    return None

# Display logo at the top
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logo.png", width=300)

st.title("Fintech Portfolio App")
st.header("Investment Portfolio Tracker")
st.subheader("Monitor your investments and portfolio spread.")
st.write("Welcome to the Fintech Portfolio App! Here you can track and visualize your investments effortlessly.")

# Persistence functions using browser localStorage
def save_to_storage(investments):
    """Save investments to browser localStorage"""
    investments_json = json.dumps(investments)
    # Encode to base64 to handle special characters
    encoded_data = base64.b64encode(investments_json.encode()).decode()
    st.query_params["data"] = encoded_data

def load_from_storage():
    """Load investments from browser localStorage"""
    try:
        encoded_data = st.query_params.get("data", "")
        if encoded_data:
            decoded_data = base64.b64decode(encoded_data).decode()
            return json.loads(decoded_data)
    except:
        pass
    return []

# Initialize session state for storing investments
if 'investments' not in st.session_state:
    # Try to load from storage first
    stored_investments = load_from_storage()
    st.session_state.investments = stored_investments

st.divider()

# Input section
st.subheader("Add New Investment")
col1, col2 = st.columns(2)

with col1:
    investment_type = st.selectbox("Select Investment Type:", ["Stocks", "Bonds", "Real Estate", "Cryptocurrency"])
    
    # Show different options based on investment type
    if investment_type == "Stocks":
        st.write("**Select from Popular Stocks:**")
        investment_name = st.selectbox(
            "Choose a stock:",
            [""] + list(POPULAR_STOCKS.keys()) + ["Custom Entry"],
            key="stock_select"
        )
        
        # If custom entry is selected, show text input
        if investment_name == "Custom Entry":
            investment_name = st.text_input("Enter custom stock symbol (e.g., AAPL):")
        elif investment_name == "":
            investment_name = ""
            
    elif investment_type == "Cryptocurrency":
        st.write("**Select from Popular Cryptocurrencies:**")
        investment_name = st.selectbox(
            "Choose a cryptocurrency:",
            [""] + list(POPULAR_CRYPTO.keys()) + ["Custom Entry"],
            key="crypto_select"
        )
        
        # If custom entry is selected, show text input
        if investment_name == "Custom Entry":
            investment_name = st.text_input("Enter custom crypto name:")
        elif investment_name == "":
            investment_name = ""
            
    else:
        # For Bonds, Real Estate, etc. - just use text input
        investment_name = st.text_input("Enter Investment Name:")
    
    entry_price = st.number_input("Enter Entry Price per Share/Unit ($):", min_value=0.0, step=0.01)
    
    # Show live price preview for supported assets
    if investment_name and investment_name not in ["", "Custom Entry"] and investment_type in ["Stocks", "Cryptocurrency"]:
        with st.spinner("Fetching live price..."):
            live_price = get_current_price(investment_name, investment_type)
            if live_price:
                st.success(f"💰 **Live Price**: ${live_price:.2f}")
                if st.button("📋 Use Live Price as Entry Price"):
                    st.session_state[f"entry_price_{investment_type}"] = live_price
                    st.rerun()
            else:
                st.warning("⚠️ Unable to fetch live price")
                # Debug info for troubleshooting
                symbol = get_symbol_from_selection(investment_name, investment_type)
                if symbol:
                    st.info(f"🔍 Trying to fetch: {symbol} ({investment_type})")
                else:
                    st.info(f"🔍 No symbol mapping found for: {investment_name}")
    
with col2:
    shares = st.number_input("Enter Number of Shares/Units:", min_value=0.0, step=0.01)
    risk_level = st.selectbox("Select Risk Level:", ["Low", "Medium", "High"])
    
# Auto-fill entry price if requested
if f"entry_price_{investment_type}" in st.session_state:
    entry_price = st.session_state[f"entry_price_{investment_type}"]
    del st.session_state[f"entry_price_{investment_type}"]

# Calculate total investment amount
if entry_price > 0 and shares > 0:
    total_amount = entry_price * shares
    st.info(f"💵 **Total Investment Amount**: ${total_amount:,.2f}")

st.divider()

# Buttons section
col1, col2 = st.columns(2)
with col1:
    if st.button("Add Investment", type="primary"):
        if investment_name and investment_type and entry_price > 0 and shares > 0:
            total_amount = entry_price * shares
            investment = {
                'name': investment_name,
                'type': investment_type,
                'entry_price': entry_price,
                'shares': shares,
                'amount': total_amount,
                'risk_level': risk_level,
                'date_added': datetime.now().isoformat()
            }
            st.session_state.investments.append(investment)
            # Save to storage whenever we add an investment
            save_to_storage(st.session_state.investments)
            st.success(f"Investment '{investment_name}' of ${total_amount:,.2f} ({shares} shares at ${entry_price}) added successfully!")
            st.balloons()
        else:
            st.error("Please fill in all fields with valid values.")

with col2:
    if st.button("Clear All Investments"):
        st.session_state.investments = []
        # Clear storage when clearing all investments
        save_to_storage([])
        st.success("All investments cleared!")

st.divider()

# Display investments and calculations
if st.session_state.investments:
    st.subheader("Your Investment Portfolio")
    
    # Calculate total portfolio value
    total_value = sum(inv['amount'] for inv in st.session_state.investments)
    
    # Create dataframe for display with edit options
    st.subheader("Edit Investment Amounts")
    
    # Performance tracking section
    st.subheader("📈 Live Performance Tracking")
    
    # Create columns for performance display
    col_names = ["Investment", "Shares", "Entry Price", "Current Price", "Total Value", "P&L", "P&L %", "Actions"]
    
    # Display header
    header_cols = st.columns([1.5, 0.8, 1, 1, 1.2, 1, 0.8, 1])
    for i, header in enumerate(col_names):
        header_cols[i].write(f"**{header}**")
    
    # Display each investment with performance data
    investments_to_remove = []
    total_portfolio_value = 0
    total_invested = 0
    
    for idx, inv in enumerate(st.session_state.investments):
        cols = st.columns([1.5, 0.8, 1, 1, 1.2, 1, 0.8, 1])
        
        # Get current price
        current_price = get_current_price(inv['name'], inv['type'])
        
        # Calculate values
        entry_price = inv.get('entry_price', inv['amount'] / inv.get('shares', 1))
        shares = inv.get('shares', 1)
        invested_amount = entry_price * shares
        
        if current_price:
            current_value = current_price * shares
            pnl = current_value - invested_amount
            pnl_percentage = (pnl / invested_amount) * 100 if invested_amount > 0 else 0
        else:
            current_value = invested_amount
            pnl = 0
            pnl_percentage = 0
        
        total_portfolio_value += current_value
        total_invested += invested_amount
        
        with cols[0]:
            st.write(inv['name'])
        
        with cols[1]:
            st.write(f"{shares:.2f}")
        
        with cols[2]:
            st.write(f"${entry_price:.2f}")
        
        with cols[3]:
            if current_price:
                st.write(f"${current_price:.2f}")
            else:
                st.write("N/A")
        
        with cols[4]:
            st.write(f"${current_value:,.2f}")
        
        with cols[5]:
            if pnl >= 0:
                st.write(f"🟢 ${pnl:,.2f}")
            else:
                st.write(f"🔴 ${pnl:,.2f}")
        
        with cols[6]:
            if pnl_percentage >= 0:
                st.write(f"🟢 {pnl_percentage:.1f}%")
            else:
                st.write(f"🔴 {pnl_percentage:.1f}%")
        
        with cols[7]:
            col_update, col_delete = st.columns(2)
            
            with col_update:
                if st.button("📝", key=f"edit_{idx}", help="Edit investment"):
                    # Set editing flag instead of showing form inline
                    st.session_state[f"editing_{idx}"] = True
                    st.rerun()
            
            with col_delete:
                if st.button("🗑️", key=f"delete_{idx}", help="Delete investment"):
                    investments_to_remove.append(idx)
    
    # Remove investments marked for deletion
    if investments_to_remove:
        for idx in sorted(investments_to_remove, reverse=True):
            removed_inv = st.session_state.investments.pop(idx)
            st.success(f"Deleted {removed_inv['name']}")
        save_to_storage(st.session_state.investments)
        st.rerun()
    
    # Edit form section (full-width, clean layout)
    for idx, inv in enumerate(st.session_state.investments):
        if st.session_state.get(f"editing_{idx}", False):
            st.divider()
            st.subheader(f"✏️ Edit {inv['name']}")
            
            # Get current values
            current_shares = inv.get('shares', 1)
            current_entry = inv.get('entry_price', inv['amount'] / current_shares if current_shares > 0 else 0)
            
            # Create clean edit form with proper width
            edit_col1, edit_col2, edit_col3 = st.columns(3)
            
            with edit_col1:
                new_shares = st.number_input(
                    "Number of Shares/Units:", 
                    value=float(current_shares), 
                    min_value=0.0,
                    step=0.01,
                    key=f"edit_shares_{idx}"
                )
            
            with edit_col2:
                new_entry = st.number_input(
                    "Entry Price per Share/Unit ($):", 
                    value=float(current_entry), 
                    min_value=0.0,
                    step=0.01,
                    key=f"edit_entry_{idx}"
                )
            
            with edit_col3:
                st.write("**New Total Amount:**")
                new_total = new_shares * new_entry
                st.info(f"${new_total:,.2f}")
            
            # Action buttons
            button_col1, button_col2, button_col3 = st.columns([1, 1, 4])
            
            with button_col1:
                if st.button("💾 Save Changes", key=f"save_{idx}", type="primary"):
                    st.session_state.investments[idx]['shares'] = new_shares
                    st.session_state.investments[idx]['entry_price'] = new_entry
                    st.session_state.investments[idx]['amount'] = new_total
                    save_to_storage(st.session_state.investments)
                    st.session_state[f"editing_{idx}"] = False
                    st.success(f"✅ Updated {inv['name']}")
                    st.rerun()
            
            with button_col2:
                if st.button("❌ Cancel", key=f"cancel_{idx}"):
                    st.session_state[f"editing_{idx}"] = False
                    st.rerun()
    
    st.divider()
    
    # Portfolio summary table (read-only view)
    st.subheader("Portfolio Summary Table")
    portfolio_data = []
    for inv in st.session_state.investments:
        percentage = (inv['amount'] / sum(inv['amount'] for inv in st.session_state.investments)) * 100
        portfolio_data.append({
            'Investment Name': inv['name'],
            'Investment Type': inv['type'],
            'Amount ($)': f"${inv['amount']:,.2f}",
            'Percentage (%)': f"{percentage:.1f}%",
            'Risk Level': inv['risk_level']
        })
    
    df = pd.DataFrame(portfolio_data)
    st.dataframe(df, use_container_width=True)
    
    # Enhanced Portfolio Summary with P&L
    st.subheader("📊 Portfolio Summary")
    
    total_pnl = total_portfolio_value - total_invested
    total_pnl_percentage = (total_pnl / total_invested * 100) if total_invested > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Investment", f"${total_invested:,.2f}")
    
    with col2:
        st.metric("Current Value", f"${total_portfolio_value:,.2f}")
    
    with col3:
        pnl_color = "normal" if total_pnl >= 0 else "inverse"
        st.metric("Total P&L", f"${total_pnl:,.2f}", f"{total_pnl_percentage:.1f}%")
    
    with col4:
        st.metric("Number of Holdings", len(st.session_state.investments))
    
    # Pie chart for visualization
    st.subheader("Portfolio Distribution")
    
    # Group by investment name and sum amounts (in case of duplicate names)
    name_totals = {}
    for inv in st.session_state.investments:
        if inv['name'] in name_totals:
            name_totals[inv['name']] += inv['amount']
        else:
            name_totals[inv['name']] = inv['amount']
    
    # Create pie chart data
    chart_data = pd.DataFrame(
        list(name_totals.items()),
        columns=['Investment Name', 'Amount']
    )
    
    # Create pie chart using Matplotlib
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(chart_data['Amount'], labels=chart_data['Investment Name'], autopct='%1.1f%%')
    ax.set_title('Portfolio Distribution by Individual Investments')
    st.pyplot(fig)
    
else:
    st.info("No investments added yet. Add your first investment above to get started!")

st.logo("logo.png")