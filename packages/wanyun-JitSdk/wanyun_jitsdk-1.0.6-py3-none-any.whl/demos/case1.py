# -*-coding:utf-8-*-
"""
Created on 2024/11/13

@author: 臧韬

@desc: 默认描述
"""

from wanyun_JitSdk import JitApi
from wanyun_JitSdk import JitApiRequest
from wanyun_JitSdk import JitApiResponse

"""
调用url: http://demoain/api/orgId/appName
accessKey: xxxx
accessSecret: xxxxxxxxxxxxxxxx
"""
authApi = JitApi("http://demoain/api/orgId/appName")
authApi.setAccessKey("xxxx")
authApi.setAccessSecret("xxxxxxxxxxxxxxxx")
authApi.setApi("services.MySvc.func1")

req = JitApiRequest()
req.setMethod("POST")
req.setParams({})
resp = req.execute(authApi)
print(resp.data)

