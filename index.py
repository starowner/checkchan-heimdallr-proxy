# -*- coding: utf-8 -*-
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
    logger.info(f'heimdallr_TOKEN = {heimdallr_TOKEN}')

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


    return {
        'statusCode': 200,
        'body': f'body = {body}, heimdallr_URL = {heimdallr_URL}, heimdallr_TOKEN = {heimdallr_TOKEN}'
    }
