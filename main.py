import yfinance
from collections import namedtuple

Dividend = namedtuple('Dividend', 'timestamp value')


class Stock(object):
    def __init__(self, ticker):
        self._name = ticker.upper()
        self._ticker = yfinance.Ticker(self._name)
        self._dividends = []
        self._load_dividend_data()

        self._dividend_stable_since = None
        self._dividend_increase_since = None
        self._evaluate_dividend_streak()
        self._avg_dividend_growth = 0
        self._evaluate_dividend_growth()

        # Convert ROE to percentage
        self._roe = round(self._evaluate_roe() * 100, 2)
        self._pe = round(self._evaluate_pe_ratio(), 2)

    def _load_dividend_data(self):
        for i, dividend_value in enumerate(self._ticker.dividends):
            if dividend_value > 0.01:
                self._dividends.append(
                    Dividend(self._ticker.dividends.index[i], dividend_value))

    def _evaluate_dividend_streak(self):
        last_increase = self._dividends[0]
        last_dividend = self._dividends[0].value
        self._dividend_stable_since = self._dividends[0]
        self._dividend_increase_since = self._dividends[0]
        for d in self._dividends[1:]:
            if d.value < last_dividend:
                self._dividend_stable_since = d
                self._dividend_increase_since = d
            elif d.value == last_dividend:
                elapsed = (d.timestamp - last_increase.timestamp).days
                if elapsed > 400:
                    self._dividend_increase_since = d
            else:
                last_increase = d
            last_dividend = d.value

    def _evaluate_dividend_growth(self):
        changes = 0
        for i, d in enumerate(self._dividends):
            if d.timestamp.year > 2005:
                last_dividend = d
                first_index = i
                break
        for d in self._dividends[first_index + 1:]:
            if (d.timestamp - last_dividend.timestamp).days > 400:
                self._avg_dividend_growth += d.value / last_dividend.value
                changes += 1
                last_dividend = d
        self._avg_dividend_growth /= changes
        self._avg_dividend_growth = round(
            (self._avg_dividend_growth - 1) * 100, 2)

    def _evaluate_roe(self):
        stockholder_equity = [v['Total Stockholder Equity']
                              for v in self._ticker.balance_sheet.to_dict().values()]
        net_income = [v['Net Income']
                      for v in self._ticker.financials.to_dict().values()]
        return sum([x / y for x, y in zip(net_income, stockholder_equity)]) / len(stockholder_equity)

    def _evaluate_pe_ratio(self):
        pes = [self._ticker.info.get(
            'trailingPE'), self._ticker.info.get('forwardPE')]
        num = 0
        total = 0
        for pe in pes:
            if pe is not None:
                total += pe
                num += 1
        if num == 0:
            return 0
        return total / num