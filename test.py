#!/usr/bin/env python3
# 22jan21 hjltu@ya.ru
# Copyright (c) 2020 hjltu

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""
test.py
Usage:
    ./test.py api_token
    ./test.py
"""


import sys, json
from orders import Orders
from config import TOKEN, ACCOUNT_ID, MARKET, TICKERS, Style


# enable/disable Traceback
sys.tracebacklimit = 0
MAX_ATTEMPT = 3

def handle_error(func):
    def wrapper(*args, **kwargs):
        attempt = 0
        print('Send request, attempt: ', end='', flush=True)
        while attempt < MAX_ATTEMPT:
            attempt += 1
            print(f'{attempt} ', end='', flush=True)
            res = func(*args, **kwargs)
            if isinstance(res, dict) or isinstance(res, list):
                break
        return res
    return wrapper

@handle_error
def exec_function(func):
    return func


def main(token=TOKEN):
    print('Initialize client...')
    # First time run, will save token in the db
    if token:
        client = Orders(db="test.db", token=token, account_id=ACCOUNT_ID)
    # if token is already saved in the db
    else:
        client = Orders()
    print(Style.BOLD + Style.GREEN + 'done' + Style.RESET)
    print('* debug:', client.last_response.url, '\n')

    print("get token:", client._get_from_db("token"))
    print("get account_id:", client._get_from_db("account_id"))

    print('Get list of user accounts... ', end='', flush=True)
    accounts = exec_function(client.get_user_accounts())
    print('result:', accounts)
    if isinstance(accounts, list):
        for acc in accounts:
            print('done\nAccount ID:', acc.get('brokerAccountId'))
    print('* debug:', client.last_response.url, '\n')

    print('Get list of currency assets... ', end='', flush=True)
    currencies = exec_function(client.get_currencies())
    print('done:', currencies)
    if isinstance(currencies, list):
        for curr in currencies:
            print(f'currency: {curr}')
    print('* debug:', client.last_response.url, '\n')

    print('Get stocks... ', end='', flush=True)
    stocks = exec_function(client.get_market('stocks'))
    if isinstance(stocks, list):
        print(stocks[0])
    else:
        return print(stocks)

    print('Get instruments... ', end='', flush=True)
    stocks = client.get_instruments_by_tickers(TICKERS, stocks)
    print('done', json.dumps(stocks[0], indent=4, default=str))
    print('* debug:', client.last_response.url, '\n')

    print('Get candles... ', end='', flush=True)
    stocks = client.get_candles(stocks, 14, "week")
    print('done', stocks[0])
    print('* debug:', client.last_response.url, '\n')

    print('Get operations... ', end='', flush=True)
    stocks = client.get_operations(99, stocks)
    print('done', stocks[0])
    print('* debug:', client.last_response.url, '\n')

    print('Get portfolio... ', end='', flush=True)
    pos = client.get_portfolio()
    print('done', pos[0]) if len(pos)>0 else print('done positions list len:', len(pos))
    print('* debug:', client.last_response.url, '\n')

    print('Get orders... ', end='', flush=True)
    stocks = client.get_orders(stocks)
    print('done', stocks[0])
    print('* debug:', client.last_response.url, '\n')

    print('Place order... ', end='', flush=True)
    order = client.place_order("BBG000HLJ7M4", 1, "Buy",  10)
    print('done', order)

    print('Cancel order... ', end='', flush=True)
    order = client.cancel_order(order.get('orderId'))
    print('done', order)



if __name__=="__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        main()
