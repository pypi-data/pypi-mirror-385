# -*-coding:utf-8-*-
"""
Created on 2024/11/13

@author: 臧韬

@desc: 默认描述
"""

import uuid


class ErrorResponse(object):
    def __init__(self, errcode, errmsg):
        self.errcode = errcode
        self.errmsg = errmsg

    def format(self, **kwargs):
        return self.__class__(errcode=self.errcode, errmsg=self.errmsg.format(**kwargs))

    @property
    def requestId(self):
        # 生成uuid，去掉中间斜杠
        reqId = str(uuid.uuid4()).replace("-", "")
        # 前面5位换成error
        return "error" + reqId[5:]

    def toDict(self):
        return {
            "errcode": self.errcode,
            "errmsg": self.errmsg,
            "requestId": self.requestId,
            "data": {}
        }


class ErrorMenu(object):
    REQUEST_CONNECT_ERROR = ErrorResponse(errcode=9000000, errmsg="HTTP请求连接失败")
    STATUS_CODE_NOT_200 = ErrorResponse(errcode=9000001, errmsg="HTTP请求状态码非200, 而是{statusCode}")
    RESPONSE_NOT_JSON = ErrorResponse(errcode=9000002, errmsg="HTTP请求返回结果不是JSON格式, 内容：{content}")
    SIGN_NOT_MATCH = ErrorResponse(errcode=9000003, errmsg="响应签名不匹配")
