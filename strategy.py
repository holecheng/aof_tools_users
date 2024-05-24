from abc import ABC, abstractmethod
import pandas as pd
import matplotlib.pyplot as plt


class Strategy(ABC):
    '''
    定义清洗策略
    '''

    @abstractmethod
    def cleaning(self, pd_data: pd.DataFrame, **kwargs):
        pass



