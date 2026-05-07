from abc import abstractmethod
from hft.strategies.base_strategy import BaseStrategy

class BaseFuturesStrategy(BaseStrategy):
    def __init__(self, name, description, contract_symbol='ES'):
        super().__init__(name, description)
        self.contract_symbol = contract_symbol
    
    def get_parameters(self):
        pass
