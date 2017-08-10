import datetime as dt

PRODUCTS_INFO = \
    {
        '百泉一号':{'dlemail':True,'updtbase':True,'tkelement':True,'calcnet':True,'pname':'百泉一号','pcode':'SD8964','ipodate':dt.date(2015,12,30),'confirmdays':2,'precision':3,'nickname':'Baiquan1'},
        '百泉二号':{'dlemail':True,'updtbase':True,'tkelement':True,'calcnet':True,'pname':'百泉二号','pcode':'SR3281','ipodate':dt.date(2016,11,24),'confirmdays':2,'precision':4,'nickname':'Baiquan2'},
        '百泉三号':{'dlemail':True,'updtbase':True,'tkelement':True,'calcnet':True,'pname':'百泉三号','pcode':'SS1391','ipodate':dt.date(2017, 5,19),'confirmdays':2,'precision':4,'nickname':'Baiquan3'},

        '百泉进取一号':{'dlemail':True,'updtbase':True,'tkelement':True,'calcnet':True,'pname':'百泉进取一号','pcode':'SM7753','ipodate':dt.date(2016,11, 3),'confirmdays':2,'precision':4,'nickname':'BaiquanJQ1'},
        '百泉汇瑾一号':{'dlemail':True,'updtbase':True,'tkelement':True,'calcnet':True,'pname':'百泉汇瑾一号','pcode':'SN4286','ipodate':dt.date(2016,11,24),'confirmdays':2,'precision':3,'nickname':'BaiquanHJ1'},
        '百泉砺石一号':{'dlemail':True,'updtbase':True,'tkelement':True,'calcnet':True,'pname':'百泉砺石一号','pcode':'None','ipodate':dt.date(2017,4,19), 'confirmdays':2,'precision':4,'nickname':'BaiquanLS1'},
        '百泉多策略一号':{'dlemail':True,'updtbase':True,'tkelement':True,'calcnet':True,'pname':'百泉多策略一号','pcode':'SS6021','ipodate':dt.date(2017, 4, 7),'confirmdays':2,'precision':3,'nickname':'BaiquanMS1'},

        '国道砺石二号':{'dlemail':True,'updtbase':True,'tkelement':True,'calcnet':True,'pname':'国道砺石二号','pcode':'SM8060','ipodate':dt.date(2016,10,10), 'confirmdays':2,'precision':4,'nickname':'GuodaoLS2'},
        '烜鼎鑫诚九号':{'dlemail':True,'updtbase':True,'tkelement':True,'calcnet':False,'pname':'烜鼎鑫诚九号','pcode':'SR0165','ipodate':dt.date(2016,12,7),  'confirmdays':2,'precision':4,'nickname':'Xuanding9'},
        '星盈7号':{'dlemail':True,'updtbase':False,'tkelement':False,'calcnet':False,'pname':'星盈7号','pcode':'SM9136','ipodate':dt.date(2016,11,16), 'confirmdays':2,'precision':4,'nickname':'Xingying7'},
    }

EMAIL_FILTER = \
    {
        '百泉一号':{'Subject':['百泉一号','估值表'],'Attachment':['百泉一号','估值表']},
        '百泉二号':{'Subject':['百泉二号','估值表'],'Attachment':['百泉二号','估值表']},
        '百泉三号':{'Subject':['百泉三号','估值表'],'Attachment':['百泉三号','估值表']},

        '百泉进取一号':{'Subject':['SM7753','百泉进取一号','估值表'],'Attachment':['SM7753','百泉进取一号','估值表']},
        '百泉汇瑾一号':{'Subject':['SN4286','百泉汇瑾一号','估值表'],'Attachment':['SN4286','百泉汇瑾一号']},
        '百泉多策略一号':{'Subject':['SS6021','百泉多策略一号','估值表'],'Attachment':['SS6021','百泉多策略一号']},

        #'百泉砺石一号':{'Subject':['粤财信托','百泉汇瑾一号','估值表']},'Attachment':{['粤财信托','百泉汇瑾一号','估值表']}},
        #'国道砺石二号':{'Subject':[],'Attachment':{}},

        '烜鼎鑫诚九号':{'Subject':['SR0165','烜鼎鑫诚九号','估值表'],'Attachment':['SR0165','烜鼎鑫诚九号']},
        '星盈7号':{'Subject':['穗信弘天禾中子星','星盈7号','估值表'],'Attachment':['穗信弘天禾中子星','星盈7号']},
    }
