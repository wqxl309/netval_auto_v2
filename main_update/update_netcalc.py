import sys

sys.path.append(r'E:\netval_auto_v2.0')

from products_info.global_vars import *
from products_info.products_info import *
from modules.file_to_database.file_to_database import *
from modules.netvalues_calculation.netval_calculation import *

if __name__ == '__main__':
    for k in PRODUCTS_INFO:
        if k == '烜鼎鑫诚九号':
            earnvars = ['earnAl','earnT']
            continue  # 目前估值表不全
        else:
            earnvars = ['earn']
        p = PRODUCTS_INFO[k]
        netdbdir = os.path.join(netdbdir_base,''.join(['netdb_',p['nickname'],'.db']))
        calculator = netvalues_calculation(pname=p['pname'],netdbdir=netdbdir,confirmdays=p['confirmdays'],precision=p['precision'])
        calculator.generate_netvalues(earnvars = earnvars)
        #t = threading.Thread(target=calculator.generate_netvalues,args=(earnvars,))
        #t.start()