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
    logger.info(f'heimdallr_URL = {heimdallr_URL}')
    heimdallr_TOKEN = os.getenv('heimdallr_TOKEN')   
    heimdallr_GROUP_KEY = os.getenv('heimdallr_GROUP_KEY')

    evt = json.loads(event)
    logger.info(f'evt = {evt}')
    body =evt.get("body")
    logger.info(f'body = {body}')
    if body is None:
        logger.error('body is None')
        return {
            'statusCode': 400,
            'body': 'body is None'
        }  
    else:
        body = json.loads(body)
        id = body.get("id")
        logger.info(f'id = {id}')
        url = body.get("url")
        logger.info(f'url = {url}')
        value = body.get("value")
        logger.info(f'value = {value}')
        html = body.get("html")
        logger.info(f'html = {html}')
        link = body.get("link")
        logger.info(f'link = {link}')
        data = body.get("data")
        logger.info(f'data = {data}')

    title = f'监测任务ID: {id}, 状态：{data}'
    logger.info(f'title = {title}')
    msg_type = 'markdown'
    content = f'>**监控值** <font color=\"info\">{value}</font>  \n> [详情链接]({link})  *** {html}'
    markdown = {"content": content}
    logger.info(f'markdown = {markdown}')


    payload = {
        "key": heimdallr_GROUP_KEY,
        "title": title,
        "msg_type": msg_type,
        "markdown": markdown
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {heimdallr_TOKEN}"
    }

    response = requests.post(heimdallr_URL, json=payload, headers=headers, timeout=120)
    logger.info(f'Heimdallr response status code: {response.status_code}')
    logger.info(f'Heimdallr response body: {response.json()}')
    return {
        'statusCode': 200,
        'body': response.json()
    }
