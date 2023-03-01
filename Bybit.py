from pybit import usdt_perpetual
from pprint import pprint
import pybit.exceptions
import logging

# stop imported moduels from logging
logging.getLogger().setLevel(logging.WARNING)
for handler in logging.getLogger().handlers:
    handler.setLevel(logging.WARNING)


# logging.basicConfig(
#     level=logging.INFO,
#     filename="Live_Positions.log",
#     format="%(levelname)s - %(asctime)s -  %(message)s",
#     datefmt="%m-%d %H:%M:%S",
# )
#initiate custom moduel
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('Live_Positions.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Orders:
    """Creates an Instance for all accounts \n\n
    name = account name\n
    long/short_tp == is actuall price for tps\n
    stop_loss is in% term from entries is fixed for all entries"""

    def __init__(
        self,
        name,
        api_key: str,
        api_secret: str,

    ):
        self.session = usdt_perpetual.HTTP(
            endpoint="https://api.bybit.com", api_key=api_key, api_secret=api_secret
        )
        self.name = str(name)
        logger.info(f'{self.name} account initiated')

       
    def __str__(self) -> str:
        return f"Account {(self.name).upper()}"

    def get_market_price(self,ticker) -> float:
        """returns market price for trading pair"""
        data = self.session.latest_information_for_symbol(symbol=ticker)
        return float(data["result"][0]["last_price"])

    def set_cross_margin(self,ticker):
        """Change Margin mode to Cross with 10x levrage"""
        margin = None
        try:
            margin = self.session.cross_isolated_margin_switch(
                symbol=ticker,
                is_isolated=False,
                buy_leverage=10,
                sell_leverage=10,
            )

        except pybit.exceptions.InvalidRequestError as e:
            logger.error(f"Check {self}'s margin Possibly it was already cross 10x")

        if margin:
            if margin["ext_code"] == "" or margin["ret_code"] == 0:
                logger.info(f"{self} Margin has been changed to cross")
            else:
                logger.error(f"Check {self}'s margin {{ {margin} }}")
            
    def open_positions(self,ticker):
        """Returns all active orders by default API returns buy and sell orders So,
        if size != 0 returns True else False\n
        Sets cross levrage automatically if is_isolated is true"""

        positions = self.session.my_position(symbol=ticker)["result"]
        if positions[0]['is_isolated']== True:
            self.set_cross_margin()



        position = {"Buy": False, "Sell": True}

        position[positions[0]["side"]] = True if positions[0]["size"] != 0 else False
        position[positions[1]["side"]] = True if positions[1]["size"] != 0 else False
        return position

    def active_orders(self,ticker):
        """Returns all limit orders in place"""
        limit_orders = self.session.get_active_order(symbol=ticker)["result"][
            "data"
        ]
        conditional_orders = self.session.get_conditional_order(symbol=ticker)[
            "result"
        ]["data"]
        active_limit_orders = {
            i["order_id"]: {
                "Symbol": i["symbol"],
                "side": i["side"],
                "status": i["order_status"],
                "price": i["price"],
                "tp": i["take_profit"],
                "sl": i["stop_loss"],
            }
            for i in limit_orders
            if i["order_status"] == "New"
        }

        active_conditional_orders = {
            i["stop_order_id"]: {
                "Symbol": i["symbol"],
                "side": i["side"],
                "status": i["order_status"],
                "price": i["price"],
                "tp": i["take_profit"],
                "sl": i["stop_loss"],
            }
            for i in conditional_orders
            if i["order_status"] == "Untriggered"
        }
        active_limit_orders.update(active_conditional_orders)
        # return all active_orders
        return active_limit_orders

    def short_order(self,ticker, entry_price: float, qty,short_tp,stop_loss) -> bool:
        """places short order takes in entry price"""
        try:
            short = self.session.place_active_order(
                symbol=ticker,
                side="Sell",
                order_type="Limit",
                qty=qty,
                price=entry_price,
                reduce_only=False,
                close_on_trigger=False,
                time_in_force="GoodTillCancel",
                take_profit=short_tp if short_tp else '',
                stop_loss=entry_price + (entry_price * stop_loss),
            )
        except pybit.exceptions.InvalidRequestError as e:
            logger.error(f"({self}) has raised an exception {{ {e} }}")
            return False

        if short["ext_code"] == "" or short["ret_code"] == 0:
            logger.info(f"{self} Limit short has been set at {entry_price} tp:{short_tp if short_tp else ''}/sl:{entry_price + (entry_price * stop_loss)}")
            return True

    def long_order(self,ticker, entry_price: float,qty,stop_loss,long_tp = None) -> bool:
        """Places long order takes in entry price for placing a long order"""
        
        try:
            long = self.session.place_active_order(
                symbol=ticker,
                side="Buy",
                order_type="Limit",
                qty=qty,
                price=entry_price,
                time_in_force="GoodTillCancel",
                reduce_only=False,
                close_on_trigger=False,
                take_profit= long_tp if long_tp else '',
                stop_loss= entry_price - (entry_price * stop_loss),
            )

        except pybit.exceptions.InvalidRequestError as e:
            logger.error(f"({self}) has raised an exception {{ {e} }}")
            return False

        if long["ext_code"] == "" or long["ret_code"] == 0:
            logger.info(f"{self} Limit Long has been set at {entry_price} tp:{long_tp if long_tp else ''}/sl:{entry_price - (entry_price * stop_loss)}")
            return True

    def conditional_long(self,ticker, entry_price: float,qty,stop_loss,long_tp=None) -> bool:
        """Place conditional orders AKA longs above market price"""
        try:
            long = self.session.place_conditional_order(
                symbol=ticker,
                order_type="Market",
                side="Buy",
                qty=qty,
                # base price is compared to stop_px to figure out if the order will be triggerd by price crossing from upper side or lower side
                base_price=self.get_market_price(),
                stop_px=entry_price,
                time_in_force="GoodTillCancel",
                trigger_by="LastPrice",
                reduce_only=False,
                close_on_trigger=False,
                stop_loss=entry_price - (entry_price * stop_loss),
                take_profit=long_tp if long_tp else '',
            )

        except pybit.exceptions.InvalidRequestError as e:
            logger.error(f"({self}) has raised an exception {{ {e} }}")
            return False
        if long["ext_code"] == "" or long["ret_code"] == 0:
            logger.info(f"{self} Limit Long has been set at {entry_price} tp:{long_tp if long_tp else ''}/sl:{entry_price - (entry_price * stop_loss)}")

    def conditional_short(self,ticker, entry_price: float,qty,stop_loss,short_tp) -> bool:
        """Place conditional orders AKA shorts below market price"""
        try:
            short = self.session.place_conditional_order(
                qty=qty,
                symbol=ticker,
                order_type="Market",
                side="Sell",
                # base price is compared to stop_px to figure out if the order will be triggerd by price crossing from upper side or lower side
                base_price=self.get_market_price(),
                stop_px=entry_price,
                time_in_force="GoodTillCancel",
                trigger_by="LastPrice",
                reduce_only=False,
                close_on_trigger=False,
                stop_loss=entry_price + (entry_price * stop_loss),
                take_profit=short_tp if short_tp else '',
            )
        except pybit.exceptions.InvalidRequestError as e:
            logger.error(f"({self}) has raised an exception {{ {e} }}")
            return False
        if short["ext_code"] == "" or short["ret_code"] == 0:
            logger.info(f"{self} Limit Short has been set at {entry_price} tp:{short_tp if short_tp else ''}/sl:{entry_price + (entry_price * stop_loss)}")
