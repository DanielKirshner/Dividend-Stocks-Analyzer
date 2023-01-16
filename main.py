import yfinance
import traceback
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
            self._price = self._ticker.info['currentPrice']
            self._sector = self._ticker.info['sector']
            self._industry = self._ticker.info['industry']
            self._dividend_yield = self._ticker.info.get('dividendYield', 0)
            self._payout_ratio = self._ticker.info['payoutRatio']
            if self._payout_ratio is not None:
                self._payout_ratio = round(self._payout_ratio * 100, 1)
            self._beta = round(self._ticker.info['beta'], 2)
            self._market_cap = self._ticker.info['marketCap']
            self._chowder = round(self._dividend_yield * 100, 2) + self._avg_dividend_growth


    def _load_dividend_data(self):
        """
        _summary_
        Loads the dividend data into our list. 
        """
        for i, dividend_value in enumerate(self._ticker.dividends):
            if dividend_value > 0.01: # This is because the information that yfinance provides us begins to falter a bit as we run back in time.
                self._dividends.append(Dividend(self._ticker.dividends.index[i], dividend_value))


    def _evaluate_dividend_streak(self):
        """
        _summary_
        Check for how long the company gives stable dividends, and for how long they increase dividends.
        """
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
        """
        _summary_
        Calculate the average yearly dividend increase for the stock.
        """
        changes = 0
        for i, d in enumerate(self._dividends):
            if d.timestamp.year > 2005: # This is because the information that yfinance provides us begins to falter a bit as we run back in time.
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
        """
        _summary_
        Calculate the 'Return On Equity' of the stock
        Returns:
            Any (int or float): ROE
        """
        stockholder_equity = [v['Total Stockholder Equity']
                              for v in self._ticker.balance_sheet.to_dict().values()]
        net_income = [v['Net Income']
                      for v in self._ticker.financials.to_dict().values()]
        return sum([x / y for x, y in zip(net_income, stockholder_equity)]) / len(stockholder_equity)


    def _evaluate_pe_ratio(self):
        """_summary_
        Calculate the estimated value of the average between the trailingPE and the forwardPE
        Returns:
            Any (Probably float or double): P/E ratio of the stock.
        """
        pes = [self._ticker.info.get('trailingPE'), self._ticker.info.get('forwardPE')]
        num = 0
        total = 0
        for pe in pes:
            if pe is not None:
                total += pe
                num += 1
        if num == 0:
            return 0
        return total / num
    
    
    def is_interesting_stock(self):
        """
        Returns:
            Boolean : Is the stock interesting? (According to my parameters...)
        """
        return self._dividend_yield >= 0.02 and self._dividend_increase_since <= 2007 and \
            self._chowder >= 9 and self._roe >= 15 and self._payout_ratio <= 60 and \
            self._market_cap >= 2000000000 and self._beta <= 1 and self._pe <= 40


TICKERS = [
    'MSFT',
    'AAPL',
]

def main():
    for i, ticker in enumerate(TICKERS):
        print(f'Processing {ticker} ({i}/{len(TICKERS)})')
        try:
            s = Stock(ticker)
            if s.is_interesting_stock():
                 print(f'{ticker} is interesting!')
        except Exception as e:
            traceback.print_exc()


if __name__ == "__main__":
    main()
