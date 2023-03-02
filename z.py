import os, time
from dotenv import dotenv_values
from pybit import usdt_perpetual
from Bybit import Orders, logger
from pprint import pprint

config = dotenv_values(".env")
CP = 0
LP = 0
# accounts to be used by this script .env should have all accounts
GRID = range(0, 2)
TRADE = {"BTCUSDT": []}
active_positions = {"A0": {"Buy": False, "Sell": False}}
active_orders = {}
def update_active_orders():
    for account_name, account_instance in accounts_dict.items():
        active_orders[account_name] = account_instance.active_orders("BTCUSDT")

def initiaize_account_instance() -> dict:
    """Based on GRID= range(number of accounts) global variable creates account instances
    in accounts_dict"""

    accounts_dict = {}
    for i in GRID:
        accounts_dict[f"A{i}"] = Orders(
            name=f"A{i}", api_key=config[f"A{i}"], api_secret=config[f"S{i}"]
        )
    for account_name, account_instance in accounts_dict.items():
        active_positions[f"{account_name}"] = account_instance.open_positions("BTCUSDT")

    return accounts_dict
    
def initialize_execution_stream() -> dict:
    """Initialize executions streams for all accounts when new positions is opend/closed
    update active_positons dict to see if new position has been opened or closed in which account"""

    def positions(account, mes):
        ticker = mes["data"][0]["symbol"]
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

def current_market_price() -> None:
    """instrument stream to open web_socket which keeps updating CP global variable"""

    def price_update(message):
        global CP
        CP = float(message["data"]["mark_price"])

    ws = usdt_perpetual.WebSocket(
        test=False, api_key=config[f"A{GRID[0]}"], api_secret=config[f"S{GRID[0]}"]
    )
    ws.instrument_info_stream(price_update, "BTCUSDT")
    logger.info(f"A0 account being used for price streaming")

accounts_dict = initiaize_account_instance()
initialize_execution_stream()
current_market_price()
update_active_orders()
while True:
    time.sleep(1)
    if CP != LP:
        print(f"cp = {CP} / lp = {LP} {active_orders}", end="\r")
        LP = CP
