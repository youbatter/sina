# coding:utf-8
import time
from ctypes import windll, c_char_p

import requests
def catch_DLLCALL_exception(origin_func):
    '''异常捕捉器'''
    def wrapper(self,*args, **kwargs):
        try:
            result = origin_func(self,*args, **kwargs)
            return result
        except Exception as e:
            #print 'an Exception raised.',e
            self.error = e.args
            return
    return wrapper
def catch_DLLCALL_exception_forAPI(self,origin_func):
    '''异常捕捉器'''
    def wrapper(*args, **kwargs):
        try:
            _args = []
            for i in range(len(args)):
                if isinstance(args[i], str):
                    _args.append(c_char_p(args[i]))
                else:
                    _args.append(args[i])
            nowtime = time.time()
            self.result_p = origin_func(*_args, **kwargs)
            return self.result_p
        except Exception as e:
            #print 'an Exception raised.',e
            self.error = e.args
        finally:
            self.runtime = time.time()-nowtime
    return wrapper
class DLLCALL(object):
    def __init__(self,path):
        self.mydll = windll.LoadLibrary(path)
        self.error = None
        self.result_p = None
        self.runtime = 0

    @catch_DLLCALL_exception
    def __getattr__(self, item):
        api_fun = catch_DLLCALL_exception_forAPI(self, getattr(self.mydll, item))  # 返回带装饰器的函数对象,方便做异常处理
        if api_fun:
            setattr(self, item, api_fun)
        return api_fun

    @catch_DLLCALL_exception
    def getMsg(self):
        return c_char_p(self.result_p).value
if __name__ == "__main__":
    import sys,requests
    sys.path.append("..")
    print(sys.path)

    dll = DLLCALL(r"C:\Users\Administrator\Wb_api\dll_lib\OCR.dll")
    img = requests.get("http://login.sina.com.cn/cgi/pin.php").content
    with open("a.png","wb") as f:
        f.write(img)
    print(dll.OCR_E(img,len(img)), dll.getMsg(),dll.error,dll.runtime)
    time.sleep(0.5)
    img = requests.get("http://login.sina.com.cn/cgi/pin.php").content
    with open("b.png","wb") as f:
        f.write(img)

    print(dll.OCR_E(img,len(img)),dll.getMsg(),dll.error,dll.runtime)
    #raw_input(">>>")
