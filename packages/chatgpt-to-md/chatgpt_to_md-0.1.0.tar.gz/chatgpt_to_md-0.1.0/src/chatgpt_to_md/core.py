import json
import zipfile
import os
from datetime import datetime
import re

def convert(zip_path, output_dir="./chatgpt_output"):
    """
    将ChatGPT导出的zip文件转换为Markdown
    
    Args:
        zip_path: ChatGPT导出的zip文件路径
        output_dir: 输出目录，默认为当前目录下的chatgpt_output
    """
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 解压zip文件
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        
        # 查找conversations.json
        json_path = _find_conversations_json(output_dir)
        if not json_path:
            print("错误: 在zip文件中找不到 conversations.json")
            return
        
        # 读取并解析JSON数据
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 转换每个对话
        successful = 0
        for conversation in data:
            try:
                _convert_single(conversation, output_dir)
                successful += 1
            except Exception as e:
                print(f"转换对话时出错: {e}")
                continue
        
        print(f"成功转换 {successful} 个对话")
        
    except Exception as e:
        print(f"处理过程中出错: {e}")

def _find_conversations_json(directory):
    """递归查找conversations.json文件"""
    for root, dirs, files in os.walk(directory):
        if 'conversations.json' in files:
            return os.path.join(root, 'conversations.json')
    return None

def _convert_single(conversation, output_dir):
    """转换单个对话为Markdown"""
    title = conversation.get('title', '未命名对话')
    create_time = conversation.get('create_time')
    
    # 生成安全文件名
    safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
    if create_time:
        dt = datetime.fromtimestamp(create_time)
        filename = f"{dt.strftime('%Y-%m-%d')}_{safe_title}.md"
    else:
        filename = f"{safe_title}.md"
    
    filepath = os.path.join(output_dir, filename)
    
    # 构建Markdown内容
    md_content = []
    
    # YAML front matter
    md_content.append("---")
    md_content.append(f"title: {title}")
    if create_time:
        dt = datetime.fromtimestamp(create_time)
        md_content.append(f"date: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
    md_content.append("source: ChatGPT Export")
    md_content.append("---\n")
    
    md_content.append(f"# {title}\n")
    
    # 提取并排序消息
    messages = []
    for key, value in conversation.get('mapping', {}).items():
        if value and 'message' in value and value['message']:
            msg = value['message']
            if msg.get('content') and msg.get('author'):
                content_parts = msg['content'].get('parts', [''])
                content = ''.join(content_parts) if content_parts else ''
                
                if content.strip():
                    timestamp = msg.get('create_time') or 0
                    messages.append({
                        'timestamp': timestamp,
                        'role': msg['author']['role'],
                        'content': content.strip()
                    })
    
    # 按时间排序并转换
    messages.sort(key=lambda x: x['timestamp'])
    for msg in messages:
        role_display = {
            'user': '我',
            'assistant': 'ChatGPT', 
            'system': '系统',
            'tool': '工具'
        }.get(msg['role'], msg['role'])
        
        md_content.append(f"## {role_display}")
        md_content.append("")
        md_content.append(msg['content'])
        md_content.append("")
    
    # 写入文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_content))
    
    print(f"已创建: {filename}")

def main():
    """命令行入口点"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='将ChatGPT导出的zip文件转换为Markdown')
    parser.add_argument('zip_file', help='ChatGPT导出的zip文件路径')
    parser.add_argument('-o', '--output', default='./chatgpt_output', 
                       help='输出目录 (默认: ./chatgpt_output)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.zip_file):
        print(f"错误: 文件 '{args.zip_file}' 不存在")
        sys.exit(1)
    
    convert(args.zip_file, args.output)
    print("转换完成！")