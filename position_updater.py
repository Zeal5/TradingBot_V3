import os, time
from dotenv import load_dotenv
from pybit import usdt_perpetual
from pprint import pprint
load_dotenv()

API = os.getenv("API_KEY")
SECRET = os.getenv("API_SECRET")

lprice = None
cprice = None
ws = usdt_perpetual.WebSocket(test=True, api_key=API, api_secret=SECRET)

def handle_orderbook(mes):
    global cprice
    d = mes['data']['mark_price']
    cprice = d

ws.instrument_info_stream(handle_orderbook, "BTCUSDT")

while True:
    if cprice:
        print(cprice, lprice)
        lprice = cprice
    time.sleep(0.3)