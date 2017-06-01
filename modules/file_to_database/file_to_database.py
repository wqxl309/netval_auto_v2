import os
import re
import xlrd

from modules.database_assistant.database_assistant import *

class rawfile_process:
    """ 处理原始估值表的类 """
    def __init__(self,dbdir,filedir,pcode,pname):
        self._dbdir = dbdir
        self._filedir = filedir
        self._product_code = pcode  # 产品代码 需继承类提供
        self._product_name = pname  # 产品名称 需继承类提供

    def get_newtables(self):
        """
        提取已下载但还未存入数据库 的 估值表的名称，为估值表原始名称 包含文件后缀
        """
        currntbs = set(os.listdir(self._filedir))      # 文件夹中当前存储的估值表
        with db_assistant(dbdir = self._dbdir) as db:
            cursor = db.connection.cursor()
            db.create_db_table(tablename='SAVED_TABLES',titles=['TableNames TEXT'],replace=False)
            temp = cursor.execute('SELECT * FROM SAVED_TABLES').fetchall()
            savedtbs = set([tb[0] for tb in temp])
        newtables=sorted(list(currntbs.difference(savedtbs)))
        return newtables

    def get_tablenames(self,tabledir):
        """
        通过估值表路径提取表格名称 主要需要提取日期以及产品名称
        表格名称统一格式为 产品代码_产品名称_日期
        需要检查 self._product_name 与表格提取处的名称是否相同
        """
        if not os.path.exists(tabledir):
            raise Exception('估值表路径不存在，拒绝提取表格名！')
        strings=tabledir.split('\\')   # 分割估值表 表格路径
        rawname = strings[-1]
        rawname_nofix=rawname.split('.')[0]  # 去除文件名中的 文件后缀 .xlsx
        if self._product_name not in rawname_nofix:
            raise Exception('当前估值表名称中未检测出产品名称，请检查！')
        # 通过正则表达式寻找估值表名称中可能出现的不同格式的日期
        pattern = r'([1-9])([\d]{3})[-年]?([\d]{2})[-月]?([\d]{2})' # 第一个数字应该非0
        datefound = ''.join(re.search(pattern,rawname_nofix).groups())
        tablename = '_'.join([self._product_code,self._product_name,'估值表',datefound])
        return {'rawname':rawname,'tablename':tablename}

    def table_info_check(self,tabledir,datemark='日期'):
        """ 检查估值表中日期\产品名称 是否与表格文件名中的相同 """
        tablename = self.get_tablenames(tabledir)['tablename']
        temp = tablename.split('_')
        name = temp[1]
        date = temp[3]
        rawdata=xlrd.open_workbook(tabledir)
        table = rawdata.sheets()[0]          #通过索引顺序获取
        namecorrect = False
        datecorrect= False
        for dumi in range(table.nrows):
            tocheck = ''.join(table.row_values(dumi))  # 处理读取行中的空字符
            if name in tocheck:
                namecorrect = True
            if datemark in tocheck:
                pattern = r'([1-9])([\d]{3})[-年]?([\d]{2})[-月]?([\d]{2})' # 第一个数字应该非0
                datefound = ''.join(re.search(pattern,tocheck).groups())
                if date==datefound:
                    datecorrect = True
            if namecorrect & datecorrect:
                print('%s passed check, ready for storage!' % tablename)
                return tablename # 为了检查后写入数据库的时候不必再次提取tablename
        raise Exception('%s failed check !' % tablename)    # 如果始终未检测到相应日期和产品名称，则报错

    def get_table_titles(self,tabledir,titlemark='科目代码',omitchars='-%'):
        """
        从估值表(.xls)中提取正表标题
        titlemark 为识别为标题行的标记
        omitchars 为标题中需要剔除字符
        """
        rawdata = xlrd.open_workbook(tabledir)
        table = rawdata.sheets()[0]          #通过索引顺序获取
        for dumi in range(table.nrows):
            if titlemark in table.row_values(dumi):   # 识别标题行 避免采用第二行有 科目代码 的标题
                titles = list(table.row_values(dumi))
                titlenum = len(titles)
                for dumj in range(titlenum):
                    titles[dumj] = titles[dumj].strip(omitchars)   # 逐个删除标题的无效字符
                    titles[dumj] = titles[dumj].replace(' ','')    # 去除字段中空格
                    titles[dumj] = titles[dumj].replace('-','')    # - 无法被strip what the fuck？
                    if titles[dumj]=='':   # 处理标题为空的情况： 此时dumj-1 对应列应为 市值、估值增值 等
                        titles[dumj] = titles[dumj-1]+'本币'
                        titles[dumj-1] += '原币'
                return titles  # 找到标题即返回

    def table_to_db(self,tbname_dict,tabledir,varstypes,datemark='日期',titlemark='科目代码',omitchars='-%',defaluttype = 'REAL',replace=True):
        """
        将估值表excel表格写入至数据库
        tbname_dict 为估值表将在数据库中存储的名称，需在该方法外确认其是否已经更新过, 目前为包含rawname 和 tablename 的dict
        vartypes 应给为可能包含的数据类型的字典
        titlemark 需要能用做识别出标题行，同时识别出表格正文
        replace 为 True 避免在同一张表格中多次写入
        """
        hasdb=os.path.exists(self._dbdir)  # 写入前数据库必须存在，数据库的建立在方法外实现
        if not hasdb:
            print('Database does NOT exist, no update!')
            return
        self.table_info_check(tabledir=tabledir,datemark='日期')   # 写入前需先检查估值表内容
        rawtitles = self.get_table_titles(tabledir=tabledir,titlemark=titlemark,omitchars=omitchars)  # 从估值表中提取初始标题
        markpos = rawtitles.index(titlemark)  # titlemark 所在的标题行的位置
        titles = db_assistant.gen_table_titles(titles=rawtitles,varstypes=varstypes,defaluttype = defaluttype)['typed_titles']  # 标注了字段类型的标题
        tablename = tbname_dict['tablename']
        with db_assistant(dbdir = self._dbdir) as db:
            db.create_db_table(tablename=tablename,titles=titles,replace=replace)  # 创建表格
            data=xlrd.open_workbook(tabledir)
            table = data.sheets()[0]
            # 寻找正表起始行
            startline=-1
            for dumi in range(table.nrows):
                try:
                    # 检查首个元素类型，如果能转换为数值则为应该记录的行的起始行
                    int(table.row_values(dumi)[markpos])
                except ValueError:
                    continue
                else:
                    startline=dumi
                    break
            if startline==-1: # 读完整个文件都没找到起始行则程序报错
                raise Exception('Can not find startline for table : %s' % tablename)
            # 已经找到正文起始行，开始写入数据库
            cursor = db.connection.cursor()
            try:
                for dumi in range(startline,table.nrows):  # 开始从正文行写入
                    exeline=''.join(['INSERT INTO ',tablename,' VALUES (',','.join(['?']*len(titles)),')'])
                    cursor.execute(exeline , tuple(table.row_values(dumi)))
                    db.connection.commit()
            except: # 无论任何原因导致写入table失败，则都要删除未写完的table
                print('Writing table %s failed !' % tablename)
                db.connection.execute(' '.join(['DROP TABLE',tablename]))
                print('Failed table %s dropped !' % tablename)
                raise
            else: # 如果表格正常完成更新，则需将其原始名称写入 SAVED_TABLES 数据表用作记录
                cursor.execute('INSERT INTO SAVED_TABLES VALUES (?)',(tbname_dict['rawname'],))  # 需要一个 tuple 作为输入
                db.connection.commit()
                print('Writing table %s succed !' % tablename)

    def update_database(self,vartypes):
        newtables = self.get_newtables()
        if not newtables:
            print('%s : No new tables to save in db !' % self._product_name)
            return
        for table in newtables:
            tabledir = os.path.join(self._filedir,table)
            tablename_dict = self.get_tablenames(tabledir)
            self.table_to_db(tbname_dict=tablename_dict,tabledir=tabledir,varstypes=vartypes,datemark='日期',titlemark='科目代码',omitchars='-%',defaluttype = 'REAL',replace=True)
        print('%s Database update finished !' % self._product_name)

