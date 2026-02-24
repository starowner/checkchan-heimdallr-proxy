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
    return os.environ.get('heimdallr_URL')
