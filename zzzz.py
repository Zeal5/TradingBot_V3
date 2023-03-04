from Bybit import Orders
from dotenv import dotenv_values
from pybit import usdt_perpetual
from Bybit import Orders, logger
from pprint import pprint


config = dotenv_values(".env")


a = Orders(
        name=f"A", api_key=config[f"A0"], api_secret=config[f"S0"]
    )

print(a.active_orders("AKROUSDT"))


"""long position with sl
conditional active orders
{'base_price': '0.005963',
 'close_on_trigger': True,
 'created_time': '2023-03-04T00:11:46Z',
 'order_link_id': '',
 'order_status': 'Untriggered',
 'order_type': 'Market',
 'price': 0,
 'qty': 100,
 'reduce_only': True,
 'side': 'Sell',
 'sl_trigger_by': 'UNKNOWN',
 'stop_loss': 0,
 'stop_order_id': '79c38e94-71d7-4270-8078-0dcb088fe358',
 'symbol': 'AKROUSDT',
 'take_profit': 0,
 'time_in_force': 'ImmediateOrCancel',
 'tp_trigger_by': 'UNKNOWN',
 'trigger_by': 'LastPrice',
 'trigger_price': 0.0057,
 'updated_time': '2023-03-04T00:11:46Z',
 'user_id': 39337790}
{'Buy': False, 'Sell': True}
"""
"""conditional long 
conditional active orders
{'base_price': '0.006020',
 'close_on_trigger': False,######
 'created_time': '2023-03-04T00:15:53Z',
 'order_link_id': '',
 'order_status': 'Untriggered',
 'order_type': 'Market',
 'price': 0,
 'qty': 100,
 'reduce_only': False,#####
 'side': 'Buy',
 'sl_trigger_by': 'UNKNOWN',
 'stop_loss': 0,
 'stop_order_id': '6376bb74-4477-4ab1-8745-ced5b49f17c6',
 'symbol': 'AKROUSDT',
 'take_profit': 0,
 'time_in_force': 'ImmediateOrCancel',
 'tp_trigger_by': 'UNKNOWN',
 'trigger_by': 'LastPrice',
 'trigger_price': 0.006205,
 'updated_time': '2023-03-04T00:15:53Z',
 'user_id': 39337790}
 """