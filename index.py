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

def html_to_base64_image(
    html_content, 
    font_size=24, 
    font_color=(0, 0, 0), 
    bg_color=(255, 255, 255), 
    padding=20,
    line_height_ratio=1.5,
    width_limit=800
):
    """
    利用现有的 Pillow 库将 HTML 文本转换为 Base64 图片。
    注意：此方法会去除 HTML 标签，仅渲染纯文本内容。
    """
    
    # 1. 清洗 HTML 标签，提取纯文本
    # 移除 script 和 style 内容
    text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # 移除所有其他标签
    text = re.sub(r'<[^>]+>', '', text)
    # 还原常用实体字符
    text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    # 清理多余的空行
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    if not lines:
        lines = ["(无内容)"]

    # 2. 【核心修复】加载字体
    # 检查字体文件是否存在
    if not os.path.exists(FONT_PATH):
        raise FileNotFoundError(f"字体文件未找到: {FONT_PATH}。请确保已将 .ttf 字体文件上传到函数代码根目录。")
    
    try:
        # 强制使用上传的字体文件
        font = ImageFont.truetype(FONT_PATH, font_size)
    except Exception as e:
        raise RuntimeError(f"字体加载失败: {e}。请检查字体文件是否损坏或格式不支持。")

    # 3. 计算每行文本的换行与尺寸
    # 由于 Pillow 不自动换行，我们需要手动根据 width_limit 进行折行
    final_lines = []
    
    temp_img = Image.new('RGB', (1, 1))
    draw_temp = ImageDraw.Draw(temp_img)
    
    for line in lines:
        # 如果单行超过宽度限制，则手动截断换行
        current_line = line
        while True:
            bbox = draw_temp.textbbox((0, 0), current_line, font=font)
            width = bbox[2] - bbox[0]
            
            if width <= width_limit:
                final_lines.append(current_line)
                break
            else:
                # 简单的按字符截断 (更复杂的需要按单词截断)
                # 这里采用二分法或逐步减少字符来寻找最佳截断点
                low, high = 1, len(current_line)
                best_split = 1
                while low <= high:
                    mid = (low + high) // 2
                    sub_text = current_line[:mid]
                    bbox_sub = draw_temp.textbbox((0, 0), sub_text, font=font)
                    if (bbox_sub[2] - bbox_sub[0]) <= width_limit:
                        best_split = mid
                        low = mid + 1
                    else:
                        high = mid - 1
                
                # 防止死循环，至少切一个字符
                if best_split == 0: best_split = 1
                
                final_lines.append(current_line[:best_split])
                current_line = current_line[best_split:]
                
                if not current_line:
                    break

    # 4. 计算图片总高度
    line_height = int(font_size * line_height_ratio)
    total_height = len(final_lines) * line_height
    max_width = width_limit # 使用设定的最大宽度，或者可以动态计算最大行的宽度
    
    img_width = max_width + (padding * 2)
    img_height = total_height + (padding * 2)

    # 5. 创建图片并绘制
    img = Image.new('RGB', (img_width, img_height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    current_y = padding
    for line in final_lines:
        draw.text((padding, current_y), line, font=font, fill=font_color)
        current_y += line_height

    # 6. 转为 Base64 (内存操作)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG", optimize=True)
    img_bytes = buffered.getvalue()
    
    base64_str = base64.b64encode(img_bytes).decode('utf-8')
    
    return f"data:image/png;base64,{base64_str}"
    # return base64_str



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
