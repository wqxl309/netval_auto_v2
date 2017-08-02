
import numpy as np


class indicators:
    """ 根据净值 计算各种指标的类 """
    freq_dict = {'DAY':250,'D':250,'WEEK':52,'W':52,'MONTH':12,'M':12}
    indicator_dict = {
        '年化收益率':'annret',
        '年化波动率':'annvol',
        '最大回撤':'maxdd',
        '夏普比率':'sharpe',
        '卡玛比率':'calmar',
        '索提诺比率':'sortino',
        '詹森指数':'jensen',
        '特雷诺指数':'treynor',
        '期间收益率':'inret',
        '信息系数':'ic',
        '信息比率':'ir',
    }

    def __init__(self,valueinfo,indicator_list,freq):
        rf = valueinfo.get('riskfreerate')
        if rf:
            self.rf = rf # 无风险利率
        else:
            self.rf = 0
        self.freq = freq.upper()  # 日 周 月
        self.orders = [(ind,indicators.indicator_dict[ind]) for ind in indicator_list]   # 需要计算的指标,(中文，英文)
        self.valueinfo = valueinfo
        self._netvals = np.array(valueinfo['netvals'])
        self._size = self._netvals.shape
        self._netrets = self._netvals[1:,:]/self._netvals[:-1,:]-1
        # 常用指标 必须计算
        self._annret = self.calc_annret()
        self._annvol = self.calc_annvol()
        self._maxdd = self.calc_maxdd()
        # 是否需要计算 CAPM
        if ('詹森指数' in indicator_list) or ('特雷诺指数' in indicator_list) or ('信息比率' in indicator_list):
            self.capm_paras = self.calc_CAPM()

    def take_orders(self):
        delivery = {}
        for item in self.orders:
            if item[1] in ['maxdd','annret','annvol']:
                delivery[item[0]] = eval(''.join(['self._',item[1]]))
            else:
                delivery[item[0]] = eval(''.join(['self.calc_',item[1],'()']))
        return delivery

    def calc_inret(self):
        return self._netvals[-1,:]/self._netvals[0,:]-1

    def calc_annret(self):
        return np.mean(self._netrets,axis=0)*indicators.freq_dict[self.freq]

    def calc_annvol(self):
        return np.std(self._netrets,axis=0,ddof=1)*np.sqrt(indicators.freq_dict[self.freq])

    def calc_anndownvol(self):
        downrets=np.zeros_like(self._netrets,dtype=np.float)
        idx = self._netrets<0
        downrets[idx] = self._netrets[idx]
        return np.std(downrets,axis=0,ddof=1)*np.sqrt(indicators.freq_dict[self.freq])

    def calc_maxdd(self):
        maxnet = np.zeros([1,self._size[1]])
        drawdowns = np.zeros_like(self._netvals,dtype=np.float)
        for dumi in range(self._size[0]):
            idx = self._netvals[dumi,:]>maxnet
            maxnet[:,idx[0]] = self._netvals[dumi,idx[0]]
            drawdowns[dumi,:] = self._netvals[dumi,:]/maxnet[:,:]-1
        return np.min(drawdowns,axis=0)

    def calc_sharpe(self):
        return (self._annret-self.rf)/self._annvol

    def calc_calmar(self):
        return -(self._annret-self.rf)/self._maxdd

    def calc_sortino(self):
        return (self._annret-self.rf)/self.calc_anndownvol()

    def calc_jensen(self):
        return self.capm_paras['beta']*indicators.freq_dict[self.freq]

    def calc_treynor(self):
        return (self._annret-self.rf)/self.capm_paras['alpha']

    def calc_ic(self):
        benchnet = np.array(self.valueinfo.get('benchmark'))
        if benchnet is None:
            raise Exception('No benchmark is provided, can not calc IC !')
        benchret = benchnet[1:]/benchnet[:-1]-1
        retmat = np.column_stack([benchret,self._netrets])-self.rf
        coeffmat = np.corrcoef(retmat,rowvar=False)
        return np.transpose(coeffmat[1:,0])

    def calc_ir(self):
        ir = np.mean(self.capm_paras['res'],axis=0)/np.std(self.capm_paras['res'],axis=0,ddof=1)
        return ir

    def calc_winloss_recorders(self):
        wins = np.ones([1,self._size[1]])
        loss = np.ones([1,self._size[1]])
        maxwin = np.ones([1,self._size[1]])
        maxlos = np.ones([1,self._size[1]])
        for dumi in range(self._size[0]):
            if dumi>0 and dumi<self._size[0]-1:
                winstop = np.all([self._netrets[dumi-1,:]>0 , self._netrets[dumi,:]<=0],axis=0)
                losstop = np.all([self._netrets[dumi-1,:]<0 , self._netrets[dumi,:]>=0],axis=0)
                wins[:,winstop] = 1  # 每次停止后需要重置为1
                loss[:,losstop] = 1  # 每次停止后需要重置为1
                wins = wins+np.all([self._netrets[dumi,:]>0 , self._netrets[dumi-1,:]>0],axis=0)*1
                loss = loss+np.all([self._netrets[dumi,:]<0 , self._netrets[dumi-1,:]<0],axis=0)*1
                newwin = wins>maxwin
                newlos = loss>maxlos
                maxwin[:,newwin[0]] = wins[:,newwin[0]]
                maxlos[:,newlos[0]] = loss[:,newlos[0]]
        return {'maxwinsnum':maxwin[0,:] , 'maxlossnum':maxlos[0,:]}

    def calc_CAPM(self):
        benchnet = np.array(self.valueinfo.get('benchmark'))
        if benchnet is None:
            raise Exception('No benchmark is provided, can not calc CAPM !')
        benchret = benchnet[1:]/benchnet[:-1]-1
        x = np.column_stack([benchret-self.rf,np.ones_like(benchret)])
        y = self._netrets-self.rf
        inv1 = np.linalg.inv(np.dot(x.transpose(),x))
        paras = np.dot(np.dot(inv1,x.transpose()),y)
        residual = y - np.dot(x,paras)
        return {'alpha':paras[1,:],'beta':paras[0,:],'res':residual}
