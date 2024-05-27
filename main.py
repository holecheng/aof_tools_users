# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import json
import os
import asyncio
import pandas as pd
import datetime

from handler import TimeStrategy, get_analysis, PlayerStrategy, InsuranceStrategy
from utils.utils import sign_blind_level

file_path = os.path.dirname(os.path.abspath(__file__))
os.chdir('/')


def ac_to_excel(pds: pd.DataFrame, df_path, suffix='all'):
    pds.to_excel('./output/' + os.path.basename(df_path).split('.')[0]
                 + '_' + suffix + '.xlsx', sheet_name='data', index=False)


async def pd_node(path):
    '''
    基础功能将所有的数字以列的形式显示成excel方便进一步分析
    :param path: 输入路径
    :return:hand_number_pd: 对桌号去重的pd  pd_data： 全量PD

    dic结构 flop_insurance 与 turn_insurance 为牌型对应的领先保险 leader_index为领先的hero_index
    '''
    with open(path) as json_file:
        pd_data = []
        pd_title = []
        for line in json_file:
            line = json.loads(line)
            if not pd_data:
                pd_title = list(line.keys())
            current_row = []
            dic = {'card_list': [], 'pid_list': [], 'hero_index': None,
                   'flop_insurance': None, 'turn_insurance': None, 'leader_index': None,
                   'card_leader': False, 'pid': None, 'card': None}
            for i in pd_title:
                if i == 'players':
                    players = line[i]
                    for p in range(len(players)):
                        player = players[p]
                        # 有牌处理 无牌
                        dic['card_list'].append(player.get('cards'))
                        dic['pid_list'].append(player.get('pId'))
                        flop_insurance = player.get('flopInsurance')
                        turn_insurance = player.get('turnInsurance')
                        if flop_insurance and flop_insurance[0].get('betStacks') > 0:
                            dic['flop_insurance'] = flop_insurance[0].get('betStacks')
                            dic['leader_index'] = int(p)
                        if turn_insurance and turn_insurance[0].get('betStacks') > 0:
                            dic['turn_insurance'] = turn_insurance[0].get('betStacks')
                            dic['leader_index'] = int(p)  # todo 如果需要排除异常数据在此处理
                if i == 'timestamp':
                    current_row.append(datetime.datetime.fromtimestamp(line.get(i)))
                elif i == 'blindLevel':
                    current_row.append(sign_blind_level(line.get(i)['blinds']))
                else:
                    current_row.append(line.get(i))
                if i == 'heroIndex':
                    dic['hero_index'] = line.get(i)
                    if line.get(i) != -1:
                        dic['card'] = dic['card_list'][line.get(i)]
                        dic['pid'] = dic['pid_list'][line.get(i)]
                        if line.get(i) == dic['leader_index']:
                            dic['card_leader'] = True
                elif i in ['ev', 'outcome']:
                    hero_index = dic.get('hero_index', '')
                    dic[i] = float(line.get(i)[hero_index]) if hero_index != -1 else ''
            card = dic.get('card')
            if card:
                a, b = max(card[0], card[2]), min(card[0], card[2])
                current_row.append('%s%s' % (a, b))
            current_row += [card, dic['ev'], dic['outcome'], dic['pid'], dic['card_leader']]
            if dic['card_leader']:
                current_row += [dic['turn_insurance'], dic['flop_insurance'],]
            pd_data.append(current_row)
        pd_data = pd_data
        df_name = './' + os.path.basename(path).split('.')[0] + '.xlsx'
        output = os.sep.join([file_path, 'output', df_name])
        pd_data = pd.DataFrame(pd_data)
        pd_data.columns = pd_title + ['card_num', 'card', 'ev_player', 'outcome_player',
                                      'pid', 'card_leader', 'flop_insurance', 'turn_insurance']
        pd_data.to_excel(output, sheet_name='data', index=False)
        return pd_data


if __name__ == '__main__':
    import argparse

    config_path = os.sep.join([file_path, 'config.json'])
    parser = argparse.ArgumentParser(description='传递参数')
    parser.add_argument('--time', type=str, nargs='?', help='起始时间')
    parser.add_argument('--player', type=str, nargs='?', help='玩家pid')
    parser.add_argument('--flop', type=str, nargs='?', help='flop保险')
    parser.add_argument('--turn', type=str, nargs='?', help='turn保险')
    parser.add_argument('--path', type=str, nargs='?', help='文件路径')
    normal_col = ['ev_player', 'outcome_player', 'handNumber', 'card_num']  # 局内基本信息
    args = parser.parse_args()
    start_time = end_time = player_id = flop = turn = path = None
    if args.time:
        start_time, end_time = args.time.strip().split(',')
        normal_col.append('timestamp')
        print('正在处理 {} 到 {} 时间内的数据'.format(start_time, end_time))
    if args.player:
        player_id = args.player
        normal_col.append('pid')
    if args.flop:
        flop = args.flop
        normal_col.append('flop_insurance')
    if args.turn:
        turn = args.turn
        normal_col.append('turn_insurance')
    if args.path:
        path = args.path
    df_list = []
    with open(config_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
    if config.get('mode') == 'dev':
        if 'dev_data_path' not in config:
            raise '不存在本地路径'
        dir_path = file_path + os.sep + config['dev_data_path']
    else:
        if 'abs_path' not in config and not path:
            raise '不存在有效路径'
        else:
            dir_path = path or config.get('mode')
    if os.path.exists(dir_path):
        for root, dirs, files in os.walk(dir_path):
            if dirs:
                continue
            for file in files:
                if file.startswith('aof'):
                    df_list.append(os.path.join(root, file))
    else:
        raise '{}不是有效文件'.format(dir_path)
    if not df_list:
        exit()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = [pd_node(df_path) for df_path in df_list]
    results = loop.run_until_complete(asyncio.gather(*tasks))
    for i in range(len(results)):
        result = results[i]
        df_path = df_list[i]
        normal_data = result.loc[:, normal_col]
        ans_data = normal_data
        if start_time or end_time:
            ans_data = get_analysis(TimeStrategy(), ans_data, start_time=start_time, end_time=end_time)
        if player_id:
            ans_data = get_analysis(PlayerStrategy(), ans_data, player_id=player_id)
        if flop or turn:
            ans_data = get_analysis(InsuranceStrategy(), ans_data, flop=flop, turn=turn)
        ac_to_excel(ans_data, df_path, 'ans')
        ac_to_excel(normal_data, df_path, 'normal')
        ac_to_excel(result, df_path)







