import sys
import threading

sys.path.append(r'E:\netval_auto_v2.0')

from main_update.global_vars import *
from products_info.products_info import *
from modules.file_to_database.file_to_database import *

if __name__ == '__main__':
    # 更新估值表 至 数据库 采用多线程加速更新 须确保各个产品所在的线程更新完成后再开始计算该产品的净值
    update_treads = []
    for k in PRODUCTS_INFO:
        p = PRODUCTS_INFO[k]
        dbdir = os.path.join(dbdir_base,''.join(['rawdb_',p['nickname'],'.db']))
        filedir = os.path.join(filedir_base,''.join(['估值信息 ',p['pname']]))
        processor = rawfile_process(dbdir=dbdir,filedir=filedir,pcode=p['pcode'],pname=p['pname'])
        #processor.update_database(VARTYPES)
        t = threading.Thread(target=processor.update_database,args=(VARTYPES,))
        t.start()
