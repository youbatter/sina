#coding:utf-8
from flask import Flask,jsonify
from flask.globals import request
import weiboTask
import os
import config.config as config
import ProxyPool.proxyHttp
config.LoadConfig() #载入配置文件

'''代理池设置'''
ProxyPool.proxyHttp.ProxyMinIp = 10
ProxyPool.proxyHttp.ProxyType = "http"
ProxyPool.proxyHttp.startAutoGetProxy("http://webapi.http.zhimacangku.com/getip?num=50&type=1&pro=&city=0&yys=0&port=11&pack=5725&ts=0&ys=0&cs=0&lb=1&sb=0&pb=45&mr=3&regions=","http")
app = Flask(__name__)



@app.route('/')
def hello_world():
    return jsonify('Hello World!')

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
    if request.method == 'GET':
        return jsonify({'code': '0', 'message': '没有任务'})
    else:
        if config.GetConfig("state") == 1:
            return jsonify({'code': '1', 'message': '任务进行中，请先暂停任务'})   #1 线程执行中
        n = request.form.get('n') #关注数量
        config.ChangeConfig(ThreadNum=n)
        weiboTask.thread_do().start()
        data = {'n':n}
        return jsonify({'code': '1', 'message': '任务进行中','data':data})


@app.route('/stop')
def stop():
    if config.GetConfig("state") == 1:
        config.ChangeConfig(state = -1)
        return jsonify({'code': '1', 'message': '任务正在进行中，请稍后'})
    elif config.GetConfig("state") == 0:
        return jsonify({'code': '0', 'message': '任务已经结束，可以重新启动'})


@app.route('/peizhi',methods=['POST','GET'])
def peizhi():
    if request.method == 'POST':
        n = request.form.get('n') #关注数量
        m = request.form.get('m')#关注间隔
        f =request.form.get('f') #每轮间隔时间
        t = request.form.get('t')#每个号限制下次登陆间隔
        like = request.form.get('like')#每个号限制下次登陆间隔
        pl = request.form.get('pl')#每个号限制下次登陆间隔
        config.ChangeConfig(n=n,m=m,f=f,t=t,like=like,pl=pl)
        data = {
            'n':n,
            'm':m,
            'f':f,
            't':t,
            'like':like,
            'pl':pl,
        }
        return jsonify({'code': '1', 'message': '配置修改成功', 'data': data})
    else:
        return jsonify({'code': '0', 'message': '不需要修改配置'})


@app.route('/peizhi',methods=['POST','GET'])
def show_data():
    pass


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80)