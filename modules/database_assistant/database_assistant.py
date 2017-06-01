import sqlite3


class db_assistant:
    """ 数据库辅助类，该类必须在 上下文管理器 模式下使用，否则无法连接 """
    @classmethod
    def gen_table_titles(cls,titles,varstypes,defaluttype = 'REAL'):
        """ 为采取 通过直接读取生成数据库表格标题 的任务创建带有数据类型的标题 同时识别空标题
            titles 为包含已经识别出作为标题的数据的列表
            vartypes 应给为可能包含的数据类型的字典
        """
        typed_titles = []
        empty_pos = []    # 标题中非空值对应位置为 False, 空值为True
        for tvar in titles:
            typed = False
            for tp in varstypes:
                if tvar in varstypes[tp]:
                    typed_titles.append(' '.join([tvar.strip('(%)'),tp]))
                    empty_pos.append(False)
                    typed = True
                    break
                elif tvar == '':   # titles 中包含空值
                    empty_pos.append(True)
                    typed = True
                    break
            if not typed:  # 如果没有找到指定的类型，则为默认类型
                typed_titles.append(''.join([tvar.strip('(%)'),' ',defaluttype]))
                empty_pos.append(False)
        return {'typed_titles':typed_titles,'empty_pos':empty_pos}

    def __init__(self,dbdir):
        self.dbdir=dbdir

    def __enter__(self):
        self.connection=sqlite3.connect(self.dbdir)
        return self    # 返回一个已经连接的 db_assistant对象

    def __exit__(self,exc_type,exc_instantce,traceback):
        self.connection.close()
        return False  # pop up errors

    def get_db_tablenames(self):
        """ 提取数据库中所有表格的名称，返回list """
        tbintuple = self.connection.execute(' SELECT name FROM sqlite_master WHERE type=\'table\' ').fetchall()
        tablenames = [tb[0] for tb in tbintuple]
        return tablenames

    def create_db_table(self,tablename,titles,replace=True):
        """ 创建数据库表格
            title 为 已经处理过的标题 列表,带有字段类型
            如果replace为真，则会替换已存在的同名表格
        """
        cursor = self.connection.cursor()
        exeline = ''.join(['CREATE TABLE ',tablename,' (',','.join(titles),') '])
        try:
            cursor.execute(exeline)
        except sqlite3.OperationalError as e:
            if 'already exists' in str(e):  # 如果要创建的表格已经存在
                if replace:    # 如果替换的话，先删除已存在表格再创建
                    cursor.execute(''.join(['DROP TABLE ',tablename]))
                    cursor.execute(exeline)
                    print('Table '+tablename+' created!')
                else:
                    print('Table '+tablename+' already exists!')
                return
            else: # 若果发生 不是因为表格已存在导致的异常，则将异常传出
                print('Error with creating table: %s !' % tablename)
                raise e
        else: # 正常创建
            print('Table '+tablename+' created!')

    def get_table_cols(self,tablename):
        """ 提取数据库中名为tablename 的表格的所有字段名（列名） """
        tablenames = self.get_db_tablenames()
        if tablename not in tablenames:   # 先检查数据库中是否存在该表格
            raise Exception('The table %s not in db, cant get its cols !' %tablename)
        result = self.connection.execute(''.join(['PRAGMA table_info([',tablename,'])'])).fetchall()   # sample展示 [(0, '科目代码', 'TEXT', 0, None, 0)] 序号 名称 类型 unknown unknown unknown
        cols = [c[1] for c in result]
        return cols


if __name__=='__main__':
    dbdir = r'C:\Users\Jiapeng\Desktop\Net Value\test.db'
    tablename = 'SS6021_百泉多策略一号_估值表_20170407'
    with db_assistant(dbdir) as db:
        print(db.get_table_cols(tablename))

    a={'4':2,'2':3,'5':1,'-1':1}
    for t,s in sorted(a).items():
        print(t,s)