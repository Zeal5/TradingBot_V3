import os, time
from dotenv import dotenv_values
from pybit import usdt_perpetual
from Bybit import Orders
from pprint import pprint

config = dotenv_values(".env")
SYMBOL = 'BTCUSDT'
lprice = float(0)
cprice = float(0)

ws = usdt_perpetual.WebSocket(test=False, api_key=config["A0"], api_secret=config["S0"])


def handle_orderbook(mes):
    global cprice
    d = mes["data"]["mark_price"]
    cprice = float(d)


# ws.instrument_info_stream(handle_orderbook, "BTCUSDT")
# grid_lines = [25000]
# accounts_obj = []
# for i in range(len(grid_lines)):
#     accounts_obj.append(
#         Orders(i, api_key=config["A0"], api_secret=config["S0"], symbol=SYMBOL
#                ,stoploss_percentage=0.5,profit_percentage=10,)
#     )
active_positions = {
        "A0": 
                {"long":False,
                 "short":False}
}
                    

def pos(mes):
    new_pos = mes['data']
    pprint(mes)



#order execution stream
ws.execution_stream(callback=pos)
while True:
    time.sleep(1)
    

    # if cprice != lprice:

    #     print(rf"{cprice:.2f} / {lprice:.2f}   {(cprice - (lprice )):.2f}   ", end="\r")

    #     for i in grid_lines:
    #         try:
    #             if cprice >= i > lprice or lprice > i >= cprice:
    #                 print(f"Trade at {i} {(cprice - lprice)} ")
    #         except TypeError:
    #             pass
    #     lprice = cprice
    # else:
    #     time.sleep(0.1)
