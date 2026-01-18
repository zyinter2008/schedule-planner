#!/usr/bin/env python3
"""
月度计划看板 - 本地服务器
使用方法: python3 server.py
访问地址: http://localhost:3000
"""

import http.server
import json
import os
from urllib.parse import urlparse
import random
import string
import time

PORT = 3000
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')
GOALS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'goals.json')

# 确保 data.json 存在
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

# 确保 goals.json 存在，初始化默认目标
if not os.path.exists(GOALS_FILE):
    default_goals = {
        "2025": {
            "learning": "web3(每周2h)、英语(每周0.5h*2)、读书(每周3h)、写作一篇(1h)",
            "exercise": "每周运动 0.5h * 2 次",
            "hobby": "每周练习2h，录歌一首"
        }
    }
    with open(GOALS_FILE, 'w', encoding='utf-8') as f:
        json.dump(default_goals, f, ensure_ascii=False, indent=2)

def read_data():
    """读取数据文件"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def write_data(data):
    """写入数据文件"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def read_goals():
    """读取年度目标"""
    try:
        with open(GOALS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def write_goals(goals):
    """写入年度目标"""
    with open(GOALS_FILE, 'w', encoding='utf-8') as f:
        json.dump(goals, f, ensure_ascii=False, indent=2)

def generate_id():
    """生成唯一ID"""
    return str(int(time.time() * 1000)) + ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)
    
    def send_json(self, data, status=200):
        """发送 JSON 响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def read_body(self):
        """读取请求体"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length:
            body = self.rfile.read(content_length).decode('utf-8')
            return json.loads(body)
        return None
    
    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """处理 GET 请求"""
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/plans':
            # 获取所有计划
            plans = read_data()
            self.send_json(plans)
        elif parsed.path == '/api/goals':
            # 获取年度目标
            goals = read_goals()
            self.send_json(goals)
        else:
            # 静态文件服务
            super().do_GET()
    
    def do_POST(self):
        """处理 POST 请求"""
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/plans':
            # 添加新计划
            body = self.read_body()
            if body:
                plans = read_data()
                body['id'] = generate_id()
                body['completed'] = False
                plans.append(body)
                write_data(plans)
                self.send_json(body, 201)
                print(f"✅ 添加计划: {body.get('title', '')}")
            else:
                self.send_json({'error': '无效的请求数据'}, 400)
        else:
            self.send_json({'error': '未找到路由'}, 404)
    
    def do_PUT(self):
        """处理 PUT 请求"""
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/plans':
            # 批量导入
            body = self.read_body()
            if isinstance(body, list):
                write_data(body)
                self.send_json({'success': True, 'count': len(body)})
                print(f"📥 导入 {len(body)} 条计划")
            else:
                self.send_json({'error': '无效的数据格式'}, 400)
        elif parsed.path.startswith('/api/goals/'):
            # 更新某一年的目标
            year = parsed.path.split('/')[-1]
            body = self.read_body()
            if body:
                goals = read_goals()
                goals[year] = body
                write_goals(goals)
                self.send_json({'success': True, 'year': year})
                print(f"🎯 更新 {year} 年度目标")
            else:
                self.send_json({'error': '无效的请求数据'}, 400)
        elif parsed.path.startswith('/api/plans/'):
            # 更新单个计划
            plan_id = parsed.path.split('/')[-1]
            body = self.read_body()
            if body:
                plans = read_data()
                for i, plan in enumerate(plans):
                    if plan['id'] == plan_id:
                        plans[i] = {**plan, **body}
                        write_data(plans)
                        self.send_json(plans[i])
                        print(f"✏️ 更新计划: {plans[i].get('title', '')}")
                        return
                self.send_json({'error': '计划不存在'}, 404)
            else:
                self.send_json({'error': '无效的请求数据'}, 400)
        else:
            self.send_json({'error': '未找到路由'}, 404)
    
    def do_PATCH(self):
        """处理 PATCH 请求 - 切换完成状态"""
        parsed = urlparse(self.path)
        
        if parsed.path.startswith('/api/plans/'):
            plan_id = parsed.path.split('/')[-1]
            plans = read_data()
            for i, plan in enumerate(plans):
                if plan['id'] == plan_id:
                    plans[i]['completed'] = not plans[i].get('completed', False)
                    write_data(plans)
                    self.send_json(plans[i])
                    status = '✅' if plans[i]['completed'] else '⏳'
                    print(f"{status} {plans[i].get('title', '')}")
                    return
            self.send_json({'error': '计划不存在'}, 404)
        else:
            self.send_json({'error': '未找到路由'}, 404)
    
    def do_DELETE(self):
        """处理 DELETE 请求"""
        parsed = urlparse(self.path)
        
        if parsed.path.startswith('/api/plans/'):
            plan_id = parsed.path.split('/')[-1]
            plans = read_data()
            for i, plan in enumerate(plans):
                if plan['id'] == plan_id:
                    deleted = plans.pop(i)
                    write_data(plans)
                    self.send_json({'success': True})
                    print(f"🗑️ 删除计划: {deleted.get('title', '')}")
                    return
            self.send_json({'error': '计划不存在'}, 404)
        else:
            self.send_json({'error': '未找到路由'}, 404)
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        try:
            if args and isinstance(args[0], str) and '/api/' in args[0]:
                return  # API 请求单独处理日志
        except:
            pass
        # 静默其他日志
        pass

def main():
    print(f"""
╔═══════════════════════════════════════════════════╗
║                                                   ║
║   📆 月度计划看板服务器已启动                      ║
║                                                   ║
║   🌐 访问地址: http://localhost:{PORT}             ║
║   📁 数据文件: data.json                          ║
║                                                   ║
║   按 Ctrl+C 停止服务器                            ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
""")
    
    with http.server.HTTPServer(('', PORT), RequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 服务器已停止")

if __name__ == '__main__':
    main()

