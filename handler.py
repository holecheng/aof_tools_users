from datetime import datetime

from pandas import DataFrame

from strategy import Strategy
import pandas as pd


# class GroupStrategy(Strategy):
#     def cleaning(self, data: pd.DataFrame, group=0, args=None, group_type='mean') -> pd.DataFrame:
#         # todo 建议暂时用一行分组，不然显示图片会出问题 暂时不用此策略
#         domain = {}
#         if not isinstance(group, list):
#             group = [group]
#         args = args if args else [data.columns[1]]
#         for arg in args:
#             domain.update({arg: group_type})
#
#         print(data.columns, group)
#         data = data.groupby('card_num', as_index=False).agg(domain)
#         print(data)
#         # data['card_num'] = data.apply(lambda x: x['card_num'] + '(' + str(x['count']) + ')', axis=1)
#         # show_pds(data, group[0], args)
#         return data


class TimeStrategy(Strategy):
    # 针对时间做数据清洗
    def cleaning(self, data: pd.DataFrame, start_time=None, end_time=datetime.now().strftime("%Y-%m-%d")):
        if start_time:
            data = data[data['timestamp'] >= start_time]
        if end_time:
            data = data[data['timestamp'] <= end_time]
        return data


class PlayerStrategy(Strategy):
    # 针对时间做数据清洗
    def cleaning(self, data: pd.DataFrame, player_id=None):
        if player_id is not None:
            data = data[data['player_id'] == player_id]
        return data


class InsuranceStrategy(Strategy):
    def cleaning(self, data: pd.DataFrame, turn=None, flop=None):
        turn, flop = int(turn) if turn else None, int(flop) if turn else None
        data = data[data['turn_insurance'].notnull() | data['flop_insurance'].notna()]
        if turn:
            data = data[(data['turn_insurance'].notnull() & data['turn_insurance'] > turn) | data['flop_insurance']]
        if flop:
            data = data[(data['flop_insurance'].notnull() & data['flop_insurance'] > flop) | data['turn_insurance']]
        return data


class PdAnalysis:
    def __init__(self, strategy: Strategy, pds: pd.DataFrame):
        self.strategy = strategy
        self.pds = pds

    def clean_pds(self, **kwargs) -> pd.DataFrame:
        return self.strategy.cleaning(self.pds, **kwargs)


def get_analysis(strategy: Strategy, pds: pd.DataFrame, **kwargs) -> DataFrame:
    return PdAnalysis(strategy, pds).clean_pds(**kwargs)










