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
import shelve
import requests
from datetime import datetime, timedelta


MSG_ERR = "Error! "
MSG_REQUEST = "Send Request. Response: {}"
MSG_REQUEST_ERR = MSG_ERR + MSG_REQUEST
MSG_CLIENT = "Client. Response: {} {}"
MSG_CLIENT_ERR = MSG_ERR + MSG_CLIENT
MSG_MARKET = 'Market. Response: {} {}'
MSG_MARKET_ERR = MSG_ERR + MSG_MARKET
MSG_MARKET_LIST = 'is not in the market list: {}'
MSG_POST = 'Send POST: {}'
STOCKS = 'stocks'
ETFS = 'etfs'
BONDS = 'bonds'


class Base(object):

    """ https://tinkoffcreditsystems.github.io/invest-openapi/ """

    def __init__(self,
        db: str = "test.db", token: str = None, account_id: str = None, sandbox: bool = True):

        """ Create new client
        https://tinkoffcreditsystems.github.io/invest-openapi/auth/
        Input:
            token: str, stored in db,
            account_id: str, stored in db,
            db: str, file name for database,
            sandbox: bool
        Output: POST response:
            res.status:200,
            res.headers: {'Server': 'nginx', 'Date': 'Sat, 20 Mar 2021 19:44:56 GMT',
                'Content-Type': 'application/json', 'Transfer-Encoding': 'chunked',
                'Cache-Control': 'no-store, no-cache, must-revalidate',
                'access-control-allow-origin': '*', 'access-control-allow-headers': 'accept,
                content-type, authorization, access-control-allow-headers, x-requested-with',
                'access-control-allow-methods': 'GET,HEAD,POST,DELETE,OPTIONS,PUT,PATCH',
                'content-encoding': 'gzip', 'x-edge-processing-time': '26'}
            res.text: {"trackingId":"db0eb52b6bd1a88d",
                "payload":{"brokerAccountType":"Tinkoff","brokerAccountId":"SB2954177"},
                "status":"Ok"} """

        self.db = shelve.open(db)

        if token:
            self.token = token
            self.db["token"] = token
        else:
            self.token = self.db.get("token")

        if account_id:
            self.account_id = account_id
            self.db["account_id"] = account_id
        else:
            self.account_id = self.db.get("account_id")

        self.last_response = None
        self.api_url = "https://api-invest.tinkoff.ru/openapi"
        self.headers = {'content-type': 'application/json'}
        self.headers.update({"Authorization": "Bearer " + self.token})

        if sandbox:
            self.api_url = self.api_url + "/sandbox"
            url = self.api_url + "/sandbox/register"
            payload = { "brokerAccountType": "Tinkoff" }

            # new clients
            code, res = self._send_request(url, params=None, payload=payload)

            if code == 200:
                print(MSG_CLIENT.format(code, "Ok"))
                self.account_id = json.loads(res).get('payload').get('brokerAccountId')
            else:
                msg = json.loads(res).get('payload').get('message')
                raise Exception(MSG_CLIENT_ERR.format(code, msg))

        else:
            url = self.api_url + "/register"

        # for sandbox: 
        #clear all orders
        #self.client.sandbox.sandbox_clear_post()
        # remove balance
        #self.client.sandbox.sandbox_remove_post()


    def _send_request(self, url: str, params: dict = None, payload: dict = None):

        """ Send POST request
            Input:
                url: str,
                payload: dict
            Output:
                status: int,
                res: str
            How to converddt output(res.text) to dict:
                res['payload']['total'],
                res['payload']['instruments'],
                res['status'])
            response:
                ['apparent_encoding', 'close', 'connection', 'content', 'cookies',
                'elapsed', 'encoding', 'headers', 'history', 'is_permanent_redirect',
                'is_redirect', 'iter_content', 'iter_lines', 'json', 'links',
                'next', 'ok', 'raise_for_status', 'raw', 'reason', 'request',
                'status_code', 'text', 'url'] """

        if payload:
            data = json.dumps(payload)  # to json
            self.last_response = requests.post(url, data=data, headers=self.headers, params=params)
        else:
            self.last_response = requests.get(url, headers=self.headers, params=params)

        try:
            res = (self.last_response.status_code, self.last_response.text)
        except Exception as e:
            raise Exception(MSG_REQUEST_ERR.format(e))

        return res


    def get_user_accounts() -> list:

        """ Get list of user accounts """

        url = self.api_url + "/user/accounts"

        code, res = self._send_request(url)

        if code == 200:
            return json.loads(res).get('payload').get('accounts')
        else:
            msg = json.loads(res).get('payload').get('message')
            raise Exception(MSG_CLIENT_ERR.format(code, msg))


class Market(Base):


    def __init__(self,
        db: str = "test.db", token: str = None, account_id: str = None, sandbox: bool = True):

        super().__init__(db, token, account_id, sandbox)
        self.markets = ("stocks", "etfs", "bonds", "currencies")


    def get_market(self, market: str = None) -> list:

        """ Get all stocks
            Input:
                instrument:
                    'stocks': Output: list of stocks for all currencies,
                    'etfs': Output: list of etfs for all currencies,
                    'bonds': Output: list of bonds for all currencies
            Output:
                res: list = [{}]
            How to converddt output(res.text) to dict:
                res['payload']['total'],
                res['payload']['instruments'],
                res['status']) """

        if not market:
            market = self.markets[0]

        if market in self.markets:
            url = self.api_url + "/market/" + market
        else:
            raise Exception(MSG_MARKET_ERR.format(market, MSG_MARKET_LIST.format(self.markets)))

        code, res = self._send_request(url)
        #return json.loads(res)['payload']['instruments'] if status == 200 else json.loads(res)
        if code == 200:
            return json.loads(res).get('payload').get('instruments')
        else:
            msg = json.loads(res).get('payload').get('message')
            raise Exception(MSG_MARKET_ERR.format(code, msg))


    def get_instruments_by_tickers(self, tickers: tuple, all_instruments: list) -> list:

        """ Get my instruments from all market instruments, create my_instruments.
        Input:
            tickers: tuple = ("T", "F", "AAL"),
            all_instruments: list = self.get_market()
        Output: my_instruments: list = [{
                'currency': 'USD',
                'figi': 'BBG000HLJ7M4',
                'isin': 'US45867G1013',
                'lot': 1,
                'min_price_increment': 0.01,
                'name': 'InterDigItal Inc',
                'ticker': 'IDCC',
                'type': 'Stock'}] """

        my_instruments = []

        for ticker in tickers:
            for instrument in all_instruments:
                if ticker == instrument.get('ticker'):
                    my_instruments.append(instrument)

        return my_instruments


    def get_candles(self,
        instruments: list, depth: int = 1, interval: str = 'day') -> list:

        """ Add candles to list of instruments
            time = 2019-08-19T18:38:33.131642+03:00
        Input:
            instrument: list of my instruments,
            depth: int, days = 1,
            interval: str, candles interval = 2min, 3min, 5min, 10min, 15min, 30min, hour, day, week, month
        Output: instruments: list = [{
                "figi": "BBG000HLJ7M4",
                "ticker": "IDCC",
                "isin": "US45867G1013",
                "min_price_increment": 0.01,
                "lot": 1,
                "currency": "USD",
                "name": "InterDigItal Inc",
                "type": "Stock",
                "candles": [{
                    'c': 67.63,
                    'figi': 'BBG000HLJ7M4',
                    'h': 68.93,
                    'interval': 'day',
                    'l': 66.56,
                    'o': 68.93,
                    'time': datetime.datetime(2021, 3, 18, 4, 0, tzinfo=tzutc()),
                    'v': 30932}"] """

        url = self.api_url + "/market/candles"
        _from = (datetime.utcnow() - timedelta(days=depth)).isoformat() + '+00:00'
        to = datetime.utcnow().isoformat() + '+00:00'
        #params = {"from": _from, "to": to, "interval": interval}

        for instrument in instruments:
            params = {"figi": instrument['figi']}
            params.update({"from": _from, "to": to, "interval": interval})
            code, res = self._send_request(url, params=params)

            if code == 200:
                instrument['candles'] = json.loads(res).get('payload').get('candles')
            else:
                msg = json.loads(res).get('payload').get('message')
                print(MSG_MARKET_ERR.format(code, msg))
                instrument['candles'] = None

        return instruments










