#coding:utf-8
'''
数据库操作模块
'''
import pymysql
import traceback
from functools import wraps

config = {
    'host': 'rm-bp17lwu41ilub2uit4o.mysql.rds.aliyuncs.com',
    'port': 3306,
    'user': 'sxn',
    'password': 'rootroot',
    'db': 'sina_wb',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}


def withSessionAutoFree(set_utf8 = False):
    '''装饰器,数据库会话自动提交,异常自动回滚'''
    def _call_withSessionAutoFree(origin_func):
        @wraps(origin_func)
        def wrapper(self,*args, **kwargs):
            try:
                # 连接数据库
                db = pymysql.connect(**config)
                # 创建游标
                cursor = db.cursor()
            except:
                print(traceback.print_exc())
                return
            try:
                if set_utf8:
                    cursor.execute("set names utf8")
                result = origin_func(self,cursor,*args, **kwargs)
                return result
            except:
                db.rollback()
                print(traceback.print_exc())
            finally:
                db.commit()  # 提交更改
                cursor.close()  # 关闭游标
                db.close()  # 关闭数据库
        return wrapper
    return _call_withSessionAutoFree










# if __name__ == "__main__":
#     # conn_test(None)
#     cha_res_head(None,'7188739318')