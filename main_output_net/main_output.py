from remotewind import w

from main_output_net.output_functions import get_configure
from main_output_net.output_functions import generate_output



if __name__=='__main__':
    configure = get_configure('./configure.txt')
    confkeys = configure.keys()

    products = configure['productadd']
    # 提取计算起始截止日期
    if 'startdate' in confkeys:
        startdate = configure['startdate'][0]                        # 设为 False 将以最早的日期为开始
    else:
        startdate= False
    if 'enddate' in confkeys:
        enddate =  configure['enddate'][0]                                  # 设为 False 将以最近的时期为结束
    else:
        enddate = False
    # 提取指数
    if 'needmktidx' in confkeys and configure['needmktidx'][0]:
        if 'mktidxadd' not in confkeys:
            raise Exception(u'未指定所需指数代码')
        mktidx = configure['mktidxadd']                                  # 是否输出同步指数
    else:
        mktidx = False
    # 提取计算频率
    if 'frequency' in confkeys:
        freq =  configure['frequency'][0]                          # 净值频率 包含日度--day, 周度--week 以及 月度 -- month
        filename = freq
    else:
        raise Exception(u'未设定数据频率')

    # 输出路径
    outdir=r'.\输出结果' + '\\'+ filename + '_净值.xlsx'
    # 提取需要计算的指标
    indicators_info = {}
    if 'indicators' in confkeys and configure['indicators'][0]:
        indicators_info['indoutdir'] = r'.\输出结果' + '\\'+ filename + '_指标.xlsx'
        indicators_info['indlist'] = configure['indicatoradd']
        indicators_info['benchmark'] = configure.get('benchmark')[0]
        indicators_info['riskfreerate'] = float(configure.get('riskfreerate')[0])

    generate_output(products=products,outdir=outdir,startdate=startdate,enddate=enddate,freq=freq,mktidx=mktidx,indicators_info=indicators_info)

    print('数据提取成功！')