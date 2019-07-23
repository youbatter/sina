#coding:utf-8
'''资源初始化'''

import os
import re,random

current_path = os.path.dirname(__file__)

#----------资源初始化----------
IMG_PATH = current_path + r"/../res\head_img_"
IMG_RES_LIST = os.listdir(IMG_PATH)

def getImgPath():
    '''获取一个随机头像路径'''
    return IMG_PATH + "/" + random.choice(IMG_RES_LIST)
def getImg():
    '''获取一个随机头像'''
    return open(getImgPath(),"rb").read()

def getNickRand():
    '''获取一个随机昵称'''
    return  "{}{}".format( random.choice(NICK_RES_LIST) ,random.randint(1987,2019))

def getSignRand():
    '''获取一个随机昵称'''
    return  random.choice(SIGN_RES_LIST)

with open(current_path + r"/../res/nick_sex.txt","rb") as f:
    NICK_RES_LIST = re.findall(r"^(.+?)[\r\n]$",f.read().decode("utf-8"),re.M)

with open(current_path + r"/../res/signature.txt","rb") as f:
    SIGN_RES_LIST = re.findall(r"^(.*?)[\r\n]$",f.read().decode("utf-8"),re.M)


print (u"载入头像资源[%s] 昵称[%s]个 签名[%s]个" \
      %(len(IMG_RES_LIST),len(NICK_RES_LIST),len(SIGN_RES_LIST)))