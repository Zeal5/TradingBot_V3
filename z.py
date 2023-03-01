import os, time
from dotenv import dotenv_values
from pybit import usdt_perpetual
from Bybit import Orders, logger
import logging
from pprint import pprint


config = dotenv_values(".env")
GRID = 2
# {ticker:(grid entries,tp)}
TRADE = {"BTCUSDT": []}
active_positions = {"A0": {"long": False, "short": False}}


def initiaize_account_instance() -> dict:
    accounts_dict = {}
    for i in range(GRID):
        accounts_dict[f"A{i}"] = Orders(
            name=f"A{i}", api_key=config[f"A{i}"], api_secret=config[f"S{i}"]
        )

    return accounts_dict

accounts = initiaize_account_instance()

def initialize_execution_stream():
    def positions(account, mes):
        print(f"{account}")
        pprint(mes)

    def wrapper(account):
        return lambda data: positions(account, mes=data)

    ws_dict = {}
    account_dict = {}
    for i in range(GRID):
        ws = usdt_perpetual.WebSocket(
            test=False, api_key=config[f"A{i}"], api_secret=config[f"S{i}"]
        )
        ws_dict[f"A{i}"] = ws

    for account, ws_obj in ws_dict.items():
        # order execution stream
        ws_obj.execution_stream(callback=wrapper(account))
        logger.info(f"{account} stream initiated")

    return ws_dict

initialize_execution_stream()
CP = 0
LP = 0
def current_market_price():
    def price_update(message):
        global CP
        CP = float(message['data']['mark_price'])

    ws = usdt_perpetual.WebSocket(test=False, api_key=config["A0"], api_secret=config["S0"])
    ws.instrument_info_stream(price_update, "BTCUSDT")
    logger.info(f'A0 account being used for price streaming')

current_market_price()

while True:
    time.sleep(1)
    if CP != LP:
        print(f'cp = {CP} / lp = {LP}')
        LP = CP
    
