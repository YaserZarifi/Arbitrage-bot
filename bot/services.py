# bot/services.py

import ccxt
import requests
from decimal import Decimal, getcontext
from django.conf import settings
from .models import PriceData
from prometheus_client import Counter, Gauge


OPPORTUNITIES_FOUND = Counter(
    'arbitrage_opportunities_found_total',
    'Total number of arbitrage opportunities found'
)
# A gauge to track the last observed price difference.
PRICE_DIFFERENCE = Gauge(
    'price_difference_gauge',
    'The last observed price difference percentage between exchanges'
)









# Set precision for decimal calculations
getcontext().prec = 30

def send_telegram_notification(message):
    """
    Sends a message to a Telegram user or group.
    """
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    # Construct the API URL
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    # Construct the payload
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        print("Telegram notification sent successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Telegram notification: {e}")


def fetch_and_store_prices():
    """
    Connects to exchanges, fetches prices, stores them, and sends a notification
    if an arbitrage opportunity is found.
    """
    # ... (the ccxt initialization part is the same as before) ...
    binance = ccxt.binance({'apiKey': settings.BINANCE_API_KEY, 'secret': settings.BINANCE_SECRET_KEY, 'options': {'recvWindow': 10000}})
    gateio = ccxt.gateio({'apiKey': settings.GATEIO_API_KEY, 'secret': settings.GATEIO_SECRET_KEY})
    symbol = 'BTC/USDT'

    try:
        binance_ticker = binance.fetch_ticker(symbol)
        gateio_ticker = gateio.fetch_ticker(symbol)

        binance_price = Decimal(binance_ticker['last'])
        gateio_price = Decimal(gateio_ticker['last'])

        if gateio_price > 0:
            difference = ((binance_price - gateio_price) / gateio_price) * Decimal(100)
        else:
            difference = Decimal(0)

        price_record = PriceData.objects.create(
            currency_pair=symbol,
            binance_price=binance_price,
            gateio_price=gateio_price,
            price_difference_percent=difference
        )
        
        PRICE_DIFFERENCE.set(float(difference)) # Set the gauge to the current difference

        print(f"Saved: Binance={binance_price}, Gate.io={gateio_price}, Diff={difference:.2f}%")


        # --- NOTIFICATION LOGIC ---
        # Check if the absolute difference is greater than a threshold (e.g., 1%)
        if abs(difference) > 0.01:

            OPPORTUNITIES_FOUND.inc()

            # Create the notification message
            message = (
                f"🚨 *Arbitrage Alert!* 🚨\n\n"
                f"**Symbol:** `{symbol}`\n"
                f"**Profit:** `{abs(difference):.2f}%`\n\n"
            )


            # Determine buy/sell exchanges and format the rest of the message
            if difference > 0: # Binance price is higher, so sell on Binance
                message += (
                    f"-> *Buy on Gate.io:* `${gateio_price:,.2f}`\n"
                    f"-> *Sell on Binance:* `${binance_price:,.2f}`"
                )
            else: # Gate.io price is higher, so sell on Gate.io
                message += (
                    f"-> *Buy on Binance:* `${binance_price:,.2f}`\n"
                    f"-> *Sell on Gate.io:* `${gateio_price:,.2f}`"
                )

            # Send the notification
            send_telegram_notification(message)

        return price_record

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
