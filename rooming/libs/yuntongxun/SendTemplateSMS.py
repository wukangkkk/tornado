#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from CCPRestSDK import REST
import ConfigParser
import logging

#主帐号
accountSid= '8aaf07086812057f0168230c757d0789';

#主帐号Token
accountToken= '7d55e99d81c24196849b2748bc5aec22';

#应用Id
appId='8aaf07086812057f0168230c75d60790';

#请求地址，格式如下，不需要写http://
serverIP='app.cloopen.com';

#请求端口 
serverPort='8883';

#REST版本号
softVersion='2013-12-26';

  # 发送模板短信
  # @param to 手机号码
  # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# @param $tempId 模板Id

# def sendTemplateSMS(to,datas,tempId):
#
#
#     #初始化REST SDK
#     rest = REST(serverIP,serverPort,softVersion)
#     rest.setAccount(accountSid,accountToken)
#     rest.setAppId(appId)
#
#     result = rest.sendTemplateSMS(to,datas,tempId)
#     for k,v in result.iteritems():
#
#         if k=='templateSMS' :
#                 for k,s in v.iteritems():
#                     print '%s:%s' % (k, s)
#         else:
#             print '%s:%s' % (k, v)


class CCP(object):

    def __init__(self):
        self.rest = REST(serverIP, serverPort, softVersion)
        self.rest.setAccount(accountSid, accountToken)
        self.rest.setAppId(appId)

    @staticmethod
    def instance():
        if not hasattr(CCP, "_instance"):
            CCP._instance = CCP()
        return CCP._instance

    def sendTemplateSMS(self, to, datas, tempId):
        try:
            result = self.rest.sendTemplateSMS(to, datas, tempId)
        except Exception as e:
            logging.error(e)
            raise e

        # print result
        # for k, v in result.iteritems():
        #     if k == 'templateSMS':
        #         for k, s in v.iteritems():
        #             print '%s:%s' % (k, s)
        #     else:
        #         print '%s:%s' % (k, v)
        if result.get("statusCode") == "000000":
            return True
        else:
            return False

ccp = CCP.instance()

if __name__ == "__main__":
    ccp = CCP.instance()
    ccp.sendTemplateSMS("18260036027", ["1234", 5], 1)



   
#sendTemplateSMS(手机号码,内容数据,模板Id)