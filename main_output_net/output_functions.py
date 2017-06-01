import os

from products_info.products_info import *
from modules.netvalues_output.netval_output import *
from modules.netvalues_indicators.netval_indicators import *


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
    netdbfolder= r'E:\netval_auto_v2.0\database_netvalue'  #r'\\JIAPENG-PC\database_netvalue'

    writer_netval = pd.ExcelWriter(outdir)
    netvalues = {}
    for p in products:
        netdbdir = os.path.join(netdbfolder,''.join(['netdb_',PRODUCTS_INFO[p]['nickname'],'.db']))
        ipodate = PRODUCTS_INFO[p]['ipodate']
        outobj = netval_output(netdbdir=netdbdir,ipodate=ipodate)
        netvals = outobj.take_netvalues(startdate=startdate,enddate=enddate,freq=freq,mktidx=mktidx,regmktidx=False)
        netvals.to_excel(writer_netval,sheet_name=p,index=False)
        netvalues[p] = netvals
    writer_netval.save()

    if indicators_info:
        writer_ind = pd.ExcelWriter(indicators_info['indoutdir'])
        indlst = indicators_info['indlist']
        for p in products:
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




