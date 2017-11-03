import threading
import sys
sys.path.append(r'E:\netval_auto_v2.0')
from modules.emails_download.email_processor_product import *
from modules.file_to_database.file_to_database import *
from modules.netvalues_base.netvalues_base import *
from modules.netvalues_calculation.netval_calculation import *
import products_info.global_vars as gv
import products_info.products_info as pinfo


if __name__ == '__main__':

    # 下载邮件估值表附件
    host = 'imap.qiye.163.com' #'imap.qiye.163.com' #'smtp.qiye.163.com'
    username = 'baiquaninvest@baiquaninvest.com'
    password = 'Baiquan1818'
    savepath = r'E:\估值表'
    lastuidpath = r'E:\netval_auto_v2.0\modules\emails_download\last_uid.txt'
    pfilter = pinfo.EMAIL_FILTER
    downloader = email_processor_product(host,username,password,savepath,lastuidpath,product_filters=pfilter)
    downloader.download_imap4(downloadtype='ALL',replace=True)
    print()
    print()

    # 更新估值表 至 数据库 采用多线程加速更新 须确保各个产品所在的线程更新完成后再开始计算该产品的净值
    update_treads = []
    for p in pinfo.PRODUCTS_INFO:
        if not p['updtbase']:
            continue
        processor = rawfile_process(dbdirbase=gv.BASE_DBDIR,filedirbase=gv.BASE_FILEDIR,pcode=p['pcode'],pname=p['pname'],pnickname=p['nickname'])
        #processor.update_database(VARTYPES)
        t = threading.Thread(target=processor.update_database,args=(gv.VARTYPES,))
        update_treads.append(t)
    for t in update_treads:
        t.start()
    for t in update_treads:
        t.join()
    del update_treads
    print('rawfile update finished')
    print()
    print()

    # 提取估值表基础元素
    base_treads = []
    for p in pinfo.PRODUCTS_INFO:
        if not p['tkelement']:
            continue
        elements_extracter = netvalues_base(dbdirbase=gv.BASE_DBDIR,netdbdirbase=gv.BASE_NETDBDIR,pname=p['pname'],pnickname=p['nickname'])
        #elements_extracter.update_netdb(codedict=CODEDICT[p['nickname']],indexmark='科目代码',valcols=('市值','市值本币'))
        t = threading.Thread(target=elements_extracter.update_netdb,args=(gv.CODEDICT[p['nickname']],'科目代码',('市值','市值本币')))
        base_treads.append(t)
    for t in base_treads:
        t.start()
    for t in base_treads:
        t.join()
    del base_treads
    print('netval base update finished')
    print()
    print()

    # 计算净值 不用多线程 按制定顺序显示
    try:
        calc_treads = []
        for p in pinfo.PRODUCTS_INFO:
            if p['pname'] == '烜鼎鑫诚九号':
                earnvars = ['earnAl','earnT']
                continue  # 目前估值表不全
            else:
                earnvars = ['earn']
            if not p['calcnet']:
                continue
            calculator = netvalues_calculation(pname=p['pname'],pnickname=p['nickname'],netdbdirbase=gv.BASE_NETDBDIR,confirmdays=p['confirmdays'],precision=p['precision'])
            calculator.generate_netvalues(earnvars = earnvars)
        print('netval calc update finished')
    except BaseException as e:
        import traceback
        traceback.print_exc()
        print('Error %s' %e)
        os.system('PAUSE')