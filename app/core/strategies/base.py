from backtesting import Strategy
from abc import ABC, abstractmethod

class BaseStrategy(Strategy, ABC):
    """Base class for pre-built strategies"""

    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def next(self):
        pass
