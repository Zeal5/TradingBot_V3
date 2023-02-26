import os, time
from dotenv import dotenv_values
from pybit import usdt_perpetual
from Bybit import Orders,logger
from pprint import pprint
import websocket

config = dotenv_values(".env")
SYMBOL = 'BTCUSDT'
ws_dict = {}


for i in range(2):
    ws = usdt_perpetual.WebSocket(test=False, api_key=config[f"A{i}"], api_secret=config[f"S{i}"])
    ws_dict[f'A{i}'] = ws

active_positions = {
        "A0": 
                {"long":False,
                 "short":False}
}
                    
def pos(account,mes):
    pprint(f"account {account} message = { mes}")

print(ws_dict)
for account,ws_obj in ws_dict.items():
    #order execution stream
    ws_obj.execution_stream(callback=lambda data: pos(account,data))
    logger.info(f"{account} stream initiated")

while True:
    time.sleep(1)