#coding=utf-8
#Version:python3.6.0
from mysqlDB.wbDB import withSessionAutoFree
import json
import time

@withSessionAutoFree(set_utf8=True)
def cha_UA(self,cursor,username):
    '''判断UA是否存在'''
    ret = cursor.execute(" SELECT UA from user WHERE username='{}'".format(username))
    d = cursor.fetchone()
    ua = d.get('UA')
    return ua

@withSessionAutoFree(set_utf8=True)
def save_UA(self,cursor,username,ua,cookie):
    '''保存ua和cookie'''
    ua = json.dumps(ua)
    cookie = json.dumps(cookie)
    ret = cursor.execute("update user set UA='{}' where username='{}'".format(ua, username))
    ret1 = cursor.execute("update user set Cookie='{}' where username='{}'".format(cookie, username))

@withSessionAutoFree(set_utf8=True)
def get_updata(self,cursor,uid):
    '''保存账号得uid到表updata中'''
    ret = cursor.execute('''insert into updata(uid)values ('{}')'''.format(uid))

@withSessionAutoFree(set_utf8=True)
def res_head_status(self,cursor,uid):
    '''保存头像已修改'''
    ret = cursor.execute("update updata set touxiang=1 where uid='{}'".format(uid))

@withSessionAutoFree(set_utf8=True)
def res_info_status(self,cursor,uid):
    '''保存信息已修改'''
    ret = cursor.execute("update updata set xinxi=1 where uid='{}'".format(uid))

@withSessionAutoFree(set_utf8=True)
def cha_head_status(self,cursor,uid):
    '''获取头像是否修改状态'''
    ret = cursor.execute(" SELECT touxiang from updata WHERE uid='{}'".format(uid))
    d = cursor.fetchone()
    touxiang = d.get('touxiang')
    return touxiang

@withSessionAutoFree(set_utf8=True)
def cha_info_status(self,cursor,uid):
    '''获取信息是否修改状态'''
    ret = cursor.execute(" SELECT xinxi from updata WHERE uid='{}'".format(uid))
    d = cursor.fetchone()
    info = d.get('xinxi')
    return info

@withSessionAutoFree(set_utf8=True)
def is_get_uid(self,cursor,uid):
    ret = cursor.execute(" SELECT uid from updata WHERE uid='{}'".format(uid))
    return ret

@withSessionAutoFree(set_utf8=True)
def out_denglu(self,cursor,username):
    time1 = int(time.time())
    ret = cursor.execute("update user set `type` =0  where username='{}'".format( username))
    ret = cursor.execute("update user set endtime='{}' where username='{}'".format(time1, username))

@withSessionAutoFree(set_utf8=True)
def yichang(self, cursor, username):
    ret = cursor.execute("update user set abn = 1  where username='{}'".format(username))

@withSessionAutoFree(set_utf8=True)
def GZ_log(self, cursor,uid,username,action_uid):
    type=0  #0关注 1点赞 2评论  3转发
    ret = cursor.execute('''insert into log(uid,username,actionuid,`type`)values ('{}','{}','{}','{}')'''.format(uid,username,action_uid,type))

@withSessionAutoFree(set_utf8=True)
def DZ_log(self,cursor,uid,username,mid):
    type=1
    ret = cursor.execute('''insert into log(uid,username,actionuid,`type`)values ('{}','{}','{}','{}')'''.format(uid,username,mid,type))

@withSessionAutoFree(set_utf8=True)
def ZF_log(self,cursor,uid,username,mid):
    type = 3
    ret = cursor.execute('''insert into log(uid,username,actionuid,`type`)values ('{}','{}','{}','{}')'''.format(uid,username,mid,type))

@withSessionAutoFree(set_utf8=True)
def PL_log(self,cursor,uid,username,mid):
    type = 2 #评论
    ret = cursor.execute('''insert into log(uid,username,actionuid,`type`)values ('{}','{}','{}','{}')'''.format(uid,username,mid,type))

@withSessionAutoFree(set_utf8=True)
def cha_data(self,cursor,usr,type):
    ret = cursor.execute(" SELECT id from do_task_data WHERE usr='{}' and `task_type`='{}' and `time` >= date(now()) and `time` < DATE_ADD(date(now()),INTERVAL 1 DAY)".format(usr,type))
    return ret

@withSessionAutoFree(set_utf8=True)
def insert_data(self,cursor,usr,task_type,task_data,uid):
    ret = cursor.execute('''insert into do_task_data(usr,task_type,task_data,uid)values ('{}','{}','{}','{}')'''.format(usr,task_type,task_data,uid))

@withSessionAutoFree(set_utf8=True)
def updata_data(self,cursor,usr,task_type,task_data):
    ret = cursor.execute("update do_task_data set task_data= task_data+'{}' where usr='{}' and task_type='{}'".format(task_data,usr,task_type))

@withSessionAutoFree(set_utf8=True)
def cha_wb(self,cursor,usr):
    ret = cursor.execute(" SELECT id from wb WHERE username='{}'".format(usr))
    return ret

@withSessionAutoFree(set_utf8=True)
def insert_wb(self,cursor,usr):
    ret = cursor.execute('''insert into wb(username)values ('{}')'''.format(usr))

@withSessionAutoFree(set_utf8=True)
def updata_wb_GZ(self,cursor,data,usr):
    ret = cursor.execute("update wb set GZ= GZ+'{}' where username='{}'".format(data,usr))

@withSessionAutoFree(set_utf8=True)
def updata_wb_PL(self,cursor,data,usr):
    ret = cursor.execute("update wb set PL= PL+'{}' where username='{}'".format(data,usr))

@withSessionAutoFree(set_utf8=True)
def updata_wb_ZF(self,cursor,usr):
    ret = cursor.execute("update wb set ZF= ZF+'{}' where username='{}'".format(1,usr))

@withSessionAutoFree(set_utf8=True)
def updata_wb_DZ(self,cursor,usr):
    ret = cursor.execute("update wb set DZ= DZ+'{}' where username='{}'".format(1,usr))

@withSessionAutoFree(set_utf8=True)
def enter_data(self,cursor,username,password):
    ret = cursor.execute('''insert into user(username,password)values('{}','{}')'''.format(username,password))


# if __name__ == '__main__':
#     d = updata_wb_ZF(None,'17363075985')
    # print(d)
#     # if d ==1:
    #     insert_data(None,'13783560539','评论',12,'44555',3)
    # else:
    #     updata_data(None,'13783560539','评论')