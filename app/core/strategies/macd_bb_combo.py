from app.core.strategies.base import BaseStrategy
import talib

class MACDBBCombo(BaseStrategy):
    """
    Combined strategy using MACD and Bollinger Bands
    - Buy when price is below lower band AND MACD histogram turns positive
    - Sell when price is above upper band OR MACD histogram turns negative
    """
    macd_fast = 12
    macd_slow = 26
    macd_signal = 9
    bb_period = 20
    bb_std = 2

    def init(self):
        close = self.data.Close
        self.macd, self.macd_signal, self.macd_hist = self.I(
            talib.MACD, close, self.macd_fast, self.macd_slow, self.macd_signal
        )
        self.upper, self.middle, self.lower = self.I(
            talib.BBANDS, close, self.bb_period, self.bb_std, self.bb_std
        )

    def next(self):
        price = self.data.Close[-1]

        # Buy signal
        if not self.position:
            if price < self.lower[-1] and self.macd_hist[-1] > 0 and self.macd_hist[-2] <= 0:
                self.buy()

        # Exit signal
        else:
            if price > self.upper[-1] or self.macd_hist[-1] < 0:
                self.position.close()

    def set_params(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
