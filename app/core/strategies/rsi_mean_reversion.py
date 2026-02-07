from app.core.strategies.base import BaseStrategy
import talib

class RSIMeanReversion(BaseStrategy):
    rsi_period = 14
    rsi_oversold = 30
    rsi_overbought = 70

    def init(self):
        self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_period)

    def next(self):
        if self.rsi[-1] < self.rsi_oversold:
            if not self.position:
                self.buy()
        elif self.rsi[-1] > self.rsi_overbought:
            if self.position:
                self.position.close()
