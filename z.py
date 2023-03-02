import os
import time
from dotenv import dotenv_values
from pybit import usdt_perpetual
from Bybit import Orders, logger

config = dotenv_values(".env")
CP = 0
LP = 0
# accounts to be used by this script .env should have all accounts
GRID = range(0, 2)
TICKER = "BTCUSDT"
QTY = 0.001
ENTRIES = [15_000]
STOP_LOSS = 0.5 / 100
active_positions = {"A0": {"Buy": False, "Sell": False}}
active_orders = {"A0": {"Buy": False, "Sell": False}}


def update_active_orders():
    for account_name, account_instance in accounts_dict.items():
        active_orders[account_name] = account_instance.active_orders(TICKER)


def initiaize_account_instance() -> dict:
    """Based on GRID= range(number of accounts) global variable creates account instances
    in accounts_dict"""

    accounts_dict = {}
    for i in GRID:
        accounts_dict[f"A{i}"] = Orders(
            name=f"A{i}", api_key=config[f"A{i}"], api_secret=config[f"S{i}"]
        )
    for account_name, account_instance in accounts_dict.items():
        active_positions[f"{account_name}"] = account_instance.open_positions(TICKER)

    return accounts_dict


def initialize_execution_stream() -> dict:
    """Initialize executions streams for all accounts when new positions is opend/closed
    update active_positons dict to see if new position has been opened or closed in which account"""

    def positions(account, mes):
        ticker = mes["data"][0]["symbol"]
        active_positions[account] = accounts_dict[account].open_positions(ticker)
        active_orders[account] = accounts_dict[account].active_orders(TICKER)

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
    ws.instrument_info_stream(price_update, TICKER)
    logger.info(f"A0 account being used for price streaming")


def open_positions():
    for i in range(len(ENTRIES)):
        if ENTRIES[i] < CP and (
            active_orders[f"A{i}"]["Buy"] == False
            or active_orders[f"A{i}"]["Sell"] == False
        ):
            if (
                active_positions[f"A{i}"]["Buy"] == False
                and active_orders[f"A{i}"]["Buy"] == False
            ):
                if (
                    accounts_dict[f"A{i}"].long_order(
                        TICKER, ENTRIES[i], QTY, stop_loss=(STOP_LOSS)
                    )
                    == True
                ):
                    active_orders[f"A{i}"]["Buy"] = True
                else:
                    logger.error(
                        f"Failed to set long order for account A{i} at {ENTRIES[i]}"
                    )

            if (
                active_positions[f"A{i}"]["Sell"] == False
                and active_orders[f"A{i}"]["Sell"] == False
            ):
                if (
                    accounts_dict[f"A{i}"].conditional_short(
                        TICKER, ENTRIES[i], QTY, stop_loss=(STOP_LOSS)
                    )
                    == True
                ):
                    active_orders[f"A{i}"]["Sell"] = True
                else:
                    logger.error(
                        f"Failed to set conditional short order for account A{i} at {ENTRIES[i]}"
                    )

        if ENTRIES[i] > CP and (
            active_orders[f"A{i}"]["Buy"] == False
            or active_orders[f"A{i}"]["Sell"] == False
        ):
            if (
                active_positions[f"A{i}"]["Buy"] == False
                and active_orders[f"A{i}"]["Buy"] == False
            ):
                if (
                    accounts_dict[f"A{i}"].conditional_long(
                        TICKER, ENTRIES[i], QTY, stop_loss=(STOP_LOSS)
                    )
                    == True
                ):
                    active_orders[f"A{i}"]["Buy"] = True
                else:
                    logger.error(
                        f"Failed to set long order for account A{i} at {ENTRIES[i]}"
                    )

            if (
                active_positions[f"A{i}"]["Sell"] == False
                and active_orders[f"A{i}"]["Sell"] == False
            ):
                if (
                    accounts_dict[f"A{i}"].short_order(
                        TICKER, ENTRIES[i], QTY, stop_loss=(STOP_LOSS)
                    )
                    == True
                ):
                    active_orders[f"A{i}"]["Sell"] = True
                else:
                    logger.error(
                        f"Failed to set conditional short order for account A{i} at {ENTRIES[i]}"
                    )


accounts_dict = initiaize_account_instance()
initialize_execution_stream()
current_market_price()
update_active_orders()

while True:
    if CP != LP:
        print(f"cp = {CP} / lp = {LP} {active_orders} {active_positions}", end="\r")
        open_positions()

        LP = CP
