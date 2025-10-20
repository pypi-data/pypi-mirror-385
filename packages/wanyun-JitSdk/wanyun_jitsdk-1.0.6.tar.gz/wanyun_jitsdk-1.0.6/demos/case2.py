# -*-coding:utf-8-*-
"""
Created on 2024/11/16

@author: 臧韬

@desc: 默认描述
"""

from wanyun_JitSdk import JitApi
from wanyun_JitSdk import JitApiRequest
from wanyun_JitSdk import JitApiResponse

#
authApi = JitApi("https://jit-dev.wanyunapp.com/api/whwy/b")  # 授权方的api访问地址
authApi.setAccessKey("12345678")  # api授权元素配置的accessKey
authApi.setAccessSecret("44eb2b0bf8db45baa37f489017ca942eefe9e9")  # api授权元素配置的accessSecret
authApi.setApi("services.iThinkItsIiui.itsABigThing")  # 需要调用的api
req = JitApiRequest()
req.setMethod("POST")  # 接口请求方式，默认为POST
req.setParams({'singleLine': 'xxx', 'line2': 'xxx'})  # 接口参数
resp = req.execute(authApi)
print(resp.data)

authApi = JitApi("http://127.0.0.1:6001/api/whwy/ZTTest21")  # 授权方的api访问地址
authApi.setAccessKey("testtest")  # api授权元素配置的accessKey
authApi.setAccessSecret("32fca7ea52834355be0f978c9bf067eed05606")  # api授权元素配置的accessSecret
authApi.setApi("services.svc2.func2")  # 需要调用的api
authApi.openDebug()

req = JitApiRequest()
req.setMethod("POST")  # 接口请求方式，默认为POST
req.setParams({
    "singleLine": "ttt",
    "line2": "ttt"
})  # 接口参数
resp = req.execute(authApi)
print(resp.data)
