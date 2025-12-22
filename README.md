# 📆 月度计划看板

一个简洁美观的个人月度计划管理工具，支持本地数据存储。

![preview](https://img.shields.io/badge/status-active-success.svg)
![license](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ 功能特性

- 📋 **计划管理**：添加、编辑、删除计划
- ✅ **完成状态**：点击复选框标记完成
- 🔍 **筛选功能**：按月份、周、类型、状态筛选
- 📊 **统计面板**：总计划、完成率、各类型数量
- 💾 **本地存储**：数据保存在 `data.json` 文件中
- 📥 **导入导出**：支持 JSON 格式备份/恢复
- 🎨 **深色主题**：现代化 UI 设计
- 📱 **响应式**：支持手机、平板、电脑

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/你的用户名/schedule-planner.git
cd schedule-planner
```

### 2. 启动服务器

**方式一：Python（推荐，无需安装依赖）**

```bash
python3 server.py
```

**方式二：Node.js**

```bash
node server.js
```

### 3. 访问应用

打开浏览器访问：http://localhost:3000

## 📁 项目结构

```
schedule/
├── index.html      # 主页面
├── server.py       # Python 服务器
├── server.js       # Node.js 服务器（备选）
├── data.json       # 数据存储文件
├── package.json    # Node.js 配置
├── CHANGELOG.md    # 更新日志
├── README.md       # 项目说明
└── example.xlsx    # 原始 Excel 数据
```

## 🎯 计划类型

| 类型 | 说明 |
|------|------|
| 📚 学习输入 | 英语、读书、技能学习等 |
| 🏃‍♀️ 运动锻炼 | 跑步、健身、运动等 |
| 🎵 兴趣爱好 | 音乐、绘画、其他爱好 |
| 🌲 目标设定 | 年度/月度目标 |

## 📝 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/plans` | 获取所有计划 |
| POST | `/api/plans` | 添加新计划 |
| PUT | `/api/plans` | 批量导入 |
| PUT | `/api/plans/:id` | 更新计划 |
| PATCH | `/api/plans/:id` | 切换完成状态 |
| DELETE | `/api/plans/:id` | 删除计划 |

## 🛠️ 技术栈

- **前端**：HTML5 + CSS3 + JavaScript (原生)
- **后端**：Python / Node.js (可选)
- **存储**：JSON 文件
- **字体**：Noto Sans SC

## 📄 License

MIT License

