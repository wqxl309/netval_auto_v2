import datetime as dt

import numpy as np
import pandas as pd
from pandas.io import sql
from remotewind import w

from modules.database_assistant.database_assistant import *

class netvalues_calculation:
    """ 根据 netvalues_base 里面提取出的基础数据计算产品净值 """
    def __init__(self,pname,netdbdir,confirmdays,precision):
        self.pname = pname
        self.netdbdir = netdbdir
        self.confirmdays = confirmdays
        self.precision = precision

    def generate_netvalues(self,earnvars = ['earn']):
        """ 从头计算净值表，包括全部日期（包含非交易日） 暂时未考虑融券情况 """
        digits = self.precision
        confirmdays = self.confirmdays
        w.start()
        with db_assistant(self.netdbdir) as netdb:
            conn_net = netdb.connection
            basedata = pd.read_sql('SELECT * FROM Net_Values_Base',conn_net)  #提取基础数据
            sorteddata = basedata.sort_values(['date'],ascending=[1])     # 将数据根据日期排序，防止有些估值表发送较晚，更新靠后的情况
            # 检查缺失交易日期，如果有缺失则只生成至缺失交易日前一（交易）日； 有交易日就应该有估值表，反之不然
            alldates = sorteddata['date']
            firstdate = alldates.values[0]   # 基础数据起始日 须确保基础数据中没有重复项
            lastdate = alldates.values[-1]   # 基础数据结束日
            tdays = w.tdays(firstdate,lastdate).Times  # 期间交易日
            trddays = pd.DataFrame([dt.datetime.strftime(t,'%Y%m%d') for t in tdays])
            misstrd = ~trddays.isin(alldates.values)
            trdmiss = trddays[misstrd.values]  # 期间缺失的交易日
            if not trdmiss.empty:
                # 截止到第一个缺失交易日前的一个交易日
                #cutdate=dt.datetime.strftime(w.tdaysoffset(-1,trdmiss.values[0][0]).Times[0],'%Y%m%d')
                cutdate = dt.datetime.strftime(w.tdaysoffset(-1,trdmiss.values[0][0]).Times[0],'%Y%m%d')
                cutpos = alldates<=cutdate    # 需要提取的日期的位置
                sorteddata = sorteddata[cutpos]
            dates = sorteddata['date']
            datenum = dates.__len__()
            # 处理 融券的字段
            if 'secloan' not in sorteddata.columns:
                sorteddata['secloan'] = 0
            if 'fee_secloan' not in sorteddata.columns:
                sorteddata['fee_secloan'] = 0
            # 计算实际付费 出入金 -- 费用为每日计提，累计显示，因而是逐渐增加的，如果一次减小说明当日支付上一付费季度的费用
            fees = -(sorteddata.loc[:,['fee_service','fee_keep','fee_management','fee_secloan']+earnvars].diff())  #正常日计提 作差为正数，实际支付 作差为负数，取反则可以找到实际支付
            fees[fees<0] = 0   # 将正常每日费用计提设为0
            fees.iloc[0,:] = 0   # diff 导致第一行为NaN 需要填补为0
            paid=fees.sum(axis=1)  # 将每日各项费用加总，计算每日（账面）支付金额
            ###################　开始计算净值  #######################
            netreal=sorteddata['assetnet']/sorteddata['sharenum'] # 计算真实(单位)净值
            # 计算将业绩提成补回后的（累计）净值收益率
            bookearns = sorteddata.loc[:,earnvars].diff()   # 账面业绩提成，不是实际支付的 与fees['earn']  是不一样的！！！
            bookearns.iloc[0,:] = 0
            bookearns[bookearns<0] = 0
            bookearn = bookearns.sum(axis=1)
            net_addearn = (sorteddata['assetnet']+bookearn)/sorteddata['sharenum']
            cumret = net_addearn.values[1:]/netreal.values[:-1]-1
            cumret = np.row_stack([np.zeros([1,1]),np.reshape(cumret,[datenum-1,1])])
            netcum = np.cumprod(1+cumret)*netreal[0]  # 计算补回业绩提成后的（累计）单位净值,并确保初始值与单位净值初始值对齐
            # 在有申购赎回的时候需要采取平滑处理
            sharechg = sorteddata['sharenum'].diff() # 计算份额变动差异 >0 为由申购， <0 为有赎回，有可能申赎数量相同，但不影响金额
            sharechg[0] = 0
            # 和前一个数值相比, 确定 confirm date 交易确认日 (T+C) 的位置
            idxchg_TC = sharechg!=0 # type: pd.DataFrame
            chgpos_TC = idxchg_TC[idxchg_TC].index  # 变动位置的序号
            chgdate = dates[chgpos_TC].values # 变动位置的对应的日期
            opendate = [w.tdaysoffset(-confirmdays,c).Times[0].strftime('%Y%m%d') for c in chgdate]
            openidx = dates.isin(opendate)  # 开放日位置
            inout = np.zeros_like(netreal)
            inout[chgpos_TC] = np.round(netreal[openidx].values,digits)*sharechg[chgpos_TC].values  # 将单位净值round到指定位置，乘以分额变动计算出在开放日申购赎回的金额
            # 提取 开放日 到 确认日 期间的日期（TCm1）对应的位置，并在相应位置对应上申购赎回的金额
            inout2 = np.zeros_like(netreal)
            idxchg_TCm1 = np.zeros_like(netreal)
            opennum = 0
            opentot = opendate.__len__()
            for dumi in range(datenum):  # 将日期一个个与开放日比对
                if opennum>=opentot:      # 已经找到的开放日数量超过了所有 开放日数量，说明已经完成，可以退出了
                    break
                mydt = dates.values[dumi]
                if mydt>opendate[opennum] and mydt<chgdate[opennum]:
                    inout2[dumi] = inout[chgpos_TC[opennum]]
                    idxchg_TCm1[dumi] = 1
                elif mydt>=chgdate[opennum]:
                    opennum += 1

            amtchg = np.zeros_like(netreal)
            comptot = sorteddata['assettot']-sorteddata['shares_sell']-sorteddata['secloan']  # 资产总额扣除应付赎回款\融券金额，总资产不包含已经支付的费用，需要加回
            amtchg[1:] = comptot.values[1:]-comptot.values[:-1]+paid.values[1:]-inout[1:]  # 每日资金变动金额，补回费用，剔除申购赎回

            # 计算平滑后的 补回全部费用的 收益率
            rets = np.zeros_like(netreal)
            numerator = (comptot.values + paid.values + inout2)[1:]  # 分子与确认日对齐
            denominator = comptot.values[:-1]+(inout2+inout)[1:]
            rets[1:] = numerator/denominator-1

            netvals = pd.DataFrame(np.column_stack([dates.values,netreal,netcum,np.cumprod(1+rets)*netreal[0],rets,amtchg,np.cumsum(amtchg)]),
                                 columns=['Date','NetSingle','NetCumulated','NetCompensated','CompReturns','AmtChg','AmtCumChg'])

            sql.to_sql(netvals,name='Net_Values',con=conn_net,if_exists='replace',index=False)
            print(' '.join(['%s : Netvalues updated from' %self.pname,firstdate,'to',dates.values[-1]]))
        w.close()
