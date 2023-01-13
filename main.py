import yfinance
from collections import namedtuple

Dividend = namedtuple('Dividend', 'timestamp value')


class Stock(object):
    def __init__(self, ticker):
        self._name = ticker.upper()
        self._ticker = yfinance.Ticker(self._name)
        self._dividends = []
