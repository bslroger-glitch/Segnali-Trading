import base64
import hashlib
import json
import math
import os
from datetime import datetime
from urllib.parse import quote_plus

import feedparser
import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- INDICI E TICKERS ---
INDICES = {
    "FTSE MIB": [
        "A2A.MI", "AMP.MI", "AZM.MI", "BAMI.MI", "BGN.MI", "BMPS.MI", "BPE.MI", "BRE.MI", 
        "BZZ.MI", "CPR.MI", "DIA.MI", "ENEL.MI", "ENI.MI", "ERG.MI", "RACE.MI", "G.MI", 
        "HER.MI", "ISP.MI", "INW.MI", "ITM.MI", "IVG.MI", "LDO.MI", "MB.MI", "MONC.MI", 
        "NEXI.MI", "PIRC.MI", "PST.MI", "PRY.MI", "REC.MI", "SFER.MI", "SRG.MI", "STLAM.MI", 
        "STM.MI", "TEN.MI", "TIT.MI", "TRN.MI", "UCG.MI", "UNIP.MI"
    ],
    "FTSE Italia All Share": [
        "A2A.MI", "ACE.MI", "AEFF.MI", "AMP.MI", "ANIMA.MI", "ARN.MI", "ARIST.MI", "ASC.MI", 
        "AVIO.MI", "AZM.MI", "BAMI.MI", "BGN.MI", "BMPS.MI", "BPE.MI", "BRE.MI", "BZZ.MI", 
        "CAI.MI", "CEM.MI", "CPR.MI", "CRED.MI", "DAL.MI", "DIA.MI", "DIB.MI", "ELN.MI", 
        "EMT.MI", "ENEL.MI", "ENI.MI", "ERG.MI", "EXP.MI", "FILA.MI", "RACE.MI", "G.MI", 
        "GVS.MI", "HER.MI", "IDA.MI", "IF.MI", "IGV.MI", "ILL.MI", "ISP.MI", "INW.MI", 
        "IRE.MI", "ITM.MI", "ITW.MI", "IVG.MI", "JUVE.MI", "LDO.MI", "LIRC.MI", "MARR.MI", 
        "MB.MI", "MFEA.MI", "MFEB.MI", "MONC.MI", "MOND.MI", "NEXI.MI", "OVS.MI", "PIAGG.MI", 
        "PIRC.MI", "PST.MI", "PRY.MI", "REC.MI", "REVO.MI", "SAES.MI", "SFER.MI", "SES.MI", 
        "SOG.MI", "SRG.MI", "SRS.MI", "STLAM.MI", "STM.MI", "TAM.MI", "TEN.MI", "TINE.MI", 
        "TIP.MI", "TIS.MI", "TIT.MI", "TRN.MI", "TXT.MI", "UCG.MI", "UNIP.MI", "WEBU.MI", 
        "WIIT.MI", "ZIGN.MI"
    ],
    "Dow Jones": [
        "AXP", "AMGN", "AAPL", "BA", "CAT", "CSCO", "CVX", "GS", "HD", "HON", "IBM", 
        "INTC", "JNJ", "KO", "JPM", "MCD", "MMM", "MRK", "MSFT", "NKE", "PG", "CRM", 
        "TRV", "UNH", "UNP", "V", "VZ", "WMT", "DIS"
    ],
    "S&P 500 (Top 50)": [
        "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "META", "BRK-B", "TSLA", "UNH", 
        "JNJ", "V", "XOM", "JPM", "PG", "MA", "AVGO", "HD", "CVX", "ABBV", "LLY", "PEP", 
        "COST", "MRK", "KO", "ADBE", "TMO", "WMT", "PFE", "CSCO", "MCD", "CRM", "ACN", 
        "ABT", "LIN", "DIS", "BAC", "NFLX", "CMCSA", "TXN", "ORCL", "VZ", "ADI", "AMD", 
        "PM", "NKE", "UPS", "INTU", "T", "LOW"
    ],
    "Nasdaq 100 (Top 50)": [
        "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "META", "TSLA", "AVGO", "ADBE", 
        "COST", "PEP", "NFLX", "CSCO", "AMD", "QCOM", "TMUS", "INTU", "AMAT", "INTC", 
        "ISRG", "TXN", "HON", "AMGN", "BKNG", "SNPS", "SBUX", "ADI", "GILD", "CDNS", 
        "REGN", "MDLZ", "VRTX", "PANW", "KLAC", "PYPL", "LRCX", "ADI", "MELI", "MNST", 
        "ORLY", "CTAS", "SNPS", "ADSK", "CDNS", "MAR", "PDD", "ABNB", "ROP", "LULU"
    ],
    "Criptovalute (Top 50)": [
        "BTC-USD", "ETH-USD", "USDT-USD", "BNB-USD", "SOL-USD", "XRP-USD", "USDC-USD", "ADA-USD", "DOGE-USD", "TRX-USD",
        "TON1-USD", "LINK-USD", "AVAX-USD", "SHIB-USD", "DOT-USD", "BCH-USD", "BCH-USD", "WBTC-USD", "UNI7083-USD", "NEAR-USD",
        "MATIC-USD", "DAI-USD", "LTC-USD", "ICP-USD", "LEO-USD", "PEPE-USD", "ETC-USD", "APT-USD", "RENDER-USD", "XLM-USD",
        "STX-USD", "OKB-USD", "ARB-USD", "INJ-USD", "FIL-USD", "VET-USD", "MKR-USD", "KAS-USD", "LDO-USD", "RNDR-USD",
        "THETA-USD", "FTM-USD", "HBAR-USD", "SUI-USD", "GRT-USD", "OP-USD", "SEI-USD", "FET-USD", "RUNE-USD", "TIA-USD"
    ]
}

# --- NOMI COMPLETI SOCIETA ---
TICKER_NAMES = {
    # FTSE MIB
    "A2A.MI": "A2A", "AMP.MI": "Amplifon", "AZM.MI": "Azimut", "BAMI.MI": "Banco BPM", 
    "BGN.MI": "Banca Generali", "BMPS.MI": "Banca MPS", "BPE.MI": "BPER Banca", 
    "BRE.MI": "Brembo", "BZZ.MI": "Buzzi Unicem", "CPR.MI": "Campari", "DIA.MI": "Diasorin", 
    "ENEL.MI": "Enel", "ENI.MI": "Eni", "ERG.MI": "Erg", "RACE.MI": "Ferrari", 
    "G.MI": "Generali Assicurazioni", "HER.MI": "Hera", "ISP.MI": "Intesa Sanpaolo", 
    "INW.MI": "Inwit", "ITM.MI": "Italgas", "IVG.MI": "Iveco Group", "LDO.MI": "Leonardo", 
    "MB.MI": "Mediobanca", "MONC.MI": "Moncler", "NEXI.MI": "Nexi", "PIRC.MI": "Pirelli", 
    "PST.MI": "Poste Italiane", "PRY.MI": "Prysmian", "REC.MI": "Recordati", 
    "SFER.MI": "Salvatore Ferragamo", "SRG.MI": "Snam", "STLAM.MI": "Stellantis", 
    "STM.MI": "STMicroelectronics", "TEN.MI": "Tenaris", "TIT.MI": "Telecom Italia", 
    "TRN.MI": "Terna", "UCG.MI": "UniCredit", "UNIP.MI": "Unipol",
    # FTSE Italia All Share (subset)
    "ACE.MI": "Acea", "AEFF.MI": "Aeffe", "ANIMA.MI": "Anima Holding", "ARN.MI": "Alerion Clean Power",
    "ARIST.MI": "Ariston Holding", "ASC.MI": "Ascopiave", "AVIO.MI": "Avio", "JUVE.MI": "Juventus FC",
    "OVS.MI": "OVS", "PIAGG.MI": "Piaggio", "WEBU.MI": "Webuild",
    # USA
    "AAPL": "Apple Inc.", "MSFT": "Microsoft", "AMZN": "Amazon", "NVDA": "NVIDIA", 
    "GOOGL": "Alphabet (A)", "GOOG": "Alphabet (C)", "META": "Meta Platforms", "TSLA": "Tesla", 
    "BRK-B": "Berkshire Hathaway", "UNH": "UnitedHealth", "JNJ": "Johnson & Johnson", 
    "V": "Visa", "XOM": "Exxon Mobil", "JPM": "JPMorgan Chase", "PG": "Procter & Gamble", 
    "MA": "Mastercard", "AVGO": "Broadcom", "HD": "Home Depot", "CVX": "Chevron", 
    "ABBV": "AbbVie", "LLY": "Eli Lilly", "PEP": "PepsiCo", "COST": "Costco", 
    "MRK": "Merck & Co.", "KO": "Coca-Cola", "ADBE": "Adobe", "TMO": "Thermo Fisher", 
    "WMT": "Walmart", "PFE": "Pfizer", "CSCO": "Cisco Systems", "MCD": "McDonald's", 
    "CRM": "Salesforce", "ACN": "Accenture", "ABT": "Abbott Laboratories", "LIN": "Linde", 
    "DIS": "Disney", "BAC": "Bank of America", "NFLX": "Netflix", "CMCSA": "Comcast", 
    "TXN": "Texas Instruments", "ORCL": "Oracle", "VZ": "Verizon", "ADI": "Analog Devices", 
    "AMD": "AMD", "PM": "Philip Morris", "NKE": "Nike", "UPS": "United Parcel Service", 
    "INTU": "Intuit", "T": "AT&T", "LOW": "Lowe's",
    # Crypto
    "BTC-USD": "Bitcoin", "ETH-USD": "Ethereum", "USDT-USD": "Tether", "BNB-USD": "BNB", "SOL-USD": "Solana",
    "XRP-USD": "XRP", "USDC-USD": "USDC", "ADA-USD": "Cardano", "DOGE-USD": "Dogecoin", "TRX-USD": "Tron",
    "TON1-USD": "Toncoin", "LINK-USD": "Chainlink", "AVAX-USD": "Avalanche", "SHIB-USD": "Shiba Inu", "DOT-USD": "Polkadot",
    "BCH-USD": "Bitcoin Cash", "WBTC-USD": "Wrapped Bitcoin", "UNI7083-USD": "Uniswap", "NEAR-USD": "NEAR Protocol",
    "MATIC-USD": "Polygon", "DAI-USD": "Dai", "LTC-USD": "Litecoin", "ICP-USD": "Internet Computer", "LEO-USD": "UNUS SED LEO",
    "PEPE-USD": "Pepe", "ETC-USD": "Ethereum Classic", "APT-USD": "Aptos", "RENDER-USD": "Render", "XLM-USD": "Stellar",
    "STX-USD": "Stacks", "OKB-USD": "OKB", "ARB-USD": "Arbitrum", "INJ-USD": "Injective", "FIL-USD": "Filecoin",
    "VET-USD": "VeChain", "MKR-USD": "Maker", "KAS-USD": "Kaspa", "LDO-USD": "Lido DAO", "RNDR-USD": "Render Token",
    "THETA-USD": "Theta Network", "FTM-USD": "Fantom", "HBAR-USD": "Hedera", "SUI-USD": "Sui", "GRT-USD": "The Graph",
    "OP-USD": "Optimism", "SEI-USD": "Sei", "FET-USD": "Fetch.ai", "RUNE-USD": "THORChain", "TIA-USD": "Celestia"
}


POSITIVE_KEYWORDS = {
    "upgrade",
    "beat",
    "growth",
    "guidance raised",
    "record",
    "partnership",
    "acquisition",
    "buyback",
    "dividend increase",
    "strong",
    "outperform",
    "migliora",
    "utile in crescita",
    "accordo",
    "rialzo",
    "target alzato",
}

NEGATIVE_KEYWORDS = {
    "downgrade",
    "miss",
    "warning",
    "guidance cut",
    "lawsuit",
    "investigation",
    "decline",
    "weak",
    "underperform",
    "profit warning",
    "taglio",
    "perdita",
    "indagine",
    "rischio",
    "debito elevato",
}


def safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def sentiment_from_title(title):
    text = (title or "").lower()
    score = 0
    for word in POSITIVE_KEYWORDS:
        if word in text:
            score += 1
    for word in NEGATIVE_KEYWORDS:
        if word in text:
            score -= 1
    return score


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_rumors(query, max_items=12):
    rss_url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=it&gl=IT&ceid=IT:it"
    feed = feedparser.parse(rss_url)
    rows = []
    for entry in feed.entries[:max_items]:
        rows.append(
            {
                "title": entry.get("title", "Senza titolo"),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "sentiment": sentiment_from_title(entry.get("title", "")),
            }
        )
    if not rows:
        return {"avg_sentiment": 0.0, "items": []}
    avg = float(np.mean([r["sentiment"] for r in rows]))
    return {"avg_sentiment": avg, "items": rows}


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stock_data(ticker):
    tk = yf.Ticker(ticker)
    info = tk.info or {}
    # Fetch 3 years of data
    hist = tk.history(period="3y", auto_adjust=True)

    if hist.empty:
        return None

    close = hist["Close"].dropna()
    current_price = safe_float(info.get("currentPrice")) or safe_float(close.iloc[-1])
    
    # Technical Indicators
    sma50 = close.rolling(window=50).mean()
    sma200 = close.rolling(window=200).mean()
    
    # RSI Calculation
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    perf_6m = None
    if len(close) > 126:
        perf_6m = ((close.iloc[-1] / close.iloc[-126]) - 1) * 100

    returns = close.pct_change().dropna()
    volatility = float(returns.std() * math.sqrt(252) * 100) if not returns.empty else None

    eps = safe_float(info.get("trailingEps"))
    book_value = safe_float(info.get("bookValue"))
    fair_value = None
    if eps and book_value and eps > 0 and book_value > 0:
        fair_value = math.sqrt(22.5 * eps * book_value)

    fundamentals = {
        "ticker": ticker,
        "name": info.get("shortName") or ticker,
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "price": current_price,
        "market_cap": safe_float(info.get("marketCap")),
        "pe": safe_float(info.get("trailingPE")),
        "forward_pe": safe_float(info.get("forwardPE")),
        "pb": safe_float(info.get("priceToBook")),
        "roe": safe_float(info.get("returnOnEquity")),
        "debt_to_equity": safe_float(info.get("debtToEquity")),
        "revenue_growth": safe_float(info.get("revenueGrowth")),
        "earnings_growth": safe_float(info.get("earningsGrowth")),
        "dividend_yield": safe_float(info.get("dividendYield")),
        "payout_ratio": safe_float(info.get("payoutRatio")),
        "target_price": safe_float(info.get("targetMeanPrice")),
        "fair_value": fair_value,
        "volatility": volatility,
        "perf_6m": perf_6m,
        "rsi": safe_float(rsi.iloc[-1]) if not rsi.empty else None,
        "sma50": safe_float(sma50.iloc[-1]) if not sma50.empty else None,
        "sma200": safe_float(sma200.iloc[-1]) if not sma200.empty else None,
    }
    return fundamentals


def score_investment(data, profile="Bilanciata"):
    score = 50
    reasons = []

    # Weights context based on profile
    is_value = profile == "Value (Sottovalutati)"
    is_growth = profile == "Growth (Crescita)"
    is_sentiment = profile == "News/Rumors"
    
    pe = data.get("pe")
    pb = data.get("pb")
    roe = data.get("roe")
    dte = data.get("debt_to_equity")
    rev_growth = data.get("revenue_growth")
    earn_growth = data.get("earnings_growth")
    perf_6m = data.get("perf_6m")
    rsi = data.get("rsi")
    price = data.get("price")
    sma50 = data.get("sma50")
    sma200 = data.get("sma200")
    div_yield = data.get("dividend_yield")

    # 1. Fondamentali
    if pe is not None:
        if pe < 12:
            score += 12 if is_value else 8
            reasons.append("P/E basso (Value)")
        elif pe > 35:
            score -= 10 if is_value else 6
            reasons.append("P/E elevato")

    if pb is not None:
        if pb < 1.5:
            score += 8 if is_value else 5
            reasons.append("Price/Book attraente")
        elif pb > 5:
            score -= 6
            reasons.append("Price/Book eccessivo")

    if roe is not None:
        roe_pct = roe * 100
        if roe_pct > 15:
            score += 10
            reasons.append("ROE eccellente")
        elif roe_pct < 5:
            score -= 8
            reasons.append("ROE insufficiente")

    # 2. Crescita
    if rev_growth is not None:
        if rev_growth > 0.15:
            score += 12 if is_growth else 6
            reasons.append("Crescita ricavi accelerata")
        elif rev_growth < 0:
            score -= 10
            reasons.append("Fatturato in contrazione")

    if earn_growth is not None:
        if earn_growth > 0.20:
            score += 10 if is_growth else 5
            reasons.append("Utili in forte espansione")

    # 3. Analisi Tecnica
    if rsi is not None:
        if rsi < 30:
            score += 15 if is_value else 8
            reasons.append(f"Ipervenduto tecnico (RSI: {rsi:.1f})")
        elif rsi > 70:
            score -= 15
            reasons.append(f"Ipercomprato - Rischio storno (RSI: {rsi:.1f})")

    if price and sma50 and sma200:
        if price > sma50 > sma200:
            score += 10
            reasons.append("Trend rialzista confermato (Price > SMA50 > SMA200)")
        elif price < sma50 < sma200:
            score -= 10
            reasons.append("Trend ribassista di lungo periodo")

    # 4. Dividendi
    if div_yield is not None:
        dy_pct = div_yield * 100
        if dy_pct > 6:
            score += 8
            reasons.append(f"Alto rendimento dividendi ({dy_pct:.1f}%)")
        elif dy_pct > 4:
            score += 4
            reasons.append(f"Dividendo solido ({dy_pct:.1f}%)")

    return max(0, min(100, score)), reasons


def build_trade_levels(data, total_score):
    price = data.get("price")
    fair_value = data.get("fair_value")
    target = data.get("target_price")
    volatility = data.get("volatility") or 25.0

    if not price:
        return None, None, None, None

    entry_margin = max(0.03, min(0.15, volatility / 300))
    entry = price * (1 - entry_margin)

    exits = []
    if fair_value and fair_value > entry:
        exits.append(fair_value * 0.95)
    if target and target > entry:
        exits.append(target)

    score_boost = max(0.05, min(0.22, (total_score - 45) / 220 + volatility / 300))
    exits.append(price * (1 + score_boost))

    exit_price = max(exits)
    stop_loss = entry * (1 - max(0.04, min(0.12, volatility / 250)))
    potential_gain = ((exit_price - entry) / entry) * 100

    return entry, exit_price, stop_loss, potential_gain


def investment_label(score):
    if score >= 75:
        return "Molto interessante"
    if score >= 62:
        return "Interessante"
    if score >= 50:
        return "Da monitorare"
    return "Debole"


def simulate_portfolio(ranked, capital, risk_pct, max_positions, min_score):
    candidates = [
        r
        for r in ranked
        if r.get("entry") is not None
        and r.get("stop") is not None
        and r.get("exit") is not None
        and r.get("score", 0) >= min_score
        and r["entry"] > r["stop"]
    ]
    picks = candidates[:max_positions]
    if not picks:
        return []

    risk_budget = capital * (risk_pct / 100.0)
    per_trade_budget = capital / len(picks)
    rows = []
    for r in picks:
        entry = r["entry"]
        stop = r["stop"]
        exit_price = r["exit"]
        risk_per_share = entry - stop
        if risk_per_share <= 0:
            continue

        qty_by_risk = int(risk_budget // risk_per_share)
        qty_by_budget = int(per_trade_budget // entry)
        qty = max(0, min(qty_by_risk, qty_by_budget))
        if qty == 0:
            continue

        invested = qty * entry
        expected_value = qty * exit_price
        expected_profit = expected_value - invested
        max_loss = qty * risk_per_share

        rows.append(
            {
                "Ticker": r["ticker"],
                "Societa": r["name"],
                "Score": r["score"],
                "Quantita": qty,
                "Prezzo ingresso": entry,
                "Prezzo uscita": exit_price,
                "Stop loss": stop,
                "Capitale allocato": invested,
                "Profitto potenziale": expected_profit,
                "Perdita massima a stop": max_loss,
                "Rendimento stimato %": ((exit_price - entry) / entry) * 100,
            }
        )
    return rows


def analyze_ticker(ticker, profile="Bilanciata"):
    data = fetch_stock_data(ticker)
    if not data:
        return None

    fund_score, reasons = score_investment(data, profile)
    query = f"{data['name']} {ticker} borsa milano risultati trimestrali rumors"
    rumor_data = fetch_rumors(query)
    rumor_sent = rumor_data["avg_sentiment"]

    # Sentiment weight adjustment
    sentiment_mult = 12 if profile == "News/Rumors" else 6
    total_score = int(max(0, min(100, fund_score + rumor_sent * sentiment_mult)))
    entry, exit_price, stop_loss, gain = build_trade_levels(data, total_score)

    if rumor_sent > 0.3:
        reasons.append("News/rumors recenti con tono mediamente positivo")
    elif rumor_sent < -0.3:
        reasons.append("News/rumors recenti con tono mediamente negativo")

    if data.get("fair_value") and data.get("price"):
        if data["fair_value"] > data["price"] * 1.1:
            reasons.append("Prezzo sotto stima di fair value (Graham)")
        elif data["fair_value"] < data["price"] * 0.9:
            reasons.append("Prezzo sopra stima prudente di fair value")

    return {
        "ticker": ticker,
        "name": data["name"],
        "sector": data.get("sector"),
        "industry": data.get("industry"),
        "score": total_score,
        "label": investment_label(total_score),
        "entry": entry,
        "exit": exit_price,
        "stop": stop_loss,
        "gain": gain,
        "price": data.get("price"),
        "target": data.get("target_price"),
        "fair_value": data.get("fair_value"),
        "volatility": data.get("volatility"),
        "rsi": data.get("rsi"),
        "div_yield": data.get("dividend_yield"),
        "reasons": reasons,
        "rumors": rumor_data["items"],
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def render_stock_chart(ticker, name):
    """
    Scarica i dati storici e renderizza un grafico candlestick professionale con indicatori.
    """
    try:
        # Recupera dati ultimi 3 anni usando Ticker.history per maggior stabilità
        tk = yf.Ticker(ticker)
        df = tk.history(period="3y", interval="1d", auto_adjust=True)
        
        if df.empty:
            return None

        # Reset index per assicurarci che 'Date' sia una colonna se necessario, 
        # ma go.Candlestick accetta df.index
        
        # Calcolo Medie Mobili
        df["SMA50"] = df["Close"].rolling(window=50).mean()
        df["SMA200"] = df["Close"].rolling(window=200).mean()

        # Calcolo RSI
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))

        # Creazione Subplots (2 righe: Prezzo/Medie e RSI)
        fig = make_subplots(
            rows=2, cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0.1,
            row_heights=[0.7, 0.3],
            subplot_titles=(f"Trend 3 Anni - {name} ({ticker})", "RSI (14)")
        )

        # Candlestick - Usiamo i nomi delle colonne standard di yfinance.history
        fig.add_trace(
            go.Candlestick(
                x=df.index, 
                open=df["Open"], 
                high=df["High"],
                low=df["Low"], 
                close=df["Close"], 
                name="Prezzo"
            ), row=1, col=1
        )

        # Medie Mobili
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], line=dict(color='orange', width=1), name="SMA 50"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA200"], line=dict(color='red', width=1), name="SMA 200"), row=1, col=1)

        # RSI
        fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], line=dict(color='purple', width=1.5), name="RSI"), row=2, col=1)
        
        # Linee di Ipercomprato/Ipervenduto
        fig.add_hline(y=70, line_dash="dash", line_color="red", line_width=1, row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", line_width=1, row=2, col=1)
        fig.update_yaxes(range=[0, 100], row=2, col=1)

        # Layout styling
        fig.update_layout(
            height=500,
            template="plotly_dark",
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis_rangeslider_visible=False,
            margin=dict(l=10, r=10, t=60, b=10)
        )

        return fig
    except Exception as e:
        print(f"Errore generazione grafico per {ticker}: {e}")
        return None


def format_eur(x):
    if x is None:
        return "n/d"
    return f"EUR {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def render_kpi(label, value, delta=None):
    delta_html = f'<div class="portfolio-kpi-delta">{delta}</div>' if delta else ""
    st.markdown(
        f"""
        <div class="portfolio-kpi">
            <div class="portfolio-kpi-label">{label}</div>
            <div class="portfolio-kpi-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="SEGNALI DI INVESTIMENTO", layout="wide")

# --- AUTHENTICATION LOGIC ---
USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        default_users = {"supervisore": {"password": "", "image_base64": ""}}
        with open(USERS_FILE, "w") as f:
            json.dump(default_users, f)
        return default_users
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"supervisore": {"password": "", "image_base64": ""}}

def save_users(users_dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users_dict, f)

def hash_password(password):
    if not password:
        return ""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    if not hashed:
        return password == ""
    return hash_password(password) == hashed

# Initialization
if "users" not in st.session_state:
    st.session_state["users"] = load_users()

# Retrieve saved login from URL parameters for persistence
query_params = st.query_params
saved_user = query_params.get("logged_in")

if "logged_in_user" not in st.session_state:
    if saved_user and saved_user in st.session_state["users"]:
        st.session_state["logged_in_user"] = saved_user
    else:
        st.session_state["logged_in_user"] = None

if "login_step" not in st.session_state:
    st.session_state["login_step"] = "select_profile"

if "selected_profile" not in st.session_state:
    st.session_state["selected_profile"] = None

def get_base64_of_bin_file(bin_file):
    import base64
    import os
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

bg_img = get_base64_of_bin_file("bg_home.png")
if bg_img:
    st.markdown(
        f"""
        <style>
        /* Target the main container of the app */
        .stApp {{
            background-image: linear-gradient(to bottom, rgba(15, 23, 42, 0.45), rgba(15, 23, 42, 1)), url("data:image/png;base64,{bg_img}");
            background-size: cover;
            background-position: top center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        /* Make the header transparent so the background shows through */
        header[data-testid="stHeader"] {{
            background: transparent !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Process actions from clickable icons
if "action" in query_params:
    action = query_params["action"]
    if action == "login":
        req_user = query_params.get("user")
        if req_user and req_user in st.session_state["users"]:
            if req_user == "supervisore":
                st.session_state["logged_in_user"] = req_user
                st.session_state["login_step"] = "select_profile"
                st.query_params["logged_in"] = req_user
                if "action" in st.query_params: del st.query_params["action"]
                if "user" in st.query_params: del st.query_params["user"]
                st.rerun()
            else:
                st.session_state["selected_profile"] = req_user
                st.session_state["login_step"] = "enter_password"
                if "action" in st.query_params: del st.query_params["action"]
                if "user" in st.query_params: del st.query_params["user"]
                st.rerun()
    elif action == "signup":
        st.session_state["login_step"] = "signup"
        if "action" in st.query_params: del st.query_params["action"]
        st.rerun()

# Login/Signup Screen
if not st.session_state["logged_in_user"]:
    st.markdown(
        """
        <style>
        .profile-pic {
            width: 120px;
            height: 120px;
            border-radius: 20px;
            background-color: #1e293b;
            color: #f8fafc;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3.5rem;
            font-weight: 700;
            margin: 0 auto 10px auto;
            border: 2px solid transparent;
            transition: all 0.2s;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            background-size: cover;
            background-position: center;
        }
        .profile-pic:hover {
            border: 2px solid #94a3b8;
        }
        .add-pic {
            background-color: transparent !important;
            border: 2px dashed #475569 !important;
            color: #475569 !important;
            font-size: 4rem !important;
            font-weight: 300 !important;
        }
        .add-pic:hover {
            border-color: #94a3b8 !important;
            color: #94a3b8 !important;
        }
        /* Make sure the text is large enough and looks clickable */
        </style>
        """, unsafe_allow_html=True
    )

    if st.session_state["login_step"] == "select_profile":
        st.markdown("<h1 style='text-align: center; font-size: 3.5rem; font-weight: 800; margin-top: 4rem; margin-bottom: 0;'>Chi sta investendo?</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #94a3b8; margin-bottom: 3rem;'>Seleziona il tuo profilo per accedere all'area segnali</p>", unsafe_allow_html=True)

        users = list(st.session_state["users"].keys())
        total_cards = len(users) + 1
        
        cols = st.columns([1] + [2]*total_cards + [1])
        
        for i, user in enumerate(users):
            with cols[i+1]:
                initial = user[0].upper()
                user_data = st.session_state["users"].get(user, {})
                img_b64 = user_data.get("image_base64", "")
                
                if img_b64:
                    bg_style = f"background-image: url('data:image/jpeg;base64,{img_b64}'); color: transparent;"
                else:
                    bg_style = ""

                # Make the avatar clickable
                link = f"/?action=login&user={quote_plus(user)}"
                st.markdown(f'<a href="{link}" target="_self" style="text-decoration: none;"><div class="profile-pic" style="{bg_style}">{initial if not img_b64 else ""}</div></a>', unsafe_allow_html=True)
                
                if st.button(user, key=f"btn_{user}", use_container_width=True, type="tertiary"):
                    if user == "supervisore":
                        st.session_state["logged_in_user"] = user
                        st.session_state["login_step"] = "select_profile"
                        st.query_params["logged_in"] = user
                        if "action" in st.query_params: del st.query_params["action"]
                        if "user" in st.query_params: del st.query_params["user"]
                        st.rerun()
                    else:
                        st.session_state["selected_profile"] = user
                        st.session_state["login_step"] = "enter_password"
                        if "action" in st.query_params: del st.query_params["action"]
                        if "user" in st.query_params: del st.query_params["user"]
                        st.rerun()
                        
        with cols[len(users)+1]:
            st.markdown(f'<a href="/?action=signup" target="_self" style="text-decoration: none;"><div class="profile-pic add-pic">+</div></a>', unsafe_allow_html=True)
            if st.button("Aggiungi", key="btn_add", use_container_width=True, type="tertiary"):
                st.session_state["login_step"] = "signup"
                if "action" in st.query_params: del st.query_params["action"]
                st.rerun()

    elif st.session_state["login_step"] == "enter_password":
        user = st.session_state["selected_profile"]
        st.markdown(f"<h2 style='text-align: center; margin-top: 4rem;'>Bentornato, {user}</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94a3b8; margin-bottom: 2rem;'>Inserisci la tua password per continuare</p>", unsafe_allow_html=True)
        
        _, c, _ = st.columns([1, 2, 1])
        with c:
            login_pwd = st.text_input("Password", type="password", key="login_pwd")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⬅️ Indietro", use_container_width=True):
                    st.session_state["login_step"] = "select_profile"
                    st.rerun()
            with col2:
                if st.button("Accedi", type="primary", use_container_width=True):
                    stored_hash = st.session_state["users"][user].get("password", "")
                    if verify_password(login_pwd, stored_hash):
                        st.session_state["logged_in_user"] = user
                        st.session_state["login_step"] = "select_profile"
                        st.query_params["logged_in"] = user
                        st.rerun()
                    else:
                        st.error("Password errata.")

    elif st.session_state["login_step"] == "signup":
        st.markdown("<h2 style='text-align: center; margin-top: 4rem;'>Nuovo Profilo</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94a3b8; margin-bottom: 2rem;'>Crea un'utenza protetta da password</p>", unsafe_allow_html=True)
        
        _, c, _ = st.columns([1, 2, 1])
        with c:
            signup_user = st.text_input("Username").strip()
            signup_pwd = st.text_input("Password", type="password")
            signup_pwd2 = st.text_input("Conferma Password", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⬅️ Annulla", use_container_width=True):
                    st.session_state["login_step"] = "select_profile"
                    st.rerun()
            with col2:
                if st.button("Crea utenza", type="primary", use_container_width=True):
                    if not signup_user:
                        st.error("Inserisci uno username.")
                    elif signup_user in st.session_state["users"]:
                        st.error("Username già in uso.")
                    elif signup_user.lower() == "supervisore":
                        st.error("Username non consentito.")
                    elif not signup_pwd:
                        st.error("Inserisci una password.")
                    elif signup_pwd != signup_pwd2:
                        st.error("Le password non coincidono.")
                    else:
                        st.session_state["users"][signup_user] = {"password": hash_password(signup_pwd), "image_base64": ""}
                        save_users(st.session_state["users"])
                        st.session_state["login_step"] = "select_profile"
                        st.success("Profilo creato! Ora puoi accedere.")
                        st.rerun()

    st.stop()  # Stop execution of the rest of the app if not logged in

st.markdown(
    """
    <style>
    .portfolio-sim-wrap [data-testid="stDataFrame"] * {
        font-size: 0.82rem !important;
    }
    .portfolio-kpi {
        background: rgba(15, 23, 42, 0.35);
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 10px;
        padding: 10px 12px;
        min-height: 74px;
    }
    .portfolio-kpi-label {
        font-size: 0.72rem;
        opacity: 0.85;
        margin-bottom: 4px;
    }
    .portfolio-kpi-value {
        font-size: 0.75rem;
        line-height: 1.1;
        font-weight: 600;
    }
    .portfolio-kpi-delta {
        font-size: 0.68rem;
        margin-top: 4px;
        color: #16a34a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.title("SEGNALI DI INVESTIMENTO")
st.caption(
    "Analisi automatica di notizie, indicatori fondamentali e livelli operativi. "
    "Uso informativo: non e consulenza finanziaria."
)

with st.sidebar:
    st.markdown(f"**Utente:** `{st.session_state['logged_in_user']}`")
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state["logged_in_user"] = None
        if "logged_in" in st.query_params:
            del st.query_params["logged_in"]
        st.rerun()
        
    if st.session_state["logged_in_user"] != "supervisore":
        with st.expander("🔑 Cambia Password"):
            old_pwd = st.text_input("Vecchia Password", type="password")
            new_pwd = st.text_input("Nuova Password", type="password")
            new_pwd2 = st.text_input("Conferma Nuova Password", type="password")
            
            if st.button("Aggiorna Password"):
                current_user = st.session_state["logged_in_user"]
                stored_hash = st.session_state["users"][current_user].get("password", "")
                if not verify_password(old_pwd, stored_hash):
                    st.error("Vecchia password errata.")
                elif not new_pwd:
                    st.error("La nuova password non può essere vuota.")
                elif new_pwd != new_pwd2:
                    st.error("Le nuove password non coincidono.")
                else:
                    st.session_state["users"][current_user]["password"] = hash_password(new_pwd)
                    save_users(st.session_state["users"])
                    st.success("Password aggiornata con successo! Effettua il logout per testare.")

        with st.expander("🖼️ Cambia Immagine Profilo"):
            uploaded_file = st.file_uploader("Scegli un'immagine", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                if st.button("Salva Immagine", use_container_width=True):
                    bytes_data = uploaded_file.getvalue()
                    b64_encoded = base64.b64encode(bytes_data).decode()
                    
                    current_user = st.session_state["logged_in_user"]
                    st.session_state["users"][current_user]["image_base64"] = b64_encoded
                    save_users(st.session_state["users"])
                    st.success("Immagine di profilo aggiornata correttamente!")
                    st.rerun()

    st.divider()

    # Info button to show manual
    @st.dialog("Manuale dell'Investitore", width="large")
    def show_manual():
        with open("Manuale_Trading.md", "r", encoding="utf-8") as f:
            st.markdown(f.read())

    if st.button("ℹ️ Info & Manuale", use_container_width=True):
        show_manual()
        
    if st.session_state["logged_in_user"] == "supervisore":
        @st.dialog("Checklist Attività", width="large")
        def show_checklist():
            st.markdown("### Gestione Attività Supervisore")
            
            # Initialize checklist in user dict if not present
            user_data = st.session_state["users"]["supervisore"]
            if "checklist" not in user_data:
                user_data["checklist"] = []
                
            tasks = user_data["checklist"]
            
            # Add new task
            new_task_title = st.text_input("Titolo attività", key="new_task_title")
            new_task_desc = st.text_area("Descrizione", key="new_task_desc")
            
            if st.button("Aggiungi", use_container_width=True):
                if new_task_title:
                    tasks.append({
                        "text": new_task_title, 
                        "description": new_task_desc, 
                        "done": False
                    })
                    save_users(st.session_state["users"])
                    st.session_state["dummy_refresh"] = st.session_state.get("dummy_refresh", 0) + 1

            st.divider()

            # Display and manage current tasks
            if not tasks:
                st.info("Nessuna attività presente.")
            else:
                for idx, task in enumerate(tasks):
                    c_check, c_text, c_del = st.columns([1, 8, 1])
                    with c_check:
                        # Use on_change to save the state instead of rerunning
                        def toggle_task(i=idx):
                            tasks[i]["done"] = st.session_state[f"chk_{i}"]
                            save_users(st.session_state["users"])

                        st.checkbox("Done", value=task["done"], label_visibility="collapsed", key=f"chk_{idx}", on_change=toggle_task)

                    with c_text:
                        text_style = "text-decoration: line-through; color: #94a3b8;" if task["done"] else ""
                        
                        desc = task.get("description", "")
                        if desc:
                            with st.expander(rf"$\textsf{{\color{{inherit}}{{{task['text']}}}}}$"):
                                st.markdown(f"<span style='{text_style}'>{desc}</span>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<span style='{text_style}'>{task['text']}</span>", unsafe_allow_html=True)
                            
                    with c_del:
                        if st.button("❌", key=f"del_{idx}", help="Elimina attività"):
                            tasks.pop(idx)
                            save_users(st.session_state["users"])
                            st.session_state["dummy_refresh"] = st.session_state.get("dummy_refresh", 0) + 1
                            
        if st.button("📋 Checklist Attività", use_container_width=True):
            show_checklist()

    st.divider()

    st.header("1. Selezione Indice")
    selected_index = st.selectbox(
        "Indice di mercato",
        options=list(INDICES.keys()),
        index=0,
        key="index_selector"
    )
    
    current_index_tickers = INDICES[selected_index]
    
    if "ticker_multiselect" not in st.session_state:
        st.session_state["ticker_multiselect"] = current_index_tickers[:8]
    st.header("2. Selezione Titoli")

    col1, col2 = st.columns(2)
    if col1.button("Seleziona Tutti"):
        st.session_state["ticker_multiselect"] = current_index_tickers
        st.rerun()
    if col2.button("Deseleziona Tutti"):
        st.session_state["ticker_multiselect"] = []
        st.rerun()

    selected = st.multiselect(
        f"Titoli da analizzare ({selected_index})",
        options=current_index_tickers,
        key="ticker_multiselect",
        format_func=lambda x: f"{x} - {TICKER_NAMES.get(x, '')}" if x in TICKER_NAMES else x
    )
    st.header("Strategia di Analisi")
    strategy_profile = st.selectbox(
        "Profilo Investitore",
        options=["Bilanciata", "Value (Sottovalutati)", "Growth (Crescita)", "News/Rumors"],
        index=0
    )
    st.header("Portfolio Simulator")
    capital = st.number_input("Capitale totale (EUR)", min_value=1000.0, value=10000.0, step=500.0)
    risk_pct = st.slider("Rischio per trade (%)", min_value=0.5, max_value=5.0, value=1.0, step=0.1)
    max_positions = st.slider("Numero massimo posizioni", min_value=1, max_value=10, value=5, step=1)
    min_score = st.slider("Score minimo per entrare in portafoglio", min_value=40, max_value=85, value=55, step=1)
    run = st.button("Avvia scansione")

if run:
    if not selected:
        st.warning("Seleziona almeno un titolo.")
    else:
        progress = st.progress(0)
        results = []
        for idx, ticker in enumerate(selected, start=1):
            res = analyze_ticker(ticker, profile=strategy_profile)
            if res:
                results.append(res)
            progress.progress(idx / len(selected))

        if not results:
            st.error("Nessun dato disponibile. Riprova piu tardi.")
        else:
            ranked = sorted(results, key=lambda x: (x["score"], x["gain"] or -999), reverse=True)
            table = pd.DataFrame(
                [
                    {
                        "Ticker": r["ticker"],
                        "Societa": r["name"],
                        "Settore": r["sector"],
                        "Score": r["score"],
                        "Valutazione": r["label"],
                        "RSI": round(r["rsi"], 1) if r["rsi"] else "n/d",
                        "Div. Yield %": round(r["div_yield"] * 100, 2) if r["div_yield"] else 0,
                        "Prezzo attuale": format_eur(r["price"]),
                        "Ingresso stimato": format_eur(r["entry"]),
                        "Guadagno potenziale %": round(r["gain"], 2) if r["gain"] is not None else None,
                    }
                    for r in ranked
                ]
            )
            st.subheader("Classifica opportunita")
            st.dataframe(table, use_container_width=True)

            top = ranked[0]
            st.success(
                f"Titolo con miglior profilo ora: {top['ticker']} ({top['name']}) "
                f"con score {top['score']} e guadagno potenziale stimato {top['gain']:.2f}%"
            )

            st.subheader("Dettaglio motivazioni")
            for r in ranked:
                with st.expander(f"{r['ticker']} - {r['name']} | Score {r['score']} ({r['label']})"):
                    st.write(f"Aggiornato: {r['updated_at']}")
                    st.write(f"Prezzo attuale: {format_eur(r['price'])}")
                    st.write(f"Range operativo: ingresso {format_eur(r['entry'])}, uscita {format_eur(r['exit'])}")
                    st.write(f"Stop loss suggerito: {format_eur(r['stop'])}")
                    st.write(f"Guadagno potenziale massimo stimato: {r['gain']:.2f}%")
                    st.write("Motivazioni:")
                    for reason in r["reasons"]:
                        st.write(f"- {reason}")

                    st.write("Rumors/News rilevate:")
                    if not r["rumors"]:
                        st.write("- Nessuna news recente trovata via feed pubblico.")
                    for item in r["rumors"][:8]:
                        st.markdown(f"- [{item['title']}]({item['link']})")

            st.subheader("Portfolio Simulator")
            simulated = simulate_portfolio(ranked, capital, risk_pct, max_positions, min_score)
            if not simulated:
                st.warning("Nessuna posizione proposta con i parametri correnti.")
            else:
                st.markdown('<div class="portfolio-sim-wrap">', unsafe_allow_html=True)
                sim_df = pd.DataFrame(simulated)
                sim_df_display = sim_df.copy()
                for col in [
                    "Prezzo ingresso",
                    "Prezzo uscita",
                    "Stop loss",
                    "Capitale allocato",
                    "Profitto potenziale",
                    "Perdita massima a stop",
                ]:
                    sim_df_display[col] = sim_df_display[col].apply(format_eur)
                sim_df_display["Rendimento stimato %"] = sim_df["Rendimento stimato %"].round(2)
                st.dataframe(sim_df_display, use_container_width=True)

                total_alloc = float(sim_df["Capitale allocato"].sum())
                total_profit = float(sim_df["Profitto potenziale"].sum())
                total_loss = float(sim_df["Perdita massima a stop"].sum())
                cash_left = capital - total_alloc
                total_return_pct = (total_profit / total_alloc * 100) if total_alloc > 0 else 0.0

                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    render_kpi("Capitale investito", format_eur(total_alloc))
                with c2:
                    render_kpi("Liquidita residua", format_eur(cash_left))
                with c3:
                    render_kpi("Profitto potenziale totale", format_eur(total_profit), f"+{total_return_pct:.2f}%")
                with c4:
                    render_kpi("Perdita massima totale a stop", format_eur(total_loss))
                st.markdown("</div>", unsafe_allow_html=True)

                st.caption(
                    "Sizing calcolato con doppio vincolo: rischio per trade e budget medio per posizione. "
                    "Simulazione euristica, non consulenza finanziaria."
                )

                st.divider()
                st.subheader("Grafici Analisi Tecnica (Posizioni Supportate)")
                
                # Renderizziamo i grafici per i titoli proposti nel simulatore
                for _, row in sim_df.iterrows():
                    ticker = row["Ticker"]
                    name = TICKER_NAMES.get(ticker, ticker)
                    with st.expander(f"Visualizza Grafico: {name} ({ticker})", expanded=False):
                        with st.spinner(f"Generazione grafico per {ticker}..."):
                            fig = render_stock_chart(ticker, name)
                            if fig:
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.error(f"Impossibile caricare il grafico per {ticker}.")
else:
    st.info("Seleziona i titoli a sinistra e premi 'Avvia scansione'.")
