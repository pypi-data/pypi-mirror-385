# -*-coding:utf-8-*-
"""
Created on 2024/11/13

@author: 臧韬

@desc: 默认描述
"""
import base64
import hashlib
import json
import time


class Sign(object):
    """
    这个签名算法用于认证服务和api授权元素
    """

    EXPIRE_TIME = 5 * 60 * 1000

    def __init__(self, secret):
        self.secret = secret

    def encode(self, args, timestamp):
        return self.getSign({**args, "timestamp": timestamp, "secret": self.secret})

    @staticmethod
    def getSign(args):
        nArgs = {}
        for k, v in args.items():
            nArgs[k.lower()] = v
        sortedKeys = sorted(nArgs.keys())
        params = []
        for key in sortedKeys:
            value = nArgs[key]
            if not isinstance(value, str):
                value = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            params.append(f"{key}={value}")
        # print("paramStr: {}".format("&".join(params).encode("utf-8")))
        # print("base64: {}".format(base64.b64encode("&".join(params).encode("utf-8"))))
        return hashlib.sha1(base64.b64encode("&".join(params).encode("utf-8"))).hexdigest()

    def verify(self, args):
        args = args.copy()
        timestamp = args.pop("timestamp")
        if abs(int(time.time() * 1000) - int(timestamp)) > self.EXPIRE_TIME:
            return False
        signature = args.pop("accessSign")
        return signature == self.encode(args, timestamp)
