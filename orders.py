#!/usr/bin/env python3
# 17mar21 hjltu@ya.ru
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

import json
from market import Market
from config import Style
from datetime import datetime, timedelta
from itertools import zip_longest as zip


MSG_ERR = "Error! "
MSG_OPERATIONS = 'Market. Response: {} {}'
MSG_OPERATIONS_ERR = MSG_ERR + MSG_OPERATIONS


class Operations(Market):

    def __init__(self,
        token: str = None, account_id: str = None, db: str = "test.db", sandbox: bool = True):

        super().__init__(token, account_id, db, sandbox)


    def get_operations(self,
        instruments: list, depth: int = 365,
        figi:str = None, account_is: str = None, for_all_instruments: bool = False):

        """ Get list of operations. Does not work!
            Input:
                instruments: list of instruments,
                depth: days from today,
                for_all: bool, for all instruments in one request
            Output:
                instruments
            Not required parameters:
                figi: str,
                brokerAccountId: str = self.account_id
            response:
                {"trackingId":"246c007a49a6e1d1","payload":{"operations":[]},"status":"Ok"} """

        url = self.api_url + "/operations"
        _from = (datetime.utcnow() - timedelta(days=depth)).isoformat() + '+03:00'
        to = datetime.utcnow().isoformat() + '+03:00'
        params = {"from": _from, "to": to}

        if for_all_instruments:
            code, res = self._send_request(url, params=params)

            if code == 200:
                return json.loads(res)['payload']['operations']
            else:
                msg = json.loads(res)['payload']['message']
                raise Exception(MSG_OPERATIONS_ERR.format(code, msg))

        for instrument in instruments:
            params.update({"figi": instrument['figi']})
            code, res = self._send_request(url, params=params)

            if code == 200:
                instrument['operations'] = json.loads(res)['payload']['operations']
            else:
                msg = json.loads(res)['payload']['message']
                print(MSG_OPERATIONS_ERR.format(code, msg))
                instrument['operations'] = None

        return instruments


    def get_portfolio(self, account_id: str = None):

        """ Get client's portfolio """

        url = self.api_url + "/portfolio"
        params = {"brokerAccountId": account_id} if account_id else None

        code, res = self._send_request(url, params=params)

        if code == 200:
            return json.loads(res).get('payload').get('positions')
        else:
            msg = json.loads(res).get('payload').get('message')
            raise Exception(MSG_OPERATIONS_ERR.format(code, msg))


class Orders(Operations):

    def __init__(self,
        token: str = None, account_id: str = None, db: str = "test.db", sandbox: bool = True):

        super().__init__(token, account_id, db, sandbox)


    def get_orders(self, instruments: list):

        """ Add active orders to list of instruments """

        url = self.api_url + "/orders"
        code, res = self._send_request(url)

        if code == 200:
            orders_list = json.loads(res)['payload']
            for instrument in instruments:
                instrument['orders'] = []
                for order in orders_list:
                    if instrument['figi'] == order['figi']:
                        instrument['orders'] = order
        else:
            msg = json.loads(res)['payload']['message']
            raise Exception(MSG_OPERATIONS_ERR.format(code, msg))

        return instruments


    def place_limit_order(self, figi, lots, op, price):

        """ Place limit order
        limit_order_request: {
            "lots": 0,
            "operation": "Buy",
            "price": 0
        } """

        #res = client.orders.orders_limit_order_post(figi, limit_order_request)
        limit_request = '{"lots": '+str(lots)+', "operation": '+op+', "price": '+str(price)+'}'
        res = self.client.orders.orders_limit_order_post(figi, json.dumps(limit_request))
        #res = self.client.orders.orders_limit_order_post(figi, (lots, op, price))


    def place_market_order(self):

        """ Place market order """

        res = client.orders.orders_market_order_post(figi, market_order_request)
















