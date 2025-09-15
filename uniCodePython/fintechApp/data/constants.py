"""
Data constants for the Portfolio App
Contains stock and cryptocurrency symbol mappings
"""

POPULAR_STOCKS = {
    # FAANG + Major Tech
    "Apple Inc. (AAPL)": "AAPL",
    "Microsoft Corp. (MSFT)": "MSFT", 
    "Alphabet Inc. (GOOGL)": "GOOGL",
    "Amazon.com Inc. (AMZN)": "AMZN",
    "Meta Platforms Inc. (META)": "META",
    "Netflix Inc. (NFLX)": "NFLX",
    
    # AI & Semiconductors
    "NVIDIA Corp. (NVDA)": "NVDA",
    "Advanced Micro Devices (AMD)": "AMD",
    "Intel Corp. (INTC)": "INTC",
    "Taiwan Semiconductor (TSM)": "TSM",
    "Qualcomm Inc. (QCOM)": "QCOM",
    "Broadcom Inc. (AVGO)": "AVGO",
    "Micron Technology (MU)": "MU",
    
    # Electric Vehicles & Energy
    "Tesla Inc. (TSLA)": "TSLA",
    "BYD Company (BYDDY)": "BYDDY",
    "NIO Inc. (NIO)": "NIO",
    "Rivian Automotive (RIVN)": "RIVN",
    "Lucid Group (LCID)": "LCID",
    "Exxon Mobil Corp. (XOM)": "XOM",
    "Chevron Corp. (CVX)": "CVX",
    
    # Financial Services
    "Berkshire Hathaway (BRK-B)": "BRK-B",
    "JPMorgan Chase & Co. (JPM)": "JPM",
    "Bank of America (BAC)": "BAC",
    "Wells Fargo & Co. (WFC)": "WFC",
    "Goldman Sachs Group (GS)": "GS",
    "Morgan Stanley (MS)": "MS",
    "Visa Inc. (V)": "V",
    "Mastercard Inc. (MA)": "MA",
    "PayPal Holdings (PYPL)": "PYPL",
    "American Express (AXP)": "AXP",
    
    # Healthcare & Pharma
    "UnitedHealth Group Inc. (UNH)": "UNH",
    "Johnson & Johnson (JNJ)": "JNJ",
    "Pfizer Inc. (PFE)": "PFE",
    "AbbVie Inc. (ABBV)": "ABBV",
    "Merck & Co. (MRK)": "MRK",
    "Eli Lilly and Co. (LLY)": "LLY",
    "Bristol Myers Squibb (BMY)": "BMY",
    "Moderna Inc. (MRNA)": "MRNA",
    "Novavax Inc. (NVAX)": "NVAX",
    
    # Consumer & Retail
    "Walmart Inc. (WMT)": "WMT",
    "Costco Wholesale (COST)": "COST",
    "Home Depot Inc. (HD)": "HD",
    "Target Corp. (TGT)": "TGT",
    "Procter & Gamble Co. (PG)": "PG",
    "Coca-Cola Co. (KO)": "KO",
    "PepsiCo Inc. (PEP)": "PEP",
    "McDonald's Corp. (MCD)": "MCD",
    "Starbucks Corp. (SBUX)": "SBUX",
    "Nike Inc. (NKE)": "NKE",
    
    # Media & Entertainment
    "Walt Disney Co. (DIS)": "DIS",
    "Comcast Corp. (CMCSA)": "CMCSA",
    "Warner Bros. Discovery (WBD)": "WBD",
    "Spotify Technology (SPOT)": "SPOT",
    
    # Cloud & Software
    "Salesforce Inc. (CRM)": "CRM",
    "Adobe Inc. (ADBE)": "ADBE",
    "Oracle Corp. (ORCL)": "ORCL",
    "ServiceNow Inc. (NOW)": "NOW",
    "Snowflake Inc. (SNOW)": "SNOW",
    "Palantir Technologies (PLTR)": "PLTR",
    "MongoDB Inc. (MDB)": "MDB",
    "Zoom Video Communications (ZM)": "ZM",
    "Slack Technologies (WORK)": "WORK",
    
    # Telecommunications
    "Verizon Communications (VZ)": "VZ",
    "AT&T Inc. (T)": "T",
    "T-Mobile US Inc. (TMUS)": "TMUS",
    "Cisco Systems Inc. (CSCO)": "CSCO",
    
    # Aerospace & Defense
    "Boeing Co. (BA)": "BA",
    "Lockheed Martin (LMT)": "LMT",
    "Raytheon Technologies (RTX)": "RTX",
    "General Dynamics (GD)": "GD",
    
    # Real Estate & REITs
    "American Tower Corp. (AMT)": "AMT",
    "Prologis Inc. (PLD)": "PLD",
    "Crown Castle Inc. (CCI)": "CCI",
    "Digital Realty Trust (DLR)": "DLR",
    
    # Industrials
    "Caterpillar Inc. (CAT)": "CAT",
    "General Electric (GE)": "GE",
    "3M Company (MMM)": "MMM",
    "Honeywell International (HON)": "HON",
    "United Parcel Service (UPS)": "UPS",
    "FedEx Corp. (FDX)": "FDX",
    
    # Commodities & Materials
    "Freeport-McMoRan (FCX)": "FCX",
    "Newmont Corp. (NEM)": "NEM",
    "Barrick Gold Corp. (GOLD)": "GOLD",
    
    # ETFs & Index Funds
    "S&P 500 ETF (SPY)": "SPY",
    "QQQ Nasdaq ETF (QQQ)": "QQQ",
    "SPDR S&P 500 ETF Trust (SPUS)": "SPUS",
    "Vanguard Total Stock Market (VTI)": "VTI",
    "iShares Core S&P 500 (IVV)": "IVV",
    "Vanguard S&P 500 ETF (VOO)": "VOO",
    "iShares MSCI Emerging Markets (EEM)": "EEM",
    "Vanguard FTSE Developed Markets (VEA)": "VEA",
    "iShares Russell 2000 (IWM)": "IWM",
    "ARK Innovation ETF (ARKK)": "ARKK",
    "ARK Genomics Revolution (ARKG)": "ARKG",
    "Global X Robotics & AI ETF (BOTZ)": "BOTZ",
    
    # International
    "Alibaba Group Holding (BABA)": "BABA",
    "ASML Holding NV (ASML)": "ASML",
    "Samsung Electronics (005930.KS)": "005930.KS",
    "Tencent Holdings (TCEHY)": "TCEHY",
    "Shopify Inc. (SHOP)": "SHOP"
}

POPULAR_CRYPTO = {
    # Top Cryptocurrencies by Market Cap
    "Bitcoin (BTC)": "bitcoin",
    "Ethereum (ETH)": "ethereum",
    "Tether (USDT)": "tether",
    "BNB (BNB)": "binancecoin",
    "Solana (SOL)": "solana",
    "USDC (USDC)": "usd-coin",
    "XRP (XRP)": "ripple",
    "Toncoin (TON)": "the-open-network",
    "Dogecoin (DOGE)": "dogecoin",
    "Cardano (ADA)": "cardano",
    
    # DeFi & Smart Contract Platforms
    "Avalanche (AVAX)": "avalanche-2",
    "TRON (TRX)": "tron",
    "Chainlink (LINK)": "chainlink",
    "Polygon (MATIC)": "matic-network",
    "Polkadot (DOT)": "polkadot",
    "Uniswap (UNI)": "uniswap",
    "Internet Computer (ICP)": "internet-computer",
    "Cosmos (ATOM)": "cosmos",
    "Ethereum Classic (ETC)": "ethereum-classic",
    "Algorand (ALGO)": "algorand",
    "Fantom (FTM)": "fantom",
    "Harmony (ONE)": "harmony",
    "NEAR Protocol (NEAR)": "near",
    "Flow (FLOW)": "flow",
    "Hedera (HBAR)": "hedera-hashgraph",
    
    # Layer 2 & Scaling Solutions
    "Arbitrum (ARB)": "arbitrum",
    "Optimism (OP)": "optimism",
    "Immutable X (IMX)": "immutable-x",
    "Loopring (LRC)": "loopring",
    
    # Privacy Coins
    "Monero (XMR)": "monero",
    "Zcash (ZEC)": "zcash",
    "Dash (DASH)": "dash",
    "Horizen (ZEN)": "horizen",
    
    # Payment & Digital Cash
    "Litecoin (LTC)": "litecoin",
    "Bitcoin Cash (BCH)": "bitcoin-cash",
    "Stellar (XLM)": "stellar",
    "Nano (XNO)": "nano",
    "DigiByte (DGB)": "digibyte",
    
    # Meme Coins & Community Tokens
    "Shiba Inu (SHIB)": "shiba-inu",
    "Pepe (PEPE)": "pepe",
    "Floki (FLOKI)": "floki",
    "SafeMoon (SAFEMOON)": "safemoon",
    "Bonk (BONK)": "bonk",
    
    # Gaming & Metaverse
    "The Sandbox (SAND)": "the-sandbox",
    "Decentraland (MANA)": "decentraland",
    "Axie Infinity (AXS)": "axie-infinity",
    "Gala (GALA)": "gala",
    "Enjin Coin (ENJ)": "enjincoin",
    "ApeCoin (APE)": "apecoin",
    "WAX (WAXP)": "wax",
    
    # Storage & Infrastructure
    "Filecoin (FIL)": "filecoin",
    "Arweave (AR)": "arweave",
    "Storj (STORJ)": "storj",
    "Siacoin (SC)": "siacoin",
    
    # Oracle & Data
    "Chainlink (LINK)": "chainlink",
    "Band Protocol (BAND)": "band-protocol",
    "API3 (API3)": "api3",
    
    # Exchange Tokens
    "FTX Token (FTT)": "ftx-token",
    "KuCoin Token (KCS)": "kucoin-shares",
    "Huobi Token (HT)": "huobi-token",
    "Crypto.com Coin (CRO)": "crypto-com-chain",
    "OKB (OKB)": "okb",
    
    # Yield Farming & DeFi
    "Aave (AAVE)": "aave",
    "Compound (COMP)": "compound-governance-token",
    "Maker (MKR)": "maker",
    "SushiSwap (SUSHI)": "sushi",
    "PancakeSwap (CAKE)": "pancakeswap-token",
    "Curve DAO Token (CRV)": "curve-dao-token",
    "Yearn.finance (YFI)": "yearn-finance",
    "1inch Network (1INCH)": "1inch",
    "Balancer (BAL)": "balancer",
    "Synthetix (SNX)": "synthetix-network-token",
    
    # AI & Technology
    "SingularityNET (AGIX)": "singularitynet",
    "Fetch.ai (FET)": "fetch-ai",
    "Ocean Protocol (OCEAN)": "ocean-protocol",
    "Render Token (RNDR)": "render-token",
    
    # Energy & Sustainability
    "Power Ledger (POWR)": "power-ledger",
    "Energy Web Token (EWT)": "energy-web-token",
    "WePower (WPR)": "wepower",
    
    # Social & Content
    "Steem (STEEM)": "steem",
    "Hive (HIVE)": "hive",
    "Basic Attention Token (BAT)": "basic-attention-token",
    "Theta Network (THETA)": "theta-token",
    "Audius (AUDIO)": "audius",
    
    # Enterprise & Business
    "VeChain (VET)": "vechain",
    "Quant (QNT)": "quant-network",
    "IOTA (MIOTA)": "iota",
    "Ripple (XRP)": "ripple",
    
    # Stablecoins
    "Tether (USDT)": "tether",
    "USD Coin (USDC)": "usd-coin",
    "Binance USD (BUSD)": "binance-usd",
    "Dai (DAI)": "dai",
    "TrueUSD (TUSD)": "true-usd",
    "Pax Dollar (USDP)": "paxos-standard",
    "Frax (FRAX)": "frax"
}
