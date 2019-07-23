#coding:utf-8
import requests,traceback
import threading,time,re
try:
    from queue import Queue,Empty
except:
    from Queue import Queue,Empty


#设置全局变量
proxyQueue = Queue() #保存代理列表
proxyLock = threading.Condition() #代理获取通知锁

ProxySwitch = False
ProxyType = "http"
ProxyUrl = ""
ProxyMinIp = 5

def autoGetProxy():
    '''后台线程函数,等待通知,自动获取填充代理IP'''
    global proxyLock,proxyQueue
    print("autoGetProxy ready:",proxyLock.acquire())#先锁起来,然后等待解锁
    try:
        while ProxySwitch:#等待获取通知
            proxyLock.wait()
            print(u"开始填充代理IP,当前数量:%d" %proxyQueue.qsize())
            while True:#获取代理IP,直到获取成功
                try:
                    res = requests.get(ProxyUrl,timeout=15)
                    if res.status_code == 200:
                        need_add_white = re.search(u'请将(.*?)设置为',res.text)
                        if need_add_white:
                            need_add_white = need_add_white.group(1)
                            requests.get("http://web.http.cnapi.cc/index/index/save_white?neek=26979&appkey=b4b522a5e77521c95baa5e5a39fa7c07&white="+need_add_white)

                        m = re.findall("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+)",res.text)
                        if m:
                            proxyQueue.not_full.acquire()
                            #批量写入到列队里面
                            try:
                                for i in m:
                                    proxyQueue._put(i)
                                    proxyQueue.unfinished_tasks += 1
                                    
                            finally:
                                proxyQueue.not_empty.notify()
                                proxyQueue.not_full.release()
                                #time.sleep(5) 测试用
                                proxyLock.notify()
                                print(u"填充代理IP列表成功,当前数量:%d" %proxyQueue.qsize())
                        else:
                            #print res.text
                            proxyLock.notify()
                            proxyLock.wait()
                            time.sleep(3)
                            continue
                        break
                except :
                    print (traceback.print_exc())
                proxyLock.notify()
                proxyLock.wait()
                #time.sleep(5)  # 如果发生异常,则延迟后 继续

    finally:
        proxyLock.release()
            
def GetProxy(
                ms = 10,#设置等待时间,默认无限等待
                getstop=5#尝试获取次数,超过次数则放弃获取
             ):
    '''获取代理IP'''
    global proxyLock,proxyQueue,ProxyType
    proxyLock.acquire()
    try:
        for i in range(getstop):
            try:
                proxy_ip = proxyQueue.get_nowait()
                #如果当前可用IP数低于min,则通知获取
                if proxyQueue.qsize()<=ProxyMinIp:
                    proxyLock.notify()
                print(u"获取代理IP成功,当前数量:%d" %proxyQueue.qsize())
                return proxy_ip
            except Empty:
                proxyLock.notify()
                proxyLock.wait(timeout=ms)
            except :
                print (traceback.print_exc())
    finally:
        proxyLock.release()

def startAutoGetProxy(url,proxy_type = "https"):
    '''启动后台线程,自动填充代理IP池 '''
    global ProxyType,ProxyUrl,ProxySwitch
    ProxyType = proxy_type
    ProxyUrl = url
    print ("startAutoGetProxy",ProxySwitch)
    if not ProxySwitch:
        ProxySwitch = True
        threading.Thread(target=autoGetProxy).start()
    
def getProxyType():
    global ProxyType, ProxyUrl
    return ProxyType
def setProxyType(proxy_type):
    global ProxyType
    ProxyType = proxy_type

class ProxyPool():
    def __init__(self
                    ,waitTime=10 #设置等待时间,默认无限等待
                    ,getTry = 5#尝试获取次数,超过次数则放弃获取
                 ):
        self.waitTime = waitTime
        self.getTry = getTry

    def get(self):
        proxy_ip =  GetProxy(self.waitTime,self.getTry)
        if proxy_ip:
            return {"http":r"{}://{}".format(ProxyType,proxy_ip),"https":r"{}://{}".format(ProxyType,proxy_ip)}

if __name__ == "__main__":
    startAutoGetProxy("http://webapi.http.zhimacangku.com/getip?num=50&type=1&pro=&city=0&yys=0&port=11&pack=5725&ts=0&ys=0&cs=0&lb=1&sb=0&pb=45&mr=3&regions=","http")
    proxies=  ProxyPool().get()
    print (proxies)
    print (requests.get("https://myip.ipip.net",proxies=proxies).text)
