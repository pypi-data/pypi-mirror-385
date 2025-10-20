# -*-coding:utf-8-*-
"""
Created on 2024/11/13

@author: 臧韬

@desc: 默认描述
"""
import json
import time

import requests
from requests import Response

from .api import JitApi
from ..common.error import ErrorMenu
from .sign import Sign
from .response import JitApiResponse
from ..common.enums import RequestMethodEnum


class JitApiRequest(object):

    def __init__(self):
        self.method = RequestMethodEnum.POST
        self.params = {}

    def setMethod(self, method):
        if method not in RequestMethodEnum.__dict__:
            raise requests.exceptions.RequestException("method is illegal")
        self.method = method

    def setParams(self, params):
        if not isinstance(params, dict):
            raise TypeError("参数应该是 字典 类型")
        self.params = params

    def execute(self, api: JitApi):
        if not isinstance(api, JitApi):
            raise TypeError("api 应该是 JitApi 类型")

        fullUrl = api.buildUrl()
        timestamp = int(time.time() * 1000)
        # timestamp = 1737011628994
        sign = Sign(api.accessSecret)
        accessSign = sign.encode(self.params, timestamp)
        # print("accessSign: {}".format(accessSign))
        headers = {
            "accessKey": api.accessKey,
            "timestamp": str(timestamp),
            "accessSign": accessSign
        }
        if api.debug:
            headers["debug"] = "1"
        try:
            response = requests.request(self.method, fullUrl, json=self.params, headers=headers)
        except requests.exceptions.ConnectionError:
            data = ErrorMenu.REQUEST_CONNECT_ERROR.toDict()
        else:
            data = self._handleResponse(response, api)

        return JitApiResponse(data)

    @staticmethod
    def _handleResponse(response: Response, api):
        statusCode = response.status_code
        if statusCode != 200:
            return ErrorMenu.STATUS_CODE_NOT_200.format(statusCode=statusCode).toDict()
        content = response.content
        try:
            respData = json.loads(content)
        except Exception as e:
            return ErrorMenu.RESPONSE_NOT_JSON.format(content=content[:50]).toDict()
        else:
            errcode = respData["errcode"]
            data = respData["data"]
            if errcode == 0:
                sign = Sign(api.accessSecret)
                if not sign.verify(data):
                    return ErrorMenu.SIGN_NOT_MATCH.toDict()
                data = data["data"]
            result = {
                "errcode": respData.get("errcode"),
                "errmsg": respData.get("errmsg"),
                "requestId": respData.get("requestId"),
                "data": data
            }

            if api.debug:
                result["debug"] = respData.get("respExtraData", {}).get("apiAuthDebug", {})
            return result
