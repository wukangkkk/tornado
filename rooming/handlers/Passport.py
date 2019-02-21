#coding=utf-8
from .BaseHandler import BaseHandler
import logging
import hashlib
import config
import re

from utils.response_code import RET
from utils.session import Session
from utils.commom import required_login

class RegisterHandler(BaseHandler):
    """
    注释说明
    """
    def post(self):
        #获取参数
        mobile=self.json_args.get("mobile")
        sms_code=self.json_args.get("phonecode")
        password=self.json_args.get("password")

        #检查参数
        if not all([mobile,sms_code,password]):
            return self.write(dict(errcode=RET.PARAMERR,errmsg="参数不完整"))
        if not re.match(r"^1\d{10}$",mobile):
            return self.write(dict(errcode=RET.DATAERR,errmsg="手机格式错误"))

        #如果产品对于密码长度有限制,需要在此做判断
        #判断验证码是否正确
        if "2468"!=sms_code:
            try:
                real_sms_code=self.redis.get("sms_code_%s"%mobile)
            except Exception as e:
                logging.error(e)
                return self.write(dict(errcode=RET.DBERR,errsmg="查询验证码出错"))
            #判断验证码是否出错
            if not real_sms_code:
                return self.write(dict(errcode=RET.NODATA,errsmg="验证码过期"))

            if real_sms_code !=sms_code:
                return self.write(dict(errcode=RET.DATAERR,ersmg="验证码错误"))
            try:
                self.redis.delete("sms_code_%s"%mobile)
            except Exception as e:
                logging.error(e)

        #保存数据,同时判断手机号是否存在，判断依据是数据库中mobile字段的唯一约束

        passwd=hashlib.sha256(password+config.passwd_hash_key).hexdigest()
        sql="insert into ih_user_profile(up_name,up_mobile,up_passwd) value(%(name)s,%(mobile)s,%(passwd)s);"
        try:
            user_id=self.db.execute(sql,name=mobile,mobile=mobile,passwd=passwd)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.DATAEXIST,errmsg="手机号码存在"))
        #用　session记录用户的登录状态记录
        self.session=Session(self)
        self.session.data["user_id"]=user_id
        self.session.data["mobile"]=mobile
        self.session.data["name"]=mobile
        try:
            self.session.save()
        except Exception as e:
            logging.error(e)
        self.write(dict(errcode=RET.OK,errmsg="注册成功"))

class LoginHandler(BaseHandler):
    """登录操作"""
    def post(self):
        #获取参数
        mobile=self.json_args.get("mobile")
        password=self.json_args.get("password")
        #检查参数
        if not all([mobile,password]):
            return self.write(dict(errcode=RET.PARAMERR,errmsg="参数错误"))
        if not re.match(r"^1\d{10}$",mobile):
            return self.write(dict(errcode=RET.DATAERR,errmsg="手机号错误"))

        #检查密码是否错误
        res=self.db.get("select up_user_id,up_name,up_passwd from ih_user_profile where up_mobile=%(mobile)s",
                        mobile=mobile)
        password=hashlib.sha256(password+config.passwd_hash_key).hexdigest()

        if res and res["up_passwd"]==unicode(password):
            #如果res存在密码同时成立,生成session数据
            #返回客户端

            try:
                self.session=Session(self)
                self.session.data["user_id"]=res["up_user_id"]
                self.session.data["name"]=res["up_name"]
                self.session.data["mobile"]=mobile
                self.session.save()
                print('-----test2----')
            except Exception as e:
                logging.error(e)
            return self.write(dict(errcode=RET.OK,errmsg="OK"))
        else:
            return self.write(dict(errcode=RET.DATAERR,errmsg="手机号或密码错误"))

class LogoutHandler(BaseHandler):
    """退出登录"""
    @required_login
    def get(self):
        #清除session
        #session=Session(self)
        self.session.clear()
        self.write(dict(errcode=RET.OK,errmsg="退出成功"))

class CheckLoginHandler(BaseHandler):
    """检查登录状态"""
    def get(self):
        #get_current_user方法在基类中已经实现,它的返回值是session.data保存在redis中
        #如果为｛｝，意味着用户未登录，否则代表用户已经登录
        if self.get_current_user():
            self.write({"errcode":RET.OK,"errmsg":"true","data":{"name":self.session.data.get('name')}})
        else:
            self.write({"errcode":RET.SESSIONERR,"errmsg":"false"})







































