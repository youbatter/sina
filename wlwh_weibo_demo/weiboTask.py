#coding:utf-8
'''
执行线程任务的模块
'''
import threading
import time
import traceback
from weibo.weibo import WeiBoLogin
from misc.res import *
from mysqlDB.wbDB import withSessionAutoFree
import mysqlDB.connDB as DB
from ProxyPool.proxyHttp import ProxyPool
import config.config as config
from fake_useragent import UserAgent
import ServerSync.ServerSync as ServerSync


WEIBO_GZ_TASK_SYNC = ServerSync.TaskClass("weibo_apiGetTaskList_GZ")#创建一个处理微博关注同步的类对象
WEIBO_ZFDZ_TASK_SYNC = ServerSync.TaskClass("weibo_apiGetZFList")#创建一个处理微博转发点赞同步的类对象
WEIBO_PL_TASK_SYNC = ServerSync.TaskClass("weibo_apiGetPLList")#创建一个处理微博评论同步的类对象

def do_zfpldz(wbUsr):
    wbUsr.usrRunLog(0,u"开始执行微博转发评论点赞任务")
    err_count = 0
    cur_succ_count = 0  # 当前成功计数

    #转发和评论因为可以重复,所以不需要本地记录,只记录点赞的就行了
    wbUsr.likeList = wbUsr.usrReadFile("like.ini", is_pickle=True, default_ret=[])  # 从本地载入已经点赞的列表
    res = wbUsr.isFreeze()
    if res == True:
        DB.yichang(None, wbUsr.usr)
        DB.out_denglu(None, wbUsr.usr)
    else:
        try:
            for task in WEIBO_ZFDZ_TASK_SYNC.getTask()["json_list"]:  # 获取关注任务
                if cur_succ_count >= float(config.GetConfig("like", 200)):  # 判断是否达到上限
                    break

                resData = {} # 查询订单是否还有效
                if not WEIBO_ZFDZ_TASK_SYNC.syncData(name="weibo_apiIsRuningTask_zfdz", a=task["id"],resData=resData):
                    continue
                needLike = resData.get("n_dz",0) #判断本订单是否需要点赞
                needForward = resData.get("n_zf",0)  #判断本订单是否需要转发
                if not (needLike or needForward ):#如果已经不需要转发和点赞了,直接跳过订单
                    continue
                needComment = resData.get("n_pl",0) #判断本订单当前是否需要评论,评论是送的
                plid = task["plid"] #获取评论ID
                reason = None
                if int(plid)>0:
                    resData = {} #获取评论内容
                    if WEIBO_ZFDZ_TASK_SYNC.syncData(url="http://118.31.171.22/api2",name="api_wbGetzfpl",a=plid,resData=resData):
                        reason = resData.get("msg")
                if not reason:reason = u"转发微博!"#如果没获取到转发或评论的内容,手动填充一个
                b1,b2 = False,False
                if needForward:
                    b1 = wbUsr.forward(task["wb_mid"], reason=reason, is_comment=needComment) #转发结果
                if needLike:
                    if task["wb_mid"] not in wbUsr.likeList:
                        b2 = wbUsr.like(task["wb_mid"])
                if b1 == False and b2 == False:
                    err_count += 1  # 做错误计数,如果连续失败,则应该跳过
                    if err_count > 5:
                        break
                    else:
                        continue
                err_count = 0  # 成功的话重置错误计数
                cur_succ_count += 1

                if b2: #如果是点赞成功,在这下面做记录,还有数据库同步处理
                    wbUsr.likeList.append(task["wb_mid"])
                    DB.DZ_log(None, uid=wbUsr.uid, username=wbUsr.usr, mid=task["wb_mid"])
                    DB.updata_wb_DZ(None,wbUsr.usr)
                    ret = DB.cha_data(None, wbUsr.usr, '点赞')  # 判断该账号当天是否记录关注
                    if ret == 1:
                        # 存在就更新
                        DB.updata_data(None, wbUsr.usr, '点赞', task_data=1)
                    else:
                        # 不存在就插入
                        DB.insert_data(None, wbUsr.usr, '点赞', 1, wbUsr.uid)
                if b1:#如果是转发成功,还有数据库同步处理
                    DB.ZF_log(None, uid=wbUsr.uid, username=wbUsr.usr, mid=task["wb_mid"])
                    DB.updata_wb_ZF(None,wbUsr.usr)
                    ret = DB.cha_data(None, wbUsr.usr, '转发')  # 判断该账号当天是否记录关注
                    if ret == 1:
                        # 存在就更新
                        DB.updata_data(None, wbUsr.usr, '转发', task_data=1)
                    else:
                        # 不存在就插入
                        DB.insert_data(None, wbUsr.usr, '转发', 1, wbUsr.uid)
                sync_dz = 1 if b2 else 0 #点赞成功反馈1
                sync_zf = 1 if b1 else 0 #转发成功反馈1
                if (b1 or b2) : #只要有一个成功,则同步数据
                    wbUsr.usrRunLog(0, u"转发点赞成功,同步到服务器结果[{}]".format(
                        WEIBO_ZFDZ_TASK_SYNC.syncData(name="weibo_apiAddTaskJindu_zfdz", a = task["id"],b = sync_dz,c = sync_zf)))
                time.sleep(config.GetConfig("m", 1))
        finally:
            wbUsr.usrSaveFile("like.ini", wbUsr.likeList, is_pickle=True)
    wbUsr.usrRunLog(0, u"完成微博转发评论点赞任务")


def do_task(index):

    @withSessionAutoFree(set_utf8=True)
    def get_user(self,cursor,time2):
        '''cursor 由装饰器withSessionAutoFree 传入,自动异常回滚,提交和关闭数据库'''
        cursor.execute(" SELECT username from user WHERE id=2 FOR UPDATE")
        a=int(cursor.fetchone().get('username'))
        time1 = int(time.time())
        cursor.execute("SELECT id,username,password from user WHERE id >'{}' and abn=0 and limit1=0 and ('{}'- endtime) >'{}' and type=0 LIMIT 1".format(a, time1,time2))
        d = cursor.fetchone()
        if not d:return
        id1 = d.get("id")
        cursor.execute("update user set type='1' where id='{}'".format(id1))
        if cursor.execute(
                "SELECT id,username,password from user WHERE id >'{}' and abn=0  and limit1=0 and ({}-endtime)>'{}' and type=0 LIMIT 1".format(
                        id1, time1, time2)) != 0:
            cursor.execute("UPDATE user set username ='{}' WHERE id=2".format(id1))
        else:
            cursor.execute("UPDATE user set username =0 WHERE id=2")
        return d

    while config.GetConfig("state") == 1:#状态 定义 0:未启动 1:已经启动 -1:正在结束
        user = get_user(None,config.GetConfig("t",0))
        if not user:
            print(u"暂无账号，等待10s")
            time.sleep(10)
            continue
        username = user.get("username")
        password = user.get("password")
        wbProxyPool = ProxyPool()
        wbUsr = WeiBoLogin(wbProxyPool)
        #查UA
        UA = DB.cha_UA(None,username)
        # 判断是否有ua
        if UA == None:
            #随机选择一个
            ua = UserAgent().random
            wbUsr.headers = {'User-Agent': ua}
            print(wbUsr.headers)
            #保存UA
        else:
            UA = eval(UA)
            wbUsr.headers = UA
        try:
            if wbUsr.login(username, password):
                res = wbUsr.isFreeze()
                if res == True:
                    DB.yichang(None,username)
                    DB.out_denglu(None,username)
                    continue
                #保存cookie，ua
                DB.save_UA(None,ua=wbUsr.headers,username=username,cookie=wbUsr.cookie)
                #判断wb表username是否存在
                ret = DB.cha_wb(None,username)
                if ret == 0:
                    DB.insert_wb(None,username)
                #判断updata表中是否存在uid，如果存在跳过一下两步
                ret = DB.is_get_uid(None,wbUsr.uid)
                if ret == 0:
                    DB.get_updata(None, wbUsr.uid)
                # 读取数据库，判断头像是否修改成功
                touxiang = DB.cha_head_status(None,wbUsr.uid)
                if touxiang == 0:   #0为没有修改成功  1为修改成功
                    imgbuf = getImg()
                    if imgbuf:
                        if wbUsr.revise_head(imgbuf):
                #             # 修改头像成功，保存到数据库updata中
                            DB.res_head_status(None,wbUsr.uid)
                            wbUsr.usrWriteConfig(u"帐号记录", u"修改头像", "1")  # 写配置记录头像已经修改成功
                    else:
                        wbUsr.usrRunLog(1, u"没有可用头像")
                # 读取数据库，判断信息是否修改成功
                info = DB.cha_info_status(None,wbUsr.uid)
                if info ==0:
                    nickname = getNickRand()
                    mydesc = getSignRand()
                    if nickname:
                        if wbUsr.changeInfo(nickname,mydesc=mydesc):
                            DB.res_info_status(None,wbUsr.uid)
                            wbUsr.usrWriteConfig(u"帐号记录", u"修改信息", "1") #写配置记录头像已经修改成功
                    else:
                        wbUsr.usrRunLog(1,u"没有可用信息")
                #转发 点赞  关注
                do_zfpldz(wbUsr)
                do_dd_pl(wbUsr)
                err_count = 0
                cur_succ_count = 0 #当前关注成功计数
                wbUsr.followList = wbUsr.usrReadFile("follows.ini", is_pickle=True,default_ret=[]) #从本地载入已经关注的列表
                try:
                    for task in WEIBO_GZ_TASK_SYNC.getTask()["json_list"]: #获取关注任务
                        #<------------这里做当单上限判断,还有当天上限判断
                        if cur_succ_count >=float( config.GetConfig("c",200)): #判断是否达到关注上限
                            break
                        if  wbUsr.followList and task["wb_uid"] in wbUsr.followList: #如果已经关注过,跳过
                            continue
                        if not WEIBO_GZ_TASK_SYNC.syncData(name="weibo_apiIsRuningTask_GZ", a = task["id"]):#查询订单是否还有效
                            continue
                        if not wbUsr.followed(task["wb_uid"]):
                            err_count+=1 #做错误计数,如果连续关注失败,则应该跳过关注
                            if err_count>5:
                                break
                            else:
                                continue
                        err_count = 0 #关注成功的话重置错误计数
                        cur_succ_count+=1
                        wbUsr.followList.append(task["wb_uid"])
                        DB.GZ_log(None,wbUsr.uid,username,task["wb_uid"])
                        wbUsr.usrRunLog(0,u"关注成功,同步到服务器结果[{}]".format(WEIBO_GZ_TASK_SYNC.syncData(name="weibo_apiAddTaskJindu_GZ", a = task["id"])))
                        time.sleep(int(config.GetConfig("m",1)))
                    #当前关注总数
                    DB.updata_wb_GZ(None,data=cur_succ_count,usr=username)
                    ret = DB.cha_data(None,username,'关注')  #判断该账号当天是否记录关注
                    if ret == 1:
                        #存在就更新
                        DB.updata_data(None,username,'关注',cur_succ_count)
                    else:
                        #不存在就插入
                        DB.insert_data(None,username,'关注',cur_succ_count,wbUsr.uid)
                    DB.out_denglu(None,username)
                        #<-------------这下面自己按照自己的数据库构造同步到数据库,关注间隔,等等....
                finally:
                    wbUsr.usrSaveFile("follows.ini", wbUsr.followList, is_pickle=True) #本地保存一份已经关注过的列表
                #关注间隔
                time.sleep(int(config.GetConfig("f", 1)))
                wbUsr.usrRunLog(0, u"完成微博关注任务")
            else:
                DB.out_denglu(None, username)
        except Exception as e:
            wbUsr.usrRunLog(u'{}出现错误'.format(username),traceback.print_exc())
            DB.out_denglu(None, username)


def do_dd_pl(wbUsr):
    wbUsr.usrRunLog(0, u"开始执行微博单独评论任务")
    err_count = 0
    cur_succ_count = 0  # 当前成功计数
    wbUsr.commentList = wbUsr.usrReadFile("comment.ini", is_pickle=True, default_ret=[])  # 从本地载入已经评论的列表
    res = wbUsr.isFreeze()
    if res == True:
        DB.yichang(None, wbUsr.usr)
        DB.out_denglu(None, wbUsr.usr)
    else:
        try:
            for task in WEIBO_PL_TASK_SYNC.getTask()["json_list"]:  # 获取评论任务
                # <------------这里做当单上限判断,还有当天上限判断
                if cur_succ_count >= float(config.GetConfig("c", 200)):  # 判断是否达到评论上限
                    break
                if wbUsr.commentList and task["wb_mid"] in wbUsr.commentList:  # 如果已经评论过,跳过
                    continue
                plid = task["id"]  # 获取评论ID
                if not WEIBO_PL_TASK_SYNC.syncData(name="weibo_apiIsRuningTask_PL", a=task["id"]):  # 查询订单是否还有效
                    continue
                reason = None
                if int(plid) > 0:
                    resData = {}  # 获取评论内容
                    if WEIBO_ZFDZ_TASK_SYNC.syncData(url="http://118.31.171.22/api2", name="api_wbGetzfpl", a=plid,
                                                     resData=resData):
                        reason = resData.get("msg")
                if not wbUsr.ddpl(task["wb_mid"],content=reason):
                    err_count += 1  # 做错误计数,如果连续关注失败,则应该跳过关注
                    if err_count > 5:
                        break
                    else:
                        continue
                err_count = 0  # 关注成功的话重置错误计数
                cur_succ_count += 1
                wbUsr.commentList.append(task["wb_mid"])
                DB.PL_log(None, uid=wbUsr.uid, username=wbUsr.usr, mid=task["wb_mid"])
                wbUsr.usrRunLog(0, u"评论成功,同步到服务器结果[{}]".format(WEIBO_GZ_TASK_SYNC.syncData(name="weibo_apiAddTaskJindu_pl", a=task["id"])))
            # DB.total_PL(None,cur_succ_count,wbUsr.usr)
            DB.updata_wb_PL(None,cur_succ_count,wbUsr.usr)
            ret = DB.cha_data(None, wbUsr.usr, '评论')  # 判断该账号当天是否记录关注
            if ret == 1:
                # 存在就更新
                DB.updata_data(None,  wbUsr.usr, '评论',task_data=cur_succ_count)
            else:
                # 不存在就插入
                DB.insert_data(None, wbUsr.usr, '评论', cur_succ_count, wbUsr.uid)
            time.sleep(int(config.GetConfig("m", 1)))
        finally:
            wbUsr.usrSaveFile("comment.ini", wbUsr.commentList, is_pickle=True)  # 本地保存一份已经评论过的列表
    wbUsr.usrRunLog(0, u"完成微博评论任务")


class thread_do(threading.Thread):
    '''启动多线程'''

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        config.ChangeConfig(state = 1) #设置任务启动
        thread_list = []
        for i in range(int(config.GetConfig("ThreadNum",1))):
            target = do_task
            thread_list.append(threading.Thread(target=target,args=(i,)))

        for i in thread_list:
            i.start()
        for i in thread_list:
            i.join()
        print (u"任务已完成", __file__)


# if __name__ == "__main__":
#     # print (getNickRand())
#     # print (getImgPath())
#     #print (getImg())
#     wbUsr = WeiBoLogin(None)
#     if wbUsr.login("13783560539", "sxn796595.."):
#         do_zfpldz(wbUsr)
#         do_dd_pl(wbUsr)
        # print (wbUsr.revise_head(getImg()))
        #print (wbUsr.changeInfo(None,getSignRand()))
        # wbUsr.followed("1839167003")
#





