
import datetime as dt

import numpy as np
import pandas as pd

from remotewind import w
from modules.database_assistant.database_assistant import *

class netval_output:
    """ 读取配置文件并根据其内容提取净值 """
    def __init__(self,netdbdir,ipodate):
        self.netdbdir = netdbdir
        self.ipodate = ipodate

    def take_netvalues(self,startdate=False,enddate=False,freq='DAY',mktidx = None,regmktidx = False):
        """
        提取指定日期内的产品净值
        如果未提供日期，则开始日期设置为ipodae，结束日期设置为 今日
        mktidx 提取指数需要针对各个产品分别提取
        regmktidx 是否需要将指数与净值对齐
        """
        w.start()
        with db_assistant(self.netdbdir) as netdb:
            conn_net = netdb.connection
            if not startdate:
                startdate = self.ipodate.strftime('%Y%m%d')
            if not enddate:
                enddate = dt.datetime.today().strftime('%Y%m%d')
            # 从净值数据库提取日度数据
            data = pd.read_sql(''.join(['SELECT * FROM Net_Values WHERE date >=',startdate,' AND date<=',enddate]),conn_net)
            dates = data['Date']
            head = dates.values[0]    # 所取数据的最早日期
            tail = dates.values[-1]   # 所取数据的最晚日期
            if freq.upper()=='WEEK':
                period='W'
            elif freq.upper()=='MONTH':
                period = 'M'
            else:
                period = 'D'
            ttimes = w.tdays(head,tail,'Period='+period).Times  # head tail 所对应的日期有可能不是交易日
            tperiods = [dt.datetime.strftime(t,'%Y%m%d') for t in ttimes]
            needextra = False
            if (tperiods[0] > head): # 使用周度、月度数据的情况下，确保第一个值为所取数据第一个 交易日
                tmptimes = w.tdays(head,tperiods[0],'Period=D').Times
                head = dt.datetime.strftime(tmptimes[0],'%Y%m%d')  # 将head设置为所提取区间的第一个交易日
                needextra = True
                tperiods.insert(0,head)
            trdidx = dates.isin(tperiods)
            trddata = data[trdidx]
            trddata = trddata.loc[:,['Date','NetSingle','NetCumulated','NetCompensated']]
            trddata.columns = ['日期','单位净值','累计净值','补回净值']
            #  提取指数数据
            if mktidx:
                winddata = w.wsd(mktidx,'close',head,tail,'Period='+period)
                if needextra:
                    windex = w.wsd(mktidx,'close',head,head)
                    exdata = np.array(windex.Data)
                    idxdata = np.row_stack([exdata,np.array(winddata.Data).T])
                else:
                    idxdata = np.array(winddata.Data).T
                if regmktidx:
                    idxdata = idxdata/idxdata[0,:]*trddata['单位净值'].values[0]   # 将指数与净值对齐
                mktidxdata=pd.DataFrame(idxdata,columns=mktidx,index=trddata.index)
                trddata=pd.concat([trddata,mktidxdata],axis=1)
        return trddata
