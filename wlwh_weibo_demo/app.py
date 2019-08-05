#coding:utf-8
from flask import Flask,jsonify
from flask.globals import request
import weiboTask
import os
import json
import datetime
import config.config as config
import ProxyPool.proxyHttp
import mysqlDB.connDB as DB
config.LoadConfig() #载入配置文件
from flask_cors import CORS, cross_origin #导入包
from flask import render_template
from flask_bootstrap import Bootstrap
'''代理池设置'''
ProxyPool.proxyHttp.ProxyMinIp = 10
ProxyPool.proxyHttp.ProxyType = "http"
ProxyPool.proxyHttp.startAutoGetProxy("http://webapi.http.zhimacangku.com/getip?num=50&type=1&pro=&city=0&yys=0&port=11&pack=5725&ts=0&ys=0&cs=0&lb=1&sb=0&pb=45&mr=3&regions=","http")
app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['JSON_AS_ASCII'] = False
CORS(app, supports_credentials=True)#设置参数


@app.route('/')
def hello_world():
    return render_template("index.html",locals = locals())


@app.route('/Update',methods=['POST','GET'])
def Update():
    return render_template("Update.html",locals = locals())


@app.route('/Enter_data',methods=['POST','GET'])
def enter_data():
    return render_template("enter_data.html",locals = locals())


@app.route('/moren')
def do_thing():
    config.ChangeConfig(state = 1)
    while config.GetConfig("state") == 1:
        #状态 定义 0:未启动 1:已经启动 -1:正在结束
        print (u"正在任务中....")
    config.ChangeConfig(state=0)
    # print (u"任务完成")
    return jsonify({'code': '0', 'message': '任务完成'})


@app.route('/run',methods=['POST','GET'])
def run():
    '''启动线程'''
    if config.GetConfig("state") == 1:
        return u"任务正在执行中,请先暂停任务"
    n = request.form.get('n')  # 线程数
    config.ChangeConfig(ThreadNum=int(n))
    weiboTask.thread_do().start()
    return "ok"


@app.route('/stop',methods=['POST','GET'])
def stop():
    if config.GetConfig("state") == 1:
        config.ChangeConfig(state = -1)
        return u"任务下在结束中"
    elif config.GetConfig("state") == 0:
        return u"任务已结束,可以重新启动"


@app.route('/peizhi',methods=['POST','GET'])
def peizhi():
    result = {"msg":u'没有任务'}
    if request.method == 'GET':
        return json.dumps(result)
    else:
        n = request.form.get('n') #关注数量
        m = request.form.get('m')#关注间隔
        f =request.form.get('f') #每轮间隔时间
        t = request.form.get('t')#每个号限制下次登陆间隔
        like = request.form.get('like')#转发数量
        pl = request.form.get('pl')#评论数量
        config.ChangeConfig(n=n,m=m,f=f,t=t,like=like,pl=pl)
        result["msg"] = u"修改成功"
        return json.dumps(result)


@app.route('/get_account',methods=['POST','GET'])
def get_account():
    if request.method == 'POST':
        file = request.files.get('file')
        print(file)
        if not file:
            return jsonify({'code': '0', 'message': '没有数据要展示'})
        # 文件名
        pic_name = file.filename
        # 文件写入磁盘
        file.save(pic_name)
        #处理文件内容
        with open(pic_name, 'r+') as f:
            data = f.readlines()
        lc = []
        for line in data:
            dit = []
            # 处理内容
            if '----' in line:
                A = line.strip('\n').split('----')
            else:
                A = line.strip('\n').split('\t')
            dit.append(0)
            dit.append(A[0])
            dit.append(A[1])
            dit.append(0)
            dit.append(0)
            time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            dit.append(time)
            dit.append(0)
            dit.append(0)
            dit.append(None)
            dit.append(None)
            lc.append(dit)
        DB.enter_data(None,lc)
        return json.dumps(data)
        # return render_template('enter_data.html', data=data)
    else:
        return json.dumps('没有导入账号')


@app.route('/Show_usr')
def Show_usr():
    #分页查询
    page = int(request.args.get('page',1))
    # u = DB.cha_user(None,page)
    u = DB.time_order(None,page)
    return render_template("Show_usr.html", u=u)


@app.route('/rizhi', methods=['POST', 'GET'])
def rizhi():
    if request.method == 'GET':
        usr = request.args.get('usr')
        usr = json.loads(usr)
        log = DB.cha_log(None,usr)
        if log:
            return render_template('log.html',log=log)
        else:
            return render_template('log.html',log='无')


@app.route('/Status')
def stauts():
    u = DB.status_doing(None)
    if u:
        return render_template("status.html",u = u)
    else:
        return render_template('status.html',u = '没有运行的账号')


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80)


#多表查询sql语句的优化
#发4100+600+800=5500-1000=4500- 3000 = 1500
#