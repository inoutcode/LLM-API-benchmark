# 快速开发指南

## 🚀 5 分钟快速开始

### 1. 准备环境

```bash
# 克隆项目（或下载源码）
git clone <your-repo-url>
cd api_perf

# 安装后端依赖
pip install -r requirements.txt

# 安装前端依赖
cd frontend && npm install && cd ..
```

### 2. 配置数据库

```bash
# 创建 MySQL 数据库
mysql -u root -p
CREATE DATABASE model_test_db CHARACTER SET utf8mb4;

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入数据库密码
```

### 3. 初始化和启动

```bash
# 初始化数据库
make init-db

# 构建前端
make build

# 启动应用
make run
```

访问 http://localhost:5000，使用 admin/admin123 登录。

## 📁 项目结构速览

```
api_perf/
├── backend/              # 后端代码
│   ├── models.py        # 数据库模型
│   ├── config.py        # 配置
│   ├── routes/          # API 路由
│   └── executor/        # 任务执行器
├── frontend/            # 前端代码
│   └── src/
│       ├── views/       # 页面组件
│       └── utils/       # 工具函数
├── run.py               # 启动脚本
└── Makefile             # 常用命令
```

## 🔧 常用命令

```bash
# 安装依赖
make install

# 初始化数据库
make init-db

# 启动应用
make run

# 开发模式（前后端分离）
make dev

# 构建前端
make build

# 清理临时文件
make clean
```

## 🎯 核心功能

### 1. 创建任务

**压力测试任务**：
- API URL: `https://api.example.com`
- API Key: `sk-xxxx`
- Model: `gpt-3.5-turbo`
- 并发数: 8
- 请求数: 50

**质量测试任务**：
- API URL: `https://relay.example.com/v1`
- API Key: `sk-xxxx`
- Audit 路径: `/path/to/audit.py`

### 2. 调度设置

- **手动执行**：点击"执行"按钮
- **Cron 表达式**：`0 */30 * * * *`（每 30 分钟）
- **固定间隔**：1800 秒（30 分钟）

### 3. 查看结果

- **仪表盘**：统计概览
- **压力测试结果**：图表 + 详细列表
- **质量测试结果**：风险摘要表格

## 🛠️ 开发指南

### 添加新的 API

1. 在 `backend/routes/` 创建路由文件
2. 在 `backend/__init__.py` 注册蓝图
3. 在 `frontend/src/utils/api.js` 添加 API 调用

### 添加新的页面

1. 在 `frontend/src/views/` 创建 Vue 组件
2. 在 `frontend/src/router/index.js` 添加路由
3. 在 `Layout.vue` 添加菜单项

### 修改数据库模型

1. 编辑 `backend/models.py`
2. 运行 `make init-db`（开发环境）
3. 生产环境使用数据库迁移工具

## 🐛 调试技巧

### 后端调试

```python
# 在代码中添加日志
import logging
logger = logging.getLogger(__name__)
logger.info("Debug message")
```

查看日志：`tail -f logs/app.log`

### 前端调试

使用 Vue DevTools 浏览器扩展。

### 数据库调试

```bash
# 连接数据库
mysql -u root -p model_test_db

# 查看任务
SELECT * FROM tasks;

# 查看结果
SELECT * FROM perf_test_results ORDER BY execution_time DESC LIMIT 10;
```

## 📝 代码规范

### Python

- 使用 4 空格缩进
- 遵循 PEP 8 规范
- 使用类型注解（可选）

### JavaScript

- 使用 2 空格缩进
- 使用 Composition API
- 组件命名：PascalCase

## 🔐 安全注意事项

1. **生产环境必须修改**：
   - `SECRET_KEY`
   - 初始管理员密码
   - MySQL 密码

2. **不要提交**：
   - `.env` 文件
   - `data/outputs/` 目录
   - API Keys

3. **定期备份**：
   - 数据库
   - 配置文件

## 📚 相关文档

- [Flask 文档](https://flask.palletsprojects.com/)
- [Vue 3 文档](https://vuejs.org/)
- [Element Plus 文档](https://element-plus.org/)
- [ECharts 文档](https://echarts.apache.org/)
- [evalscope 文档](https://github.com/modelscope/evalscope)

## ❓ 常见问题

### Q: 如何修改端口？

A: 编辑 `.env` 文件，添加 `PORT=8000`

### Q: 如何添加新的任务类型？

A: 参考 `ARCHITECTURE_NEW.md` 第 7.1 节

### Q: 如何备份数据？

A: 使用 `mysqldump` 备份数据库：
```bash
mysqldump -u root -p model_test_db > backup.sql
```

### Q: 前端构建失败？

A: 检查 Node.js 版本（需要 >= 16）：
```bash
node --version
```

## 🤝 获取帮助

- 查看日志：`logs/app.log`
- 提交 Issue：GitHub Issues
- 查看文档：`README_NEW.md` 和 `ARCHITECTURE_NEW.md`