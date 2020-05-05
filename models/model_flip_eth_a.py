# !/usr/bin/env python
import os
import sys
import json
import requests

discount = 0.15
PERCENT = 0


def calculate_value(value: int, percent):
    percent_value = int(value * percent / 100)
    return value + percent_value


def get_price():
    resp = requests.get('https://api.coingecko.com/api/v3/simple/price',
                        params={'ids': 'ethereum', 'vs_currencies': 'usd'})
    return calculate_value(resp.json()['ethereum']['usd'], PERCENT)


for line in sys.stdin:
    signal = json.loads(line)
    if signal['guy'] == os.environ['ACCOUNT_ADDRESS']:
        continue
    oracle = get_price()
    stance = {'price': oracle * (1 - discount)}
    print(json.dumps(stance), flush=True)
