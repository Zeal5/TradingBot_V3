from Bybit import Orders
from dotenv import dotenv_values
import re


config = dotenv_values(".env")

# p = 0.06925
# a = re.findall('([\d+]*)(\.)([\d+]*)',str(p))
# b = len(str(a[0][2]))
# print(round(p +(p*0.005),b))
# print(p +(p*0.005))
GRID = range(0,4)

total_trades = 0




def what():
    total_trades += 23

what()
print(total_trades)