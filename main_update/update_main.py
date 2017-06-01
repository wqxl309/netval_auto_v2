
import os
import time
import threading

from main_update.global_vars import *
from products_info.products_info import *
from modules.file_to_database.file_to_database import *
from modules.netvalues_base.netvalues_base import *
from modules.netvalues_calculation.netval_calculation import *

if __name__ == '__main__':

    # 更新估值表 至 数据库 采用多线程加速更新 须确保各个产品所在的线程更新完成后再开始计算该产品的净值
    for k in PRODUCTS_INFO:
        p = PRODUCTS_INFO[k]
        dbdir = os.path.join(dbdir_base,''.join(['rawdb_',p['nickname'],'.db']))
        filedir = os.path.join(filedir_base,''.join(['估值信息 ',p['pname']]))
        processor = rawfile_process(dbdir=dbdir,filedir=filedir,pcode=p['pcode'],pname=p['pname'])
        #processor.update_database(VARTYPES)
        t = threading.Thread(target=processor.update_database,args=(VARTYPES,))
        t.start()
        t.join()

    # 提取估值表基础元素
    for k in PRODUCTS_INFO:
        p = PRODUCTS_INFO[k]
        dbdir = os.path.join(dbdir_base,''.join(['rawdb_',p['nickname'],'.db']))
        netdbdir = os.path.join(netdbdir_base,''.join(['netdb_',p['nickname'],'.db']))
        elements_extracter = netvalues_base(dbdir,netdbdir)
        #elements_extracter.update_netdb(codedict=CODEDICT[p['nickname']],indexmark='科目代码',valcols=('市值','市值本币'))
        t = threading.Thread(target=elements_extracter.update_netdb,args=(CODEDICT[p['nickname']],'科目代码',('市值','市值本币')))
        t.start()
        t.join()


    # 计算净值
    for k in PRODUCTS_INFO:
        if k == '烜鼎鑫诚九号':
            earnvars = ['earnAl','earnT']
            continue  # 目前估值表不全
        else:
            earnvars = ['earn']
        p = PRODUCTS_INFO[k]
        netdbdir = os.path.join(netdbdir_base,''.join(['netdb_',p['nickname'],'.db']))
        calculator = netvalues_calculation(pname=p['pname'],netdbdir=netdbdir,confirmdays=p['confirmdays'],precision=p['precision'])
        #calculator.generate_netvalues(earnvars = earnvars)
        t = threading.Thread(target=calculator.generate_netvalues,args=(earnvars,))
        t.start()
        t.join()