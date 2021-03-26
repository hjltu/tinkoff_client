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
MSG_REQUEST = "Send Request. Response: {} {}"
MSG_REQUEST_ERR = MSG_ERR + MSG_REQUEST
MSG_CLIENT = "Client. Response: {}"
MSG_CLIENT_ERR = MSG_ERR + MSG_CLIENT
MSG_SANDBOX = "New sandbox client is created"
MSG_DB_WARN = "This value is not stored in the db yet"
MSG_TOKEN = "Token is:"
MSG_ACCOUNT_ID = "Account ID is {}:"
MSG_MARKET = 'Market. Response: {}'
MSG_MARKET_ERR = MSG_ERR + MSG_MARKET
MSG_MARKET_LIST = ' {} is not in the market list: {}'
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

        # token and account id stored in db
        self.db = db
        self.token = self._add_to_db("token", token)
        self.account_id = self._add_to_db("account_id", account_id)

        if not self.token:
            raise Exception(MSG_CLIENT_ERR.format(MSG_TOKEN, self.token))

        self.last_response = None
        self.api_url = "https://api-invest.tinkoff.ru/openapi"
        self.headers = {'content-type': 'application/json'}
        self.headers.update({"Authorization": "Bearer " + self.token})

        if sandbox:
            self.api_url = self.api_url + "/sandbox"
            url = self.api_url + "/sandbox/register"
            payload = { "brokerAccountType": "Tinkoff" }

            # new clients
            res = self._send_request(url, params=None, payload=payload)

            if isinstance(res, dict):
                self.account_id = res.get('payload').get('brokerAccountId')
            else:
                raise Exception(MSG_CLIENT_ERR.format(MSG_ACCOUNT_ID, self.account_id))

            print(MSG_CLIENT.format(MSG_SANDBOX))

        print(MSG_CLIENT.format(MSG_ACCOUNT_ID.format(self.account_id)))


    def _send_request(self,
        url: str,
        params: dict = None,
        payload: dict = None,
        timeout: int = 11):

        """ Send POST request
            Input:
                url: str,
                params: dict,
                payload: dict,
                timeout: int, seconds, optional,
            Output:
                status: int,
                res: list/dict/str, expected type dict, str with an error message
            dir request response:
                ['apparent_encoding', 'close', 'connection', 'content', 'cookies',
                'elapsed', 'encoding', 'headers', 'history', 'is_permanent_redirect',
                'is_redirect', 'iter_content', 'iter_lines', 'json', 'links',
                'next', 'ok', 'raise_for_status', 'raw', 'reason', 'request',
                'status_code', 'text', 'url'] """

        code, res, msg = None, None, None

        try:
            if payload:
                data = json.dumps(payload)  # to json
                self.last_response = requests.post(url, data=data, headers=self.headers, params=params, timeout=timeout)
            else:
                self.last_response = requests.get(url, headers=self.headers, params=params, timeout=timeout)

            code, res = self.last_response.status_code, json.loads(self.last_response.text)
        except Exception as e:
            return MSG_REQUEST_ERR.format(code, e)

        if code != 200:
            msg = res.get('payload').get('message')
            return MSG_REQUEST_ERR.format(code, msg)

        return res


    def get_user_accounts(self):

        """ Get list of user accounts
        Output: list, [{
            "brokerAccountType": "Tinkoff",
            "brokerAccountId": "string" }] """

        url = self.api_url + "/user/accounts"

        res = self._send_request(url)

        return res.get('payload').get('accounts') if isinstance(res, dict) else res


    def _add_to_db(self, key, val=None):

        """ Add new value to persistent data storage,
            new value stored in db as dict { key : val }
        Input:
            key: str, new key,
            val:new value
        Output: new value or None """

        with shelve.open(self.db) as db:
            if val:
                db[key] = val
            val = db.get(key)

        return val if val else None


    def _get_from_db(self, val):

        """ Get value or all values from db """

        with shelve.open(self.db) as db:
            return db.get(val)


class Market(Base):


    def __init__(self,
        db: str = "test.db", token: str = None, account_id: str = None, sandbox: bool = True):

        super().__init__(db, token, account_id, sandbox)
        self.markets = ("stocks", "etfs", "bonds", "currencies")


    def get_market(self, market: str = None) -> list:

        """ Get all stocks
            Input:
                market: str,
                    'stocks': Output: list of stocks for all currencies,
                    'etfs': Output: list of etfs for all currencies,
                    'bonds': Output: list of bonds for all currencies
            Output:
                res: list = [{}] """

        if not market:
            market = self.markets[0]

        if market in self.markets:
            url = self.api_url + "/market/" + market
        else:
            return MSG_MARKET_ERR.format(
                MSG_MARKET_LIST.format(market, self.markets))

        res = self._send_request(url)

        return res.get('payload').get('instruments') if isinstance(res, dict) else res


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
        instruments: list, depth: int = 30, interval: str = 'month'):

        """ Add candles to list of instruments
            time = 2019-08-19T18:38:33.131642+03:00
        Input:
            instrument: list of my instruments,
            depth: int, days = 1, e.g if interval = weeks then days should be = 7, 30 for month,
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
        params = {"from": _from, "to": to, "interval": interval}

        for instrument in instruments:
            params.update({"figi": instrument['figi']})
            #params.update({"from": _from, "to": to, "interval": interval})
            res = self._send_request(url, params=params)

            instrument['candles'] = (
                res.get('payload').get('candles') if isinstance(res, dict)  else res)

        return instruments











