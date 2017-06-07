import threading
import sys

sys.path.append(r'E:\netval_auto_v2.0')

from main_update.global_vars import *
from products_info.products_info import *
from modules.file_to_database.file_to_database import *
from modules.netvalues_base.netvalues_base import *


if __name__ == '__main__':
    for k in PRODUCTS_INFO:
        p = PRODUCTS_INFO[k]
        dbdir = os.path.join(dbdir_base,''.join(['rawdb_',p['nickname'],'.db']))
        netdbdir = os.path.join(netdbdir_base,''.join(['netdb_',p['nickname'],'.db']))
        elements_extracter = netvalues_base(dbdir,netdbdir)
        #elements_extracter.update_netdb(codedict=CODEDICT[p['nickname']],indexmark='科目代码',valcols=('市值','市值本币'))
        t = threading.Thread(target=elements_extracter.update_netdb,args=(CODEDICT[p['nickname']],'科目代码',('市值','市值本币')))
        t.start()