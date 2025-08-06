# ========== TELEGRAM TRADING BOT ==========
import time
import requests
from datetime import datetime

# ========== CONFIGURATION ==========
TELEGRAM_TOKEN = 'YOUR_BOT_TOKEN_HERE'
TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID_HERE'
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT']

# ========== KEEP ALIVE (FOR REPLIT) ==========
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ========== TELEGRAM FUNCTION ==========
def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

# ========== ANALYSIS FUNCTIONS ==========
def get_klines(symbol, interval="15m", limit=20):
    try:
        url = f"https://api.binance.com/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        response = requests.get(url, params=params, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Klines API error: {e}")
        return None

def calculate_rsi(klines, period=14):
    prices = [float(k[4]) for k in klines]
    if len(prices) < period + 1:
        return None
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def analyze_symbol(symbol):
    klines = get_klines(symbol)
    if not klines:
        return
    price = float(klines[-1][4])
    rsi = calculate_rsi(klines)
    if rsi is None:
        return
    signal = "NEUTRAL"
    emoji = "⚪️"
    if rsi > 70:
        signal = "Overbought (SELL)"
        emoji = "🔴"
    elif rsi < 30:
        signal = "Oversold (BUY)"
        emoji = "🟢"
    message = (
        f"<b>{emoji} {symbol} RSI Signal</b>\n"
        f"------------------\n"
        f"<b>Price:</b> ${price:,.2f}\n"
        f"<b>RSI:</b> {rsi:.2f}\n"
        f"<b>Signal:</b> {signal}"
    )
    if signal != "NEUTRAL":
        send_telegram_message(message)
        print(f"📤 Sent signal for {symbol}")
    else:
        print(f"⚪ No strong signal for {symbol}. RSI={rsi:.2f}")

# ========== MAIN LOOP ==========
if __name__ == "__main__":
    keep_alive()
    send_telegram_message("✅ <b>Trading Bot Started!</b>")
    while True:
        print(f"\n⏱️ New Scan at {datetime.now().strftime('%H:%M:%S')}")
        for symbol in SYMBOLS:
            analyze_symbol(symbol)
            time.sleep(10)
        print("⏳ Waiting 5 minutes...")
        time.sleep(300)
