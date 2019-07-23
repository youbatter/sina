#coding:utf-8
'''
微博接口类,处理微博登录,关注,转发等操作
'''
try:
    import configparser as ConfigParser
except:
    import ConfigParser
import codecs
import pickle
import threading

from misc.dll_call import DLLCALL
from misc.misc  import passRsa
from logs.logs import log


import base64
import json
import os
import random
import re
import time
import urllib
import requests
import traceback
from functools import wraps
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
CURRET_PATH = os.path.dirname(__file__)
OCRDLL_PATH = CURRET_PATH + r"/../dll_lib/OCR.dll"
HOMEPATH = os.environ['HOMEPATH']
HOMEPATH = os.path.join("c:/",HOMEPATH)
Documents = os.path.join(HOMEPATH,"Documents")
wbUserDirs = os.path.join(Documents, "wbUserDirs")
if not os.path.exists(wbUserDirs):
    os.makedirs(wbUserDirs)
assert os.path.exists(wbUserDirs), u"wbUserDirs 目录创建失败!"
print (wbUserDirs)

class WeiBoLogin:

    def weiboExcept(func):
        '''捕捉异常装饰器,遇到异常只打印,不抛出异常'''
        @wraps(func)
        def wrapped_function(self, *args, **kwargs):
            #log_string = func.__name__ + " was called"
            #print(log_string)
            result = None
            try:
                result = func(self, *args, **kwargs)
            except:
                print(traceback.print_exc())
            return result

        return wrapped_function

    def auto_conn_proxy(attempts=3):  # 定义一个专门处理代理连接问题的装饰器
        def _decorator(func):
            @wraps(func)
            def wrapped_function(self, *args, **kwargs):
                #log_string = func.__name__ + " was called"
                #print(log_string)
                if self.ProxyPool:#判断是否开启代理器
                    if not self.proxies:
                        self.proxies = self.ProxyPool.get()

                result = None
                for i in range(attempts):
                    try:
                        result = func(self, *args, **kwargs)
                    except (requests.exceptions.ProxyError, requests.exceptions.ReadTimeout,
                            requests.exceptions.ConnectTimeout,requests.exceptions.ConnectionError):  # 几种异常一起处理
                        if self.ProxyPool:
                            self.proxies = self.ProxyPool.get()
                        continue
                    # except: 其他错误外部自己处理
                    #     print(traceback.print_exc())
                    break
                return result
            return wrapped_function
        return _decorator

    @weiboExcept
    def usrRunLog(self, level, *arg):
        '''帐号运行日志,需要先成功获取帐号'''
        run_log = [log.info, log.warn,log.debug][level]
        usrName = self.usr if self.usr else "default"
        try:
            if len(arg)==1 and isinstance(arg[0],(str,dict)):
                run_log(u"('%s', %s)"  %(usrName, arg[0]))
            else:
                run_log((usrName, arg))
        except:
            print (traceback.print_exc())

    def usrSaveFile(self,saveFileName,saveData,is_pickle=False,mode="wb"):
        '''保存用户数据'''
        if self.userPath:
            saveFilePath = u"%s/%s.txt" %(self.userPath,saveFileName)
            try:
                self.ConfigLock.acquire()
                with open(saveFilePath,mode) as f:
                    if is_pickle:
                        pickle.dump(saveData,f)
                    else:
                        f.write(saveData)
            except :
                #self.usrRunLog(1, traceback.format_exc())
                self.usrRunLog(1,u"usrSaveFile[%s]" %saveFilePath)
            finally:
                self.ConfigLock.release()

    def usrReadFile(self,ReadFileName,is_pickle=False,mode="rb",default_ret=None):
        '''读取用户数据'''
        if self.userPath:
            ret = default_ret
            ReadFilePath = u"%s/%s.txt" %(self.userPath,ReadFileName)
            if not os.path.isfile(ReadFilePath):return ret
            try:
                self.ConfigLock.acquire()
                with open(ReadFilePath,mode) as f:
                    if is_pickle:
                        ret = pickle.load(f)
                    else:
                        ret =  f.read()
            except Exception as e:
                print (traceback.print_exc())
                self.usrRunLog(1,u"usrReadFile[%s]" %ReadFilePath,e)
            finally:
                self.ConfigLock.release()
            return ret

    def usrReadConfig(self,section,option,default=None):
        '''读取用户配置'''
        ret = None
        FilePath = u"%s/config.ini" % (self.userPath)
        cp = ConfigParser.SafeConfigParser()
        try:
            with codecs.open(FilePath, 'r', encoding='utf-8') as f:
                cp.readfp(f)
            ret = cp.get(section, option)
        except :
            pass
        ret = default if not ret else ret
        return ret

    def usrWriteConfig(self,section,option,writeValue):
        '''写用户配置'''
        ret = None
        FilePath = u"%s/config.ini" % (self.userPath)
        cp = ConfigParser.SafeConfigParser()
        try:
            with codecs.open(FilePath, 'a+', encoding='utf-8') as f:
                cp.readfp(f)
            with codecs.open(FilePath, 'w+', encoding='utf-8') as f:
                if not cp.has_section(section):
                    cp.add_section(section)
                cp.set(section, option,writeValue)
                cp.write(f)
        except:
            self.usrRunLog(1,traceback.format_exc())

    def __init__(self,ProxyPool_obj):
        self.session = requests.session()
        self.usr,self.psw,self.uid,self.nick = None,None,None,None
        try:
            self.OCRDLL = DLLCALL(OCRDLL_PATH)
        except:
            self.OCRDLL = None
        self.cookie =  None
        self.ProxyPool = ProxyPool_obj #设置一个代理获取器对象,用来自动获取代理
        self.proxies = None
        self.userPath = None
        self.followList = None #记录已关注列表
        self.likeList = None #记录已点赞列表
        self.commentList = None
        self.isLogin = False #是否登录成功
        self.ConfigLock = threading.Lock()
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.15 (KHTML, like Gecko) Chrome/24.0.1295.0 Safari/537.15"} #None

    @auto_conn_proxy(attempts=5)
    def weibo_get(self, url, cookies=None, proxies=None, headers=None, timeout=30, **kwargs):
        if not cookies: cookies = self.cookie
        if not proxies: proxies = self.proxies
        if not headers: headers = self.headers.copy()
        if u"Referer" not in headers:
            headers["Referer"] = url
        return self.session.get(url, cookies=cookies, proxies=proxies, headers=headers,verify=False, timeout=timeout, **kwargs)

    @auto_conn_proxy(attempts=5)
    def weibo_post(self, url, data, cookies=None, proxies=None, headers=None, timeout=30, **kwargs):
        if not cookies: cookies = self.cookie
        if not proxies: proxies = self.proxies
        if not headers: headers = self.headers.copy()
        if u"Referer" not in headers:
            headers["Referer"] = url
        return self.session.post(url, data=data, cookies=cookies, proxies=proxies, headers=headers, timeout=timeout,verify=False,
                                 **kwargs)

    @weiboExcept
    def login(self,usr,psw):
        def get_cha(pcid):
            cha_url = "http://login.sina.com.cn/cgi/pin.php?r=" + str(
                int(random.random() * 100000000)) + "&s=0&p=" + pcid
            cha_page = self.weibo_get(cha_url)

            img = cha_page.content
            if self.OCRDLL:
                retCode = self.OCRDLL.OCR_E(img, len(img))
                retCode = self.OCRDLL.getMsg()
            else:
                with open("cha.jpg", 'wb') as f:
                    f.write(cha_page.content)
                    f.close()
                retCode = input("code:")
            return retCode
        self.usr = usr
        self.psw = psw
        su = base64.b64encode(usr.encode('utf-8')).decode()
        url = "https://login.sina.com.cn/sso/prelogin.php?entry=account&su=%s&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_=%d"%(su,(int(time.time()*1000)))
        res_login_frist = self.weibo_get(url).json()
        print (res_login_frist)
        for try_login in range(4):
            sp = passRsa("%s\t%s\n%s" % (res_login_frist["servertime"], res_login_frist["nonce"], psw), res_login_frist["pubkey"], "10001")
            data = {
                'encoding': 'utf-8', 'entry': 'weibo','gateway': '1', 'nonce': res_login_frist["nonce"],
                'pagerefer': 'https://login.sina.com.cn/crossdomain2.php?action=logout&r=https%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D%252F',
                'prelt': '22', 'pwencode': 'rsa2','qrcode_flag': 'false',
                'returntype': 'TEXT',#返回JSON格式
                'rsakv': res_login_frist["rsakv"],'savestate': '7', 'servertime': int(time.time()),'service': 'miniblog','sp': sp,
                'sr': '1920*1080','su': su,'url': 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
                'useticket': '1','vsnf': '1'}
            url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)&_={}'.format(int(time.time() * 1000))
            code = get_cha(res_login_frist["pcid"]) #强制打码登录
            data['pcid'] = res_login_frist["pcid"]
            data['door'] = code
            login_result = self.weibo_post(url,data=data).json()
            self.usrRunLog(0, json.dumps(login_result,ensure_ascii=False))
            if login_result["retcode"] == u"0":
                '''登录成功'''
                self.uid = login_result["uid"]
                self.nick = login_result["nick"]
                self.isLogin = True
                self.cookie = requests.utils.dict_from_cookiejar(self.session.cookies)
                self.userPath = os.path.join(wbUserDirs, self.usr)
                if not os.path.exists(self.userPath): #创建用户目录
                    os.mkdir(self.userPath)
                self.usrRunLog(0,u"登录成功")
                return True
            elif u'输入的验证码不正确' in login_result["reason"]:
                continue
            elif login_result["retcode"] == u"4040":
                '''登录次数太多'''
                self.usrRunLog(1,u"登录次数太多")
                break
            else:
                break

    @weiboExcept
    def isFreeze(self):
        '''判断号码是否异常'''
        res = self.weibo_get("https://weibo.com/", allow_redirects=False)
        if u"'/unfreeze'" in res.headers.get("Location", ""):
            return True

    @weiboExcept
    def revise_head(self,imgbuf):
        '''修改头像'''
        if not self.isLogin:return
        def get_rid():
            get_rid = None
            html = self.weibo_get("https://account.weibo.com/set/photo")
            if html.status_code == 200:
                try:
                    get_rid = re.search("setting_rid = '(.*?)';", html.text).group(1)
                except Exception as e:
                    self.usrRunLog(1, e,'没有setting_rid,换下一个号')
                    exit()
            if not get_rid:
                self.usrRunLog(1, '修改头像获取rid失败')
                return
            return get_rid

        rid = get_rid()
        if not rid:return
        headers = self.headers.copy()
        headers['Referer'] = 'https://account.weibo.com/set/aj5/photo/upload'
        data = {"setting_rid": rid}
        files = {'Filedata': ("img.jpg", imgbuf, "image/jpeg", {})}
        res = self.weibo_post("https://account.weibo.com/set/aj5/photo/upload",data=data,files=files,headers=headers)
        if res.status_code == 200 and u'"ret":1' in res.text:
            self.usrRunLog(0,u"头像上传成功")
            return True
        else:
            self.usrRunLog(0, u"头像上传失败:" + res.text)

    @weiboExcept
    def get_rid(self):
        if not self.isLogin: return
        url = 'https://account.weibo.com/set/iframe?skin=skin048'
        r = self.weibo_get(url)
        res = re.findall(r"<title>(.*)</title>", r.text)
        if res:
            title = res[0]
            if u"个人" in title:
                rid = re.findall(r'value=\"(.*?)\"', r.text)[0]
                return rid

    @weiboExcept
    def changeInfo(self,nickname,mydesc="",province="41",Date_Year="1991",birthday_m="12",birthday_d="31"):
        '''修改资料'''
        if not self.isLogin: return
        grid = self.get_rid()
        if not grid:return
        data = {
            'setting_rid': grid,
            'oldnick': self.nick,
            'nickname': nickname,
            'realname': '',
            'gender': 'm',
            'blog': '',
            'mydesc': mydesc,
            'province': province,
            'city': '1',
            'love': '',
            'Date_Year': Date_Year,
            'birthday_m': birthday_m,
            'birthday_d': birthday_d,
        }
        headers = self.headers.copy()
        headers['Referer'] = 'https://account.weibo.com/set/iframe?skin=skin048'
        url = 'https://account.weibo.com/set/aj/iframe/editinfo'
        result = self.weibo_post(url=url, headers=headers, data=data).json()
        if result["code"] == "100000":
            self.usrRunLog(0,u"修改资料成功")
            return True
        elif result["code"] == "100001":
            self.usrRunLog(1, u"修改资料-系统繁忙")
        else:
            self.usrRunLog(1, u"修改资料失败!"+json.dumps(result,ensure_ascii=False))

    @weiboExcept
    def followed(self, wb_uid):
        res = self.weibo_get("https://weibo.com/u/" + wb_uid)
        try:
            refer = re.search(r"uid=\d+&fnick=.*?&f=1&refer_flag=.*?&refer_lflag=&refer_from=profile_headerv6",
                              res.text, re.S).group(0)
            fnick = re.search(r"&fnick=(.*?)&", refer).group(1)
            refer = refer.replace(fnick, urllib.parse.quote(fnick.encode("utf-8")))
            location = re.search(r"CONFIG\['location'\]='(.*?)';", res.text).group(1)
        except:
            location = ""
            refer = "uid={}&fnick=&f=1&refer_flag=&refer_lflag=&refer_from=profile_headerv6".format(wb_uid)

        url = "https://weibo.com/aj/f/followed?ajwvr=6&__rnd=" + "1562815650613"
        post = refer + "&location=" + location + "&oid=" + wb_uid + "&wforce=1&nogroup=false"
        headers = self.headers.copy()
        headers.update({
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": url,  # 这个一定要加上
            })
        res = self.weibo_post(url, data=post, headers=headers).json()
        if res["code"] == u"100000":
            self.usrRunLog(0,u"关注[{}]成功".format(wb_uid))
            return True
        if res["code"] == u"100003":
            self.usrRunLog(0,u"关注[{}]失败，账号异常".format(wb_uid))
        else:
            self.usrRunLog(0, u"关注[{}]失败:{}".format(wb_uid,json.dumps(res,ensure_ascii=False)))

    @weiboExcept
    def isFreeze(self):
        '''判断号码是否异常'''
        res = self.weibo_get("https://weibo.com/", allow_redirects=False)
        if u"/unfreeze" in res.headers.get("Location", ""):
            return True

    @weiboExcept
    def forward(self, mid, reason, is_comment=0):
        '''转发和评论'''
        if not self.isLogin: return
        url = "https://weibo.com/aj/v6/mblog/forward?ajwvr=6&__rnd={}".format(int(time.time() * 1000))
        post = "pic_src=&pic_id=&appkey=&mid={mid}&style_type=2&mark=&reason={reason}&location=&pdetail=&module=&page_module_id=&refer_sort=&is_comment={is_comment}&rank=0&rankid=&rid=&_t=0".format(
            mid=mid, reason=urllib.parse.quote(reason), is_comment=is_comment
        )
        if is_comment: post += "&is_comment_base=1"
        headers = self.headers.copy()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["X-Requested-With"] = "XMLHttpRequest"
        res = self.weibo_post(url, data=post, headers=headers).json()
        if res["code"] == u"100000":
            self.usrRunLog(0, u"转发[{}]成功".format(mid))
            return True
        else:
            self.usrRunLog(0, u"转发[{}]失败:{}".format(mid, json.dumps(res, ensure_ascii=False)))
            return False

    @weiboExcept
    def like(self, mid):
        '''点赞'''
        url = "https://weibo.com/aj/v6/like/add?ajwvr=6&__rnd={}".format(int(time.time() * 1000))
        post = "location=&rid=&version=mini&qid=heart&mid={mid}&loc=profile&cuslike=1&_t=0".format(mid=mid)
        headers = self.headers.copy()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["X-Requested-With"] = "XMLHttpRequest"
        res = self.weibo_post(url, data=post, headers=headers).json()
        if res["code"] == u"100000":
            self.usrRunLog(0, u"点赞[{}]成功".format(mid))
            return True
        else:
            self.usrRunLog(0, u"点赞[{}]失败:{}".format(mid, json.dumps(res, ensure_ascii=False)))
            return False

    @weiboExcept
    def ddpl(self,mid,content):
        if not self.isLogin: return
        url = 'https://weibo.com/aj/v6/comment/add?ajwvr=6&__rnd={}'.format(int(time.time() * 1000))
        post = "act=post&mid={mid}&uid={uid}&forward=0&isroot=0&content={content}&location=&module=scommlist&group_source=&filter_actionlog=&_t=0&pdetail=".format(mid=mid,uid=self.uid,content=urllib.parse.quote(content))
        headers = self.headers.copy()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["X-Requested-With"] = "XMLHttpRequest"
        res = self.weibo_post(url, data=post, headers=headers).json()
        if res["code"] == u"100000":
            self.usrRunLog(0, u"评论[{}]成功".format(mid))
            return True
        else:
            self.usrRunLog(0, u"评论[{}]失败:{}".format(mid, json.dumps(res, ensure_ascii=False)))


if __name__ == "__main__":
    WeiBoLogin(None).login("15269797480","aaaaa88888")