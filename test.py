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
    ./test.py
"""


import sys, json
from orders import Orders
from config import TOKEN, ACCOUNT_ID, MARKET, TICKERS


# enable/disable Traceback
# sys.tracebacklimit = 0


def main():
    print('Initialize client...')
    #client = Orders(TOKEN, ACCOUNT_ID, "test.db")
    client = Orders()
    print('done')
    print('* debug:', client.last_response.url, '\n')

    print('Get list of user accounts... ', end='')
    accounts = client.get_user_accounts()
    print('done', accounts)
    print('* debug:', client.last_response.url, '\n')
    return

    #print('Get stocks... ', end='')
    stocks = client.get_market()
    #print('done', type(stocks), dir(stocks))
    #print(stocks[0])
    #print('* debug:', client.last_response.url, '\n')

    #print('Get instruments... ', end='')
    stocks = client.get_instruments_by_tickers(TICKERS, stocks)
    #print('done', type(stocks), dir(stocks))
    #print(stocks[0])
    #print('* debug:', client.last_response.url, '\n')

    #print('Get prices... ', end='')
    stocks = client.get_candles(stocks, 3, "day")
    #print('done', stocks[0])
    #print('* debug:', client.last_response.url, '\n')

    print('Get operations... ', end='')
    stocks = client.get_operations(stocks)
    #print('done', stocks[0])
    #print('done', json.dumps(stocks[0], indent=4, default=str))
    #print('* debug:', client.last_response.url, '\n')

    #print('Get prices... ', end='')
    stocks = client.get_orders(stocks)
    print('done', stocks[0])
    print('* debug:', client.last_response.url, '\n')

    #print('limit... ', end='')
    #stocks = client.place_limit_order("BBG000HLJ7M4", 1, "Buy",  10)
    #print('done', json.dumps(stocks[0], indent=4, default=str))

if __name__=="__main__":
    #arg=sys.argv[1:]
    main()
