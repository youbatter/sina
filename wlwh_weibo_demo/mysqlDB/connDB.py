#coding=utf-8
#Version:python3.6.0
from mysqlDB.wbDB import withSessionAutoFree
import json
import time
import datetime

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
def enter_data(self,cursor,lc):
    sql = '''insert into user values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
    cursor.executemany(sql, lc)

@withSessionAutoFree(set_utf8=True)
def cha_Cookie(self,cursor,username):
    '''判断UA是否存在'''
    ret = cursor.execute(" SELECT Cookie from user WHERE username='{}'".format(username))
    d = cursor.fetchone()
    ua = d.get('Cookie')
    return ua

@withSessionAutoFree(set_utf8=True)
def cha_ip(self,cursor,device_number):
    ret = cursor.execute(" SELECT * from device WHERE ip='{}'".format(device_number))
    return ret

@withSessionAutoFree(set_utf8=True)
def cha_user(self,cursor,page):
    page = (page-1) * 200
    ret = cursor.execute(" SELECT * from `user` limit {},200".format(page))
    d = cursor.fetchall()
    print(d)
    lc = []
    for i in d:
        dit = {}
        dit['账号'] = i.get('username')
        dit['密码'] = i.get('password')
        enter_time= i.get('time')
        dit['导入时间'] = enter_time.strftime("%Y-%m-%d %H:%M:%S")
        endtime= i.get('endtime')
        endtime=time.localtime(endtime)
        dit['结束时间'] = time.strftime("%Y-%m-%d %H:%M:%S", endtime)
        status = i.get('abn')
        if status == 1:
            dit['状态'] = '账号异常'
        else:
            status = i.get('type')
            if status == 1:
                dit['状态'] = '账号正在运行中'
            else:
                dit['状态'] = '账号正常'
        ret1 = cursor.execute(" SELECT * from `wb` where `username`={} ".format(dit['账号']))
        get_total = cursor.fetchone()
        if get_total == None:
            dit['关注总数'] = 0
            dit['点赞总数'] = 0
            dit['转发总数'] = 0
            dit['评论总数'] = 0
        else:
            dit['关注总数'] = get_total.get('GZ')
            dit['点赞总数'] = get_total.get('DZ')
            dit['转发总数'] = get_total.get('ZF')
            dit['评论总数'] = get_total.get('PL')
        #判断当天关注  数据
        dit['当天评论总数'] = 0
        dit['当天关注总数'] = 0
        dit['当天点赞总数'] = 0
        dit['当天转发总数'] = 0
        ret1 = cursor.execute(" SELECT `task_type`,task_data,uid from `do_task_data` where `usr`={} and `time` >= date(now()) and `time` < DATE_ADD(date(now()),INTERVAL 1 DAY) ".format(dit['账号']))
        get_today_total = cursor.fetchall()
        if get_today_total :
            for today_total in get_today_total:
                dit['uid'] = today_total['uid']
                print(dit['uid'])
                type = today_total['task_type']
                if type== '评论':
                    dit['当天评论总数'] = today_total['task_data']
                if type== '转发':
                    dit['当天转发总数'] = today_total['task_data']
                if type== '点赞':
                    dit['当天点赞总数'] = today_total['task_data']
                if type== '关注':
                    dit['当天关注总数'] = today_total['task_data']
        lc.append(dit)
    return lc

@withSessionAutoFree(set_utf8=True)
def cha_log(self,cursor,usr):
    ret1 = cursor.execute(" SELECT uid,actionuid,`type` from log where username={}".format(usr))
    get_today_log = cursor.fetchall()
    today_logs = []
    if get_today_log:
        for today_log in get_today_log:
            type = today_log['type']
            uid = today_log['uid']
            actionuid = today_log['actionuid']
            if type == '0':
                log = uid + '关注' + actionuid + '成功'
                today_logs.append(log)
            if type == '1':
                log = uid + '点赞' + actionuid + '成功'
                today_logs.append(log)
            if type == '2':
                log = uid + '评论' + actionuid + '成功'
                today_logs.append(log)
            if type == '3':
                log = uid + '转发' + actionuid + '成功'
                today_logs.append(log)
        return today_logs

@withSessionAutoFree(set_utf8=True)
def status_doing(self,cursor):
    ret = cursor.execute(" SELECT username from `user` where type=1")
    d = cursor.fetchall()
    today_logs = []
    for i in d:
        dit = {}
        dit['username'] = i['username']
        ret1 = cursor.execute(" SELECT uid,actionuid,`type`,`time` from log where username={}".format(i['username']))
        if ret1 == 0:
            dit['日志'] = '没有日志'
        else:
            today_log = cursor.fetchall()[-1]
            type = today_log['type']
            uid = today_log['uid']
            actionuid = today_log['actionuid']
            if type == '0':
                log = uid + '关注' + actionuid + '成功'
                dit['日志'] = log
            if type == '1':
                log = uid + '点赞' + actionuid + '成功'
                dit['日志'] = log
            if type == '2':
                log = uid + '评论' + actionuid + '成功'
                dit['日志'] = log
            if type == '3':
                log = uid + '转发' + actionuid + '成功'
                dit['日志'] = log
        today_logs.append(dit)
    return today_logs

@withSessionAutoFree(set_utf8=True)
def time_order(self,cursor,page):
    '''
    按照账号导入时间排序
    :param self:
    :param cursor:
    :param page:
    :return:
    '''
    page = (page - 1) * 200
    ret = cursor.execute(" SELECT * from `user` ORDER BY `time` DESC limit {},200 ".format(page))
    d = cursor.fetchall()
    lc = []
    for i in d:
        dit = {}
        dit['账号'] = i.get('username')
        dit['密码'] = i.get('password')
        enter_time = i.get('time')
        dit['导入时间'] = enter_time.strftime("%Y-%m-%d %H:%M:%S")
        endtime = i.get('endtime')
        endtime = time.localtime(endtime)
        dit['结束时间'] = time.strftime("%Y-%m-%d %H:%M:%S", endtime)
        status = i.get('abn')
        if status == 1:
            dit['状态'] = '账号异常'
        else:
            status = i.get('type')
            if status == 1:
                dit['状态'] = '账号正在运行中'
            else:
                dit['状态'] = '账号正常'
        ret1 = cursor.execute(" SELECT * from `wb` where `username`={} ".format(dit['账号']))
        get_total = cursor.fetchone()
        if get_total == None:
            dit['关注总数'] = 0
            dit['点赞总数'] = 0
            dit['转发总数'] = 0
            dit['评论总数'] = 0
        else:
            dit['关注总数'] = get_total.get('GZ')
            dit['点赞总数'] = get_total.get('DZ')
            dit['转发总数'] = get_total.get('ZF')
            dit['评论总数'] = get_total.get('PL')
        # 判断当天关注  数据
        dit['当天评论总数'] = 0
        dit['当天关注总数'] = 0
        dit['当天点赞总数'] = 0
        dit['当天转发总数'] = 0
        ret1 = cursor.execute(
            " SELECT `task_type`,task_data,uid from `do_task_data` where `usr`={} and `time` >= date(now()) and `time` < DATE_ADD(date(now()),INTERVAL 1 DAY) ".format(
                dit['账号']))
        get_today_total = cursor.fetchall()
        if get_today_total:
            for today_total in get_today_total:
                dit['uid'] = today_total['uid']
                print(dit['uid'])
                type = today_total['task_type']
                if type == '评论':
                    dit['当天评论总数'] = today_total['task_data']
                if type == '转发':
                    dit['当天转发总数'] = today_total['task_data']
                if type == '点赞':
                    dit['当天点赞总数'] = today_total['task_data']
                if type == '关注':
                    dit['当天关注总数'] = today_total['task_data']
        lc.append(dit)
    return lc

if __name__ == '__main__':
    time_order(None,page=1)
