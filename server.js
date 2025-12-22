const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;
const DATA_FILE = path.join(__dirname, 'data.json');

// 确保 data.json 存在
if (!fs.existsSync(DATA_FILE)) {
    fs.writeFileSync(DATA_FILE, '[]', 'utf8');
}

// MIME 类型映射
const MIME_TYPES = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon'
};

// 读取请求体
function readBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            try {
                resolve(body ? JSON.parse(body) : null);
            } catch (e) {
                reject(e);
            }
        });
        req.on('error', reject);
    });
}

// 发送 JSON 响应
function sendJSON(res, data, status = 200) {
    res.writeHead(status, {
        'Content-Type': 'application/json; charset=utf-8',
        'Access-Control-Allow-Origin': '*'
    });
    res.end(JSON.stringify(data));
}

// 发送静态文件
function sendFile(res, filePath) {
    const ext = path.extname(filePath);
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';
    
    fs.readFile(filePath, (err, data) => {
        if (err) {
            res.writeHead(404);
            res.end('File not found');
            return;
        }
        res.writeHead(200, { 'Content-Type': contentType });
        res.end(data);
    });
}

// 读取数据
function readData() {
    try {
        const data = fs.readFileSync(DATA_FILE, 'utf8');
        return JSON.parse(data);
    } catch (e) {
        return [];
    }
}

// 写入数据
function writeData(data) {
    fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2), 'utf8');
}

// 创建服务器
const server = http.createServer(async (req, res) => {
    const url = new URL(req.url, `http://localhost:${PORT}`);
    const pathname = url.pathname;

    // CORS 预检请求
    if (req.method === 'OPTIONS') {
        res.writeHead(200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        });
        res.end();
        return;
    }

    // API 路由
    if (pathname === '/api/plans') {
        try {
            if (req.method === 'GET') {
                // 获取所有计划
                const plans = readData();
                sendJSON(res, plans);
            } else if (req.method === 'POST') {
                // 添加新计划
                const body = await readBody(req);
                const plans = readData();
                body.id = Date.now().toString() + Math.random().toString(36).substr(2, 9);
                body.completed = false;
                plans.push(body);
                writeData(plans);
                sendJSON(res, body, 201);
                console.log(`✅ 添加计划: ${body.title}`);
            } else if (req.method === 'PUT') {
                // 批量更新（导入）
                const body = await readBody(req);
                if (Array.isArray(body)) {
                    writeData(body);
                    sendJSON(res, { success: true, count: body.length });
                    console.log(`📥 导入 ${body.length} 条计划`);
                } else {
                    sendJSON(res, { error: '无效的数据格式' }, 400);
                }
            }
        } catch (e) {
            sendJSON(res, { error: e.message }, 500);
        }
        return;
    }

    if (pathname.startsWith('/api/plans/')) {
        const id = pathname.split('/')[3];
        try {
            if (req.method === 'PUT') {
                // 更新计划
                const body = await readBody(req);
                let plans = readData();
                const index = plans.findIndex(p => p.id === id);
                if (index !== -1) {
                    plans[index] = { ...plans[index], ...body };
                    writeData(plans);
                    sendJSON(res, plans[index]);
                    console.log(`✏️ 更新计划: ${plans[index].title}`);
                } else {
                    sendJSON(res, { error: '计划不存在' }, 404);
                }
            } else if (req.method === 'DELETE') {
                // 删除计划
                let plans = readData();
                const plan = plans.find(p => p.id === id);
                plans = plans.filter(p => p.id !== id);
                writeData(plans);
                sendJSON(res, { success: true });
                console.log(`🗑️ 删除计划: ${plan?.title || id}`);
            } else if (req.method === 'PATCH') {
                // 切换完成状态
                let plans = readData();
                const index = plans.findIndex(p => p.id === id);
                if (index !== -1) {
                    plans[index].completed = !plans[index].completed;
                    writeData(plans);
                    sendJSON(res, plans[index]);
                    console.log(`${plans[index].completed ? '✅' : '⏳'} ${plans[index].title}`);
                } else {
                    sendJSON(res, { error: '计划不存在' }, 404);
                }
            }
        } catch (e) {
            sendJSON(res, { error: e.message }, 500);
        }
        return;
    }

    // 静态文件服务
    let filePath = pathname === '/' ? '/index.html' : pathname;
    filePath = path.join(__dirname, filePath);
    
    // 安全检查：确保在项目目录内
    if (!filePath.startsWith(__dirname)) {
        res.writeHead(403);
        res.end('Forbidden');
        return;
    }

    sendFile(res, filePath);
});

server.listen(PORT, () => {
    console.log(`
╔═══════════════════════════════════════════════════╗
║                                                   ║
║   📆 月度计划看板服务器已启动                      ║
║                                                   ║
║   🌐 访问地址: http://localhost:${PORT}             ║
║   📁 数据文件: data.json                          ║
║                                                   ║
║   按 Ctrl+C 停止服务器                            ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
`);
});

