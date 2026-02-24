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
    evt = json.loads(event)
    logger = logging.getLogger()
    logger.info('hello world')

    heimdallr_URL = os.getenv('heimdallr_URL')
    heimdallr_TOKEN = os.getenv('heimdallr_TOKEN')   
    return {
        'statusCode': 200,
        'body': f'heimdallr_URL = {heimdallr_URL}, heimdallr_TOKEN = {heimdallr_TOKEN}'
    }
