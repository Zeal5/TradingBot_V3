from Bybit import Orders
from dotenv import dotenv_values
import re


# config = dotenv_values(".env")

# i = 1
# a = Orders(name=f"A", api_key=config[f"A{i}"], api_secret=config[f"S{i}"])

# print(a.open_positions("BTCUSDT"))

p = 0.06925
a = re.findall('([\d+]*)(\.)([\d+]*)',str(p))
b = len(str(a[0][2]))
print(round(p +(p*0.005),b))
print(p +(p*0.005))