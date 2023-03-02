import os, time
from dotenv import dotenv_values
from pybit import usdt_perpetual
from Bybit import Orders, logger
from pprint import pprint

config = dotenv_values(".env")
# accounts to be used by this script .env should have all accounts
GRID = range(0,2)
TRADE = {"BTCUSDT": []}
active_positions = {"A0": {"long": False, "short": False}}

def initiaize_account_instance() -> dict:
    accounts_dict = {}
    for i in GRID:
        accounts_dict[f"A{i}"] = Orders(
            name=f"A{i}", api_key=config[f"A{i}"], api_secret=config[f"S{i}"]
        )
    for account_name,account_instance in accounts_dict.items():
        active_positions[f'{account_name}'] =  account_instance.open_positions("BTCUSDT")
    

    return accounts_dict

accounts_dict = initiaize_account_instance()

def initialize_execution_stream():
    def positions(account, mes):
        ticker = mes['data'][0]['symbol']
        active_positions[account] = accounts_dict[account].open_positions(ticker)

    def wrapper(account):
        return lambda data: positions(account, mes=data)

    ws_dict = {}
    account_dict = {}
    for i in GRID:
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
        CP = float(message["data"]["mark_price"])

    ws = usdt_perpetual.WebSocket(
        test=False, api_key=config[f"A{GRID[0]}"], api_secret=config[f"S{GRID[0]}"]
    )
    ws.instrument_info_stream(price_update, "BTCUSDT")
    logger.info(f"A0 account being used for price streaming")

current_market_price()

while True:
    time.sleep(1)
    if CP != LP:
        print(f"cp = {CP} / lp = {LP} {active_positions}",end='\r')
        LP = CP
