# -*- coding: utf-8 -*-
import requests
import logging
import json
import os
# To enable the initializer feature (https://help.aliyun.com/document_detail/2513452.html)
# please implement the initializer function as below：
# def initializer(context):
#   logger = logging.getLogger()
#   logger.info('initializing')

def handler(event, context):
    logger = logging.getLogger()
    heimdallr_URL = os.getenv('heimdallr_URL')
    heimdallr_TOKEN = os.getenv('heimdallr_TOKEN')   
    heimdallr_GROUP_KEY = os.getenv('heimdallr_GROUP_KEY')
 
    evt = json.loads(event)
    body =evt.get("body")
    if body is None:
        logger.error('body is None')
        return {
            'statusCode': 400,
            'body': 'body is None'
        }  
    else:
        body = json.loads(body)
        id = body.get("id")
        url = body.get("url")
        value = body.get("value")
        html = body.get("html")
        link = body.get("link")
        data = body.get("data")

    title = f'监测任务ID: {id}, 状态：{data}'
    msg_type = 'text'
    # content = f'>**监控值** <font color=\"info\">{value}</font>  \n> [详情链接]({link})  *** {html}'
    # markdown = {"content": content}
    text = {"content": f'{title}  \n 监控值: {value}  \n <a href="{link}">详情链接</a>  \n {html}'
    }

    payload = {
        "key": heimdallr_GROUP_KEY,
        "title": title,
        "msg_type": msg_type,
        "text": text,
        "enable_duplicate_check": 1,
        "duplicate_check_interval": 1800
    }
    logger.info(f'payload = {payload}')

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {heimdallr_TOKEN}"
    }
    logger.info(f'headers: {headers}')

    response = requests.post(heimdallr_URL, json=payload, headers=headers, timeout=120)
    logger.info(f'Heimdallr response status code: {response.status_code}')
    logger.info(f'Heimdallr response body: {response.json()}')
    return {
        'statusCode': 200,
        'body': response.json()
    }
