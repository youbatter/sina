#coding:utf-8
#pip install rsa
import rsa
import base64, binascii


def passRsa(password, pubkey, key_plus):
    rsaPublickey = int(pubkey, 16)

    key = rsa.PublicKey(rsaPublickey, int(key_plus, 16))  # 创建公钥
    message = password.encode('utf-8')  # 拼接明文js加密文件中得到
    passwd = rsa.encrypt(message, key)  # 加密
    passwd = binascii.b2a_hex(passwd)  # 将加密信息转换为16进制。
    return passwd.upper()