#coding:utf-8
import logging,os,time,threading
from logging.handlers import TimedRotatingFileHandler

CURRET_PATH = os.path.dirname(__file__)
LOG_FILE = CURRET_PATH + r"/../LOGFiles"

#################################################################################################
log_format = '[%(asctime)s] %(levelname)s[%(lineno)dL][%(thread)d]: %(message)s'
log_today = time.strftime('%Y-%m-%d',time.localtime())
if not os.path.isdir(LOG_FILE):os.mkdir(LOG_FILE)

log = logging.getLogger('')
fileTimeHandler = None

def setLog( fileName = "RunTime.log"):
    '''重新配置LOG日志'''
    global log,fileTimeHandler
    if fileTimeHandler:
        log.removeHandler(fileTimeHandler)
    fileTimeHandler = None
    #################################################################################################
    # 定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
    fileTimeHandler = TimedRotatingFileHandler(LOG_FILE + "/" + fileName, when = 'D', interval=2)
    fileTimeHandler.suffix = "%Y%m%d%H.log"  # 设置 切分后日志文件名的时间格式 默认 filename+"." + suffix 如果需要更改需要改logging 源码
    logging.basicConfig(level=logging.INFO,
                        filemode='a')  # 文件输出等级
    # console = logging.StreamHandler()
    fileTimeHandler.setLevel(logging.INFO)
    formatter = logging.Formatter(log_format)
    fileTimeHandler.setFormatter(formatter)

    # log.addHandler(console)
    log.addHandler(fileTimeHandler)
##########################################################################################
setLog()

class WriteLogs(object):
    def __init__(self):
        self.lock = threading.Lock()

    def write(self,_path,_outstr):
        '''写出日志'''
        self.lock.acquire()
        try:
            if not os.path.exists(_path): #判断文件是否存在,如果不存在则获取目录,然后判断目录是否存在
                dirname = os.path.dirname(_path)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
            with open(_path,"a+") as f:
                f.write(_outstr + "\n")
        except:
            pass
        finally:
            self.lock.release()

LOGWRITELOG = WriteLogs()
