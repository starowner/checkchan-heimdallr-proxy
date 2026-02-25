# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import base64
import io
import re
import requests
import logging
import json
import os
# To enable the initializer feature (https://help.aliyun.com/document_detail/2513452.html)
# please implement the initializer function as below：
# def initializer(context):
#   logger = logging.getLogger()
#   logger.info('initializing')

FONT_PATH = os.path.join(os.path.dirname(__file__), "NotoSansCJK-Regular.ttc")


def html_to_image_file_then_base64(html_content, font_size=24):
    """
    流程模拟：
    1. HTML -> 内存图片对象
    2. 图片对象 -> 保存到内存文件对象 (模拟写文件)
    3. 内存文件对象 -> 读取二进制数据 (模拟读文件)
    4. 二进制数据 -> Base64
    
    全程无物理磁盘 IO。
    """
    
    # --- 步骤 0: 预处理文本 (去除标签) ---
    text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines: lines = ["(无内容)"]

    # --- 步骤 1: 加载字体 (必须指定本地字体以避免 FC 编码错误) ---
    if not os.path.exists(FONT_PATH):
        raise FileNotFoundError(f"错误：未找到字体文件 {FONT_PATH}。请在 FC 控制台上传 font.ttf 到代码根目录。")
    
    font = ImageFont.truetype(FONT_PATH, font_size)

    # --- 步骤 2: 计算布局与绘制 (内存中创建图片对象) ---
    temp_img = Image.new('RGB', (1, 1))
    draw_temp = ImageDraw.Draw(temp_img)
    
    # 简单换行处理
    final_lines = []
    width_limit = 800
    for line in lines:
        current_line = line
        while True:
            bbox = draw_temp.textbbox((0, 0), current_line, font=font)
            if (bbox[2] - bbox[0]) <= width_limit:
                final_lines.append(current_line)
                break
            # 强制截断
            split_idx = max(1, len(current_line) // 2)
            # 优化截断点：尝试找到最接近宽度的位置
            low, high = 1, len(current_line)
            best = 1
            while low <= high:
                mid = (low + high) // 2
                sub_bbox = draw_temp.textbbox((0, 0), current_line[:mid], font=font)
                if (sub_bbox[2] - sub_bbox[0]) <= width_limit:
                    best = mid
                    low = mid + 1
                else:
                    high = mid - 1
            final_lines.append(current_line[:best])
            current_line = current_line[best:]
            if not current_line: break

    # 计算尺寸
    line_height = int(font_size * 1.5)
    padding = 20
    img_w = width_limit + (padding * 2)
    img_h = len(final_lines) * line_height + (padding * 2)
    
    # 绘制
    img = Image.new('RGB', (img_w, img_h), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    y = padding
    for line in final_lines:
        draw.text((padding, y), line, font=font, fill=(0, 0, 0))
        y += line_height

    # --- 步骤 3: 模拟“保存为文件” (写入内存缓冲区) ---
    # 创建一个 BytesIO 对象，它在内存中表现得像一个打开的文件
    memory_file = io.BytesIO()
    
    # 将图片“保存”到这个内存文件中 (格式 PNG)
    img.save(memory_file, format='PNG')
    
    # 【关键】模拟文件读写切换：将指针移回文件开头
    # 就像你写完文件后，如果要读它，必须先 close 再 open，或者 seek(0)
    memory_file.seek(0)
    
    # --- 步骤 4: 模拟“读取文件内容” ---
    # 从内存文件中读取所有二进制数据
    image_bytes = memory_file.read()
    
    # 此时 memory_file 可以被关闭或丢弃，我们拿到了纯二进制数据
    del memory_file

    # --- 步骤 5: 转为 Base64 ---
    base64_str = base64.b64encode(image_bytes).decode('utf-8')
    
    # return f"data:image/png;base64,{base64_str}"
    return base64_str



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
        attach = html_to_base64_image(html)

    title = f'监测任务ID: {id}, 状态：{data}'
    msg_type = 'text'
    # text = f'>**监控值** \n \n ><font color=\"info\">{value}</font>  \n\n >[详情链接]({link})  \n *** \n {html}'
    # markdown = {"content": content}
    text = f'监控值:\n\n{value}\n\n<a href="{link}">详情链接</a>\n\n{html}'

    payload = {
        "key": heimdallr_GROUP_KEY,
        "title": title,
        "msg_type": msg_type,
        "body": text,
        "attach": attach
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
