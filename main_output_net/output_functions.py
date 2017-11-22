import os

import pandas as pd

from products_info.products_info import PRODUCTS_INFO
from modules.netvalues_output.netval_output import netval_output
from modules.netvalues_indicators.netval_indicators import indicators


def get_configure(confdir):
    """ 从配置文件中提取参数 """
    result = {}
    with open(confdir,'r') as conf:
        while True:
            ln = conf.readline()
            if len(ln)==0:  # 遇到空行即停止 不包括唯一含有 /n 的行
                break
            else:
                notepos = ln.find('#')   # 注释标号后的内容都将被忽略
                newln = ln[0:notepos]
                contents = newln.split('=')
                if len(contents)>=3:
                    raise Exception('每行只能设置一个参数')
                elif len(contents)==1:   # 一行只有一个值，没有=将被忽略
                    continue
                title = contents[0].strip().lower()
                if len(title)==0:
                    continue
                cont = contents[1].strip().upper()
                if cont in ['TRUE','FALSE']:
                    cont = cont=='TRUE'
                #同一个Key 下的参数添加到列表里面
                if (title not in result):
                    result[title] = [cont]
                else:
                    result[title].append(cont)
    return result


def generate_output(products,outdir,startdate=False,enddate=False,freq='week',mktidx=False,indicators_info=None):
    """
    综合输出 所有产品
    indicator_info = {'indoutdir':...,'indlist': ... , 'riskfreerate':..., 'benchmark':... }
    """
    netdbfolder= r'\\JIAPENG-PC\database_netvalue'

    writer_netval = pd.ExcelWriter(outdir)
    netvalues = {}
    for p in products:
        for prod in PRODUCTS_INFO:
            if p==prod['pname']:
                p = prod
                break
        netdbdir = os.path.join(netdbfolder,''.join(['netdb_',p['nickname'],'.db']))
        ipodate = p['ipodate']
        outobj = netval_output(netdbdir=netdbdir,ipodate=ipodate)
        netvals = outobj.take_netvalues(startdate=startdate,enddate=enddate,freq=freq,mktidx=mktidx,regmktidx=False)
        if netvals is not None:  # 有数才输出
            netvals.to_excel(writer_netval,sheet_name=p['pname'],index=False)
        netvalues[p['pname']] = netvals
    writer_netval.save()

    if indicators_info:
        writer_ind = pd.ExcelWriter(indicators_info['indoutdir'])
        indlst = indicators_info['indlist']
        for p in products:
            if netvalues[p] is None: #没有净值数据，也不必计算指标
                continue
            if indicators_info['benchmark'] in netvalues[p].columns:
                bc = netvalues[p][indicators_info['benchmark']].values
            else:
                bc = indicators_info['benchmark']
            valueinfo = {'netvals':netvalues[p].loc[:,['单位净值','累计净值','补回净值']].values,
                         'riskfreerate':indicators_info.get('riskfreerate'),
                         'benchmark':bc
                         }
            indobj = indicators(valueinfo,indicator_list=indlst,freq=freq)
            ind_results = pd.DataFrame(indobj.take_orders(),index=['单位净值','累计净值','补回净值'])
            ind_results.to_excel(writer_ind,sheet_name=p)
        writer_ind.save()




