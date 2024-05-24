import pandas as pd
import matplotlib.pyplot as plt


def return_not_null(data: pd.DataFrame, col_index) -> pd.DataFrame:
    if not isinstance(col_index, list):
        col_index = [col_index]
    for i in col_index:
        data = data[data[i].notnull()]
    return data


def show_pds(pds: pd.DataFrame, out_y: list):
    '''

    :param pds: 输入数组
    :param out_y: 对应的折线图列
    :return:
    '''
    plt.rc("font", family="DengXian")
    plt.rcParams["axes.unicode_minus"] = False
    title = pds.iloc[:, 0]
    plt.figure(figsize=(16, 8))
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    if len(colors) <= len(out_y):
        raise '输出折线图条数不能大于7'
    for i in out_y:
        color = colors.pop()
        y = pds[i]
        plt.plot(title, y, '-%s' % color, color=color, label=i)
    plt.legend(loc='best')
    plt.grid(True)
    plt.xlabel('cards')
    plt.ylabel('数值')
    plt.title('对应cards造成的期望结果')
    plt.xticks(rotation=90, fontsize=8)
    plt.show()


def get_pd_whool_one_col(data) -> pd.DataFrame:
    '''
    加一列全是1的列。方便出图的时候可以将数据样本数加上
    :param data:
    :return:
    '''
    new_column = pd.Series(1, index=data.index)
    data = data.assign(count=new_column)
    return data


def sign_blind_level(blinds: list) -> str:
    '''
    将底池级别转化
    :param blinds:
    :return:
    '''
    return '_'.join(map(lambda x: str(int(x//100)), blinds))
