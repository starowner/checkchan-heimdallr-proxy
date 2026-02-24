# -*- coding: utf-8 -*-
import logging
import json
import os
# To enable the initializer feature (https://help.aliyun.com/document_detail/2513452.html)
# please implement the initializer function as below：
# def initializer(context):
#   logger = logging.getLogger()
#   logger.info('initializing')
event_example = {
    "version": "v1",
    "rawPath": "/",
    "headers": {
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "no-cache",
        "X-Forwarded-Proto": "https",
        "Content-Type": "application/json",
        "Content-Length": "246",
        "Accept": "*/*",
        "Connection": "keep-alive",
        "User-Agent": "PostmanRuntime/7.51.1",
        "Postman-Token": "a1b298a9-353f-4534-88ab-f8c3980ad499",
        "Host": "checkchlr-proxy-ggsguhdmtj.cn-shanghai.fcapp.run,checkchlr-proxy-ggsguhdmtj.cn-shanghai.fcapp.run"
    },
    "queryParameters": {},
    "body": "{\r\n\"id\": \"监测任务id，用于识别结果属于哪个任务\",\r\n\"url\": \"原始监测URL，用于识别结果属于哪个任务\",\r\n\"value\": \"监测到的纯文本内容\",\r\n\"html\": \"监测到的HTML内容\",\r\n\"link\": \"监测内容对应的URL\"\r\n}",
    "isBase64Encoded": false,
    "requestContext": {
        "accountId": "1926626230927744",
        "domainName": "checkchlr-proxy-ggsguhdmtj.cn-shanghai.fcapp.run",
        "domainPrefix": "checkchlr-proxy-ggsguhdmtj",
        "requestId": "1-699d51ea-160a87-54c1b40505c9",
        "time": "2026-02-24T07:23:22.320752064+00:00",
        "timeEpoch": "1771917802320",
        "http": {
            "method": "POST",
            "path": "/",
            "protocol": "HTTP/1.1",
            "sourceIp": "222.71.68.3",
            "userAgent": "PostmanRuntime/7.51.1"
        }
    }
}

def handler(event, context):
    evt = json.loads(event)
    logger = logging.getLogger()
    logger.info('hello world')
    return os.environ.get('heimdallr_URL')
