import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mpdt
import numpy as np


def netval_plot():
    mpl.rcParams['font.sans-serif'] = ['SimHei'] #用来正常显示中文标签
    fig=plt.figure(figsize=(20,15))
    showdatenum=20
    N=len(netdate)
    if N<=showdatenum:
        showidx=[x for x in range(N)]
    else:
        step=int(np.floor(N/showdatenum))
        showidx=[x for x in range(0,N,step)]
        if N-1-showidx[-1]>=step/2:
            showidx.append(N-1)
    ax=fig.add_subplot(121)
    ax.set_ylim(plotlimits)
    ax.set_xlim([showidx[0],showidx[-1]])
    ax.plot(netsig,'r',lw=2,label=self.productname)
    colors=['g','b']
    if mktidx:
        for dumi in range(len(mktidx)):
            ax.plot(idxdata_sig[:,dumi],colors[dumi],label=mktidx[dumi],lw=2)
    plt.xticks(rotation=70)
    plt.xticks(showidx,netdate.iloc[showidx])
    plt.legend(loc='upper left')
    #ax.xaxis.set_major_formatter(mpdt.DateFormatter('%Y-%m-%d'))
    #plt.xticks(pd.date_range(trddata['NetSingle'].index[0],trddata['NetSingle'].index[-1],freq='1min'))
    ax2=fig.add_subplot(122)
    ax2.set_ylim(plotlimits)
    ax2.set_xlim([showidx[0],showidx[-1]])
    ax2.plot(netcum,'r',lw=2,label=self.productname)
    colors2=['b','gray']
    if mktidx:
        for dumi in range(len(mktidx)):
            ax2.plot(idxdata_cum[:,dumi],colors2[dumi],label=mktidx[dumi],lw=2)
    plt.xticks(rotation=70)
    plt.xticks(showidx,netdate.iloc[showidx])
    plt.legend(loc='upper left')
    plt.show()