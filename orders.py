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


from market import Market
from datetime import datetime, timedelta
from itertools import zip_longest as zip


MSG_ERR = "Error! "
MSG_OPERATIONS = 'Operations. Response: {}'
MSG_OPERATIONS_ERR = MSG_ERR + MSG_OPERATIONS
MSG_ORDERS = 'Operations. Response: {}'
MSG_ORDERS_ERR = MSG_ERR + MSG_OPERATIONS
MSG_PLACE_ORDER = "Operation should be {} instead of {}"

class Operations(Market):

    def __init__(self,
        db: str = "test.db", token: str = None, account_id: str = None, sandbox: bool = True):

        super().__init__(db, token, account_id, sandbox)


    def get_operations(self,
        depth: int = 365,
        instruments: list = None,
        figi:str = None,
        account_id: str = None):

        """ Add operations to the list instruments or get all operations in one request
            Input:
                instruments: list of instruments,
                depth: days from today,
                figi: str, not implemented yet! The definition of this argument has is irrelevant,
                account_id: str, optional
            Output:
                list or error message string """

        url = self.api_url + "/operations"
        _from = (datetime.utcnow() - timedelta(days=depth)).isoformat() + '+03:00'
        to = datetime.utcnow().isoformat() + '+03:00'
        params = {"from": _from, "to": to}
        if account_id:
            params.update({"brokerAccountId": account_id})

        if not instruments:
            res = self._send_request(url, params=params)

            return res.get('payload').get('operations') if isinstance(res, dict) else res

        # TODO
        if figi:
            pass

        for instrument in instruments:
            params.update({"figi": instrument['figi']})
            res = self._send_request(url, params=params)

            instrument['operations'] = (
                res.get('payload').get('operations') if isinstance(res, dict) else res)

        return instruments


    def get_portfolio(self, account_id: str = None):

        """ Get client's portfolio,
        Output: list of dict of the opened positions
            or error message string """

        url = self.api_url + "/portfolio"
        params = {"brokerAccountId": account_id} if account_id else None

        res = self._send_request(url, params=params)

        return res.get('payload').get('positions') if isinstance(res, dict) else res


class Orders(Operations):

    def __init__(self,
        db: str = "test.db", token: str = None, account_id: str = None, sandbox: bool = True):

        super().__init__(db, token, account_id, sandbox)


    def get_orders(self, instruments: list = None, account_id: str = None):

        """ Add active orders to list of instruments
        Input:
            instruments: list, optional,
            account_id: str, optional
        Output:
            expected result: list,
                instruments['orders'] list or list of dict of the opened positions
            or error message string """

        url = self.api_url + "/orders"
        params = {"brokerAccountId": account_id} if account_id else None

        res = self._send_request(url)

        if isinstance(res, str):
            return res

        orders_list = res.get('payload')

        if instruments:
            for instrument in instruments:
                instrument['orders'] = []
                for order in orders_list:
                    if instrument.get('figi') == order.get('figi'):
                        instrument['orders'] = order

            return instruments
        return orders_list


    def place_order(self,
        figi: str,
        lots: int,
        op: str,
        price: float,
        account_id: str = None):

        """ Place limit order
        Input:
            "figi:, str,
            "lots": int,
            "op": str, "Buy" or "Sell",
            "price": float, for limit orders, optional
            account_id: str, optional
        Output:
            expected type dict, str with an error message """

        ops = ("Buy", "Sell")
        if op not in ops:
            msg = MSG_PLACE_ORDER.format(ops, op)
            return MSG_ORDERS_ERR.format(msg)

        url = self.api_url + "/orders/market-order"
        params = {"figi": figi}
        #params.update{"brokerAccountId": account_id}) if account_id else None
        if account_id:
            params.update({"brokerAccountId": account_id})
        payload = {"lots": lots, "operation": op}
        if price:
            url = self.api_url + "/orders/limit-order"
            payload.update({"price": price})
        res = self._send_request(url, params=params, payload=payload)

        return res.get('payload') if isinstance(res, dict) else res


    def cancel_order(self, order_id: str, account_id: str = None):

        """ Cancel order
        Input:
            order_id: str,
            account_id: str, optional
        Output:
            expected type dict, str with an error message """

        url = self.api_url + "/orders/cancel"
        params = {"orderId": order_id}
        if account_id:
            params.update({"brokerAccountId": account_id})

        res = self._send_request(url, params=params)

        return res.get('payload') if isinstance(res, dict) else res















