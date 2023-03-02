from Bybit import Orders
from dotenv import dotenv_values
import re


config = dotenv_values(".env")

ENTRIES = [15_000.123,20_000]
# get decimal digit count for better print
regex_pattern = re.findall('([\d+]*)(\.)([\d+]*)',str(float(ENTRIES[0])))
formate_int = len(str(regex_pattern[0][2]))


print(round(10.123,formate_int))