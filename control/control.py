from queryhandler.timeshandler import TimeHandler


class Control:
    '''
    操作工厂：
    由此工厂进行下一步操作的转发
    '''
    def __init__(self, options, factor=None):
        self.options = options
        self.factor = factor
        if self.options == 'query':
            # 用作查询需要显示的东西
            if self.factor == 'time':
                time_handler = TimeHandler()



