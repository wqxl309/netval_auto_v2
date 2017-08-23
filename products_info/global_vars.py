
dbdir_base = r'E:\netval_auto_v2.0\database_rawfile'
netdbdir_base = r'E:\netval_auto_v2.0\database_netvalue'
filedir_base = r'E:\估值表'


#extract_codes = ['sharenum',),'assettot',),'debttot',),'assetnet',),'fee_service',),'fee_keep',),'fee_management',),'earn',),'shares_buy',),'shares_sell']
# 份额、总资产、总负债、净资产、服务费、托管费、管理费、业绩提成、认申购、赎回

fill = 'NotSeenYet'   # 目前估值表中还未出现项目的填充,),等待出现后再替换为实际代码

### 每个产品字典中，key 为该字段将被存储在 元素表（数据库中）的列名，tuple中第一个值为其在估值表中的行名(row index)，第二个值为列名，如果只有一个元素则为行名，列名采用默认
CODEDICT= \
    {
        'Baiquan1': {'sharenum':('实收资本','数量'),'assettot':('资产合计',),'debttot':('负债合计',),'assetnet':('资产净值',),'fee_service':('2206.14',),
                     'fee_keep':('2207.01',),'fee_management':('2206.01',),'earn':('2206.02',),'shares_buy':('1207.01',),'shares_sell':('2203.01',),'fee_other':('2241.99'),},

        'Baiquan2': {'sharenum':('实收资本','数量'),'assettot':('资产类合计:',),'debttot':('负债类合计:',),'assetnet':('基金资产净值:',),'fee_service':('2205',),
                     'fee_keep':('2207',),'fee_management':('2206',),'earn':(fill,),'shares_buy':(fill,),'shares_sell':('2203',),'fee_other':('224199'),},

        'Baiquan3': {'sharenum':('实收资本','数量'),'assettot':('资产类合计：',),'debttot':('负债类合计：',),'assetnet':('资产资产净值：',),'fee_service':('221001',),
                     'fee_keep':('220701',),'fee_management':('220601',),'earn':(fill,),'shares_buy':(fill,),'shares_sell':('2203',),'fee_other':('224199'),},

        'BaiquanJQ1':{'sharenum':('实收资本','数量'),'assettot':('资产合计',),'debttot':('负债合计',),'assetnet':('资产净值',),'fee_service':('2211.01',),
                      'fee_keep':('2207.01',),'fee_management':('2206.01',),'earn':('2206.02',),'shares_buy':('1207.01',),'shares_sell':('2203.01',),'fee_other':('2241.99'),},

        'BaiquanHJ1':{'sharenum':('实收资本','数量'),'assettot':('资产类合计:',),'debttot':('负债类合计:',),'assetnet':('基金资产净值:',),'fee_service':('220501',),
                      'fee_keep':('220701',),'fee_management':(fill,),'earn':(fill,),'shares_buy':('120701',),'shares_sell':('220301',),'fee_other':('224199'),},

        'BaiquanMS1':{'sharenum':('实收资本','数量'),'assettot':('资产类合计:',),'debttot':('负债类合计:',),'assetnet':('基金资产净值:',),'fee_service':('220501',),
                      'fee_keep':('220701',),'fee_management':('220601',),'earn':(fill,),'shares_buy':(fill,),'shares_sell':('220301',),'fee_other':('224199'),},


        'BaiquanLS1':{'sharenum':('实收信托','数量'),'assettot':('资产类合计:',),'debttot':('负债类合计:',),'assetnet':('信托资产净值:',),'fee_service':('220501',),
                      'fee_keep':('220701',),'fee_management':('220601',),'earn':(fill,),'shares_buy':(fill,),'shares_sell':(fill,),'fee_other':('224199'),},

        'GuodaoLS2':{'sharenum':('实收资本','数量'),'assettot':('资产合计',),'debttot':('负债合计',),'assetnet':('资产净值',),'fee_service':('2208.02',),
                     'fee_keep':('2207.01',),'fee_management':('2206.01',),'earn':('2206.02',),'shares_buy':('1207.01',),'shares_sell':('2203.01',),'fee_other':('2241.99'),},

        'Xuanding9':{'sharenum':('实收资本','数量'),'assettot':('资产类合计:',),'debttot':('负债类合计:',),'assetnet':('基金资产净值:',),'fee_service':('220501',),'fee_keep':('220701',),'fee_management':('220601',),
                     'earnT':('220602',),'earnAl':('220604',),'shares_buy':('120701',),'shares_sell':('220301',),'secloan':('210171',),'fee_secloan':('250111',),'fee_other':('224199',)},

        'Xingying7': {'sharenum':('基金资产净值','数量'),'assettot':('资产类合计',),'debttot':('负债类合计',),'assetnet':('基金资产净值',),'fee_service':('221001',),
                     'fee_keep':('220701',),'fee_management':('220601',),'earn':('220602',),'shares_buy':(fill,),'shares_sell':(fill,),'fee_other':('224199'),},

    }


VARTYPES = {'TEXT':['科目代码','科目名称','币种','停牌信息','停牌标志','权益信息','科目级别']}