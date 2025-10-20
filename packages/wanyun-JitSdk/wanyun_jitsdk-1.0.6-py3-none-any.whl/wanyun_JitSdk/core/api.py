# -*-coding:utf-8-*-
"""
Created on 2024/11/13

@author: 臧韬

@desc: 默认描述
"""


class JitApi(object):

    def __init__(self, url):
        """
        :param url: 调用url, 需要传入授权方的api调用地址
        """
        self.url = url
        self.accessKey = ""
        self.accessSecret = ""
        self.api = ""
        self.debug = False

    def setAccessKey(self, accessKey):
        """
        指定api授权元素的accessKey
        :param accessKey:
        :return:
        """
        self.accessKey = accessKey

    def setAccessSecret(self, accessSecret):
        """
        指定api授权元素的accessSecret
        :param accessSecret:
        :return:
        """
        self.accessSecret = accessSecret

    def setApi(self, api):
        """
        指定需要调用的api，格式为{服务元素fullName}.{函数}，例如 services.MySvc.func1
        :param api:
        :return:
        """
        self.api = api

    def buildUrl(self):
        """
        构造完整的请求链接
        :return:
        """
        apiPath = self.api.split(".")
        url = f"{self.url}/{'/'.join(apiPath)}"
        return url

    def openDebug(self):
        """
        开启调试模式
        :return:
        """
        self.debug = True
