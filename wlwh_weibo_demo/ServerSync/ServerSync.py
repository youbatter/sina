#coding:utf-8
'''
平台的数据同步都在这个模块处理
'''
import json
import time
import traceback
from threading import Lock,Semaphore
import requests

API_URL = "http://118.31.171.22/api/666/list"
API_URL_2 = "http://118.31.171.22/api/666"

class TaskClass (object):

    def __init__(self,taskType):
        self.last_time = 0
        self.lock = Lock()
        self.taskList = {}
        self.taskType = taskType
        self.Semaphore = Semaphore(30)  # 创建信号锁,避免服务器并发过高

    def getTask(self):
        '''获取指定任务列表'''
        params = {
            "name": self.taskType,
        }
        self.lock.acquire() #加锁
        try:
            if time.time() - self.last_time > 5:
                '''每5秒重新从服务器获取一次'''
                #print (u"开始重新获取关注任务列表")
                while True:
                    try:
                        self.taskList = requests.get(API_URL,params=params).json()
                        self.last_time = time.time()
                        break
                    except:
                        # 如果网络异常没有获取成功,延迟5秒后重新获取
                        time.sleep(5)
                        continue
        finally:
            self.lock.release() #解锁
        return self.taskList

    def syncData(self, **kwargs):
        '''数据提交同步,会一直提交直到提交成功'''
        '''可以传一个resData字典来接收返回数据'''
        ret = False
        needResData = False
        if u"resData" in kwargs:
            needResData = True
            resData = kwargs["resData"]
            del kwargs["resData"]
        url = API_URL_2
        if u"url" in kwargs:
            url = kwargs["url"]
            del kwargs["url"]
        params = {}
        params.update(kwargs)
        while True:
            self.Semaphore.acquire()
            try:
                res = requests.get(url, params=params, timeout=10).json()
                ret = len(res.keys()) >= 0
                if needResData:
                    for key in res:
                        resData[key] = res[key]
                break
            except:
                print(traceback.print_exc())
            finally:
                self.Semaphore.release()
            time.sleep(5)
        return ret


if __name__ == "__main__":
    task = TaskClass("weibo_apiGetTaskList_GZ")
    print (task.getTask())
    print (task.getTask())

    print (task.getTask())
    for i in task.getTask()["json_list"]:
        print (task.syncData(name="weibo_apiIsRuningTask_GZ", a=i["id"])) #这是查任务是否进行中
        #print (task.syncData(name="weibo_apiAddTaskJindu_GZ",a =i["id"])) #这是提交关注成功