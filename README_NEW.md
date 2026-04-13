# 模型质量测试管理后台

一个轻量级的开源管理后台，用于管理模型质量测试任务，支持服务压力测试和模型质量测试两种任务类型。

## 🎯 功能特性

- ✅ **用户认证**：账号密码登录，支持修改密码
- ✅ **任务管理**：可视化管理测试任务，支持创建、编辑、删除、启用/禁用
- ✅ **定时调度**：支持手动执行、Cron 表达式、固定间隔三种调度方式
- ✅ **服务压力测试**：基于 evalscope perf，自动解析性能指标
- ✅ **模型质量测试**：基于 audit.py，提取 Risk Summary 结构化数据
- ✅ **结果可视化**：
  - 压力测试：数值指标变化曲线（延迟、TTFT、RPS等）
  - 质量测试：表格形式呈现 11 项风险检测结果
- ✅ **原始文件保存**：按任务/执行时间命名，支持在线查看

## 🏗️ 技术架构

### 后端技术栈

- **Web 框架**：Flask 3.0（轻量级、易维护）
- **数据库**：MySQL（通过 SQLAlchemy ORM）
- **任务调度**：APScheduler（支持 Cron、Interval）
- **认证**：Flask-Login（Session 认证）

### 前端技术栈

- **框架**：Vue 3（Composition API）
- **UI 组件**：Element Plus（轻量级、美观）
- **图表**：ECharts（专业可视化）
- **构建工具**：Vite（快速开发）

### 目录结构

```
api_perf/
├── backend/               # 后端代码
│   ├── __init__.py       # Flask 应用初始化
│   ├── models.py         # 数据库模型
│   ├── config.py         # 配置文件
│   ├── routes/           # API 路由
│   │   ├── auth.py       # 认证路由
│   │   ├── tasks.py      # 任务管理路由
│   │   └── results.py    # 结果查询路由
│   └── executor/         # 任务执行器
│       └── __init__.py   # 执行逻辑
│
├── frontend/              # 前端代码
│   ├── src/
│   │   ├── main.js       # Vue 入口
│   │   ├── App.vue       # 根组件
│   │   ├── router/       # 路由配置
│   │   ├── utils/        # 工具函数
│   │   │   └── api.js    # API 请求封装
│   │   └── views/        # 页面组件
│   │       ├── Login.vue      # 登录页
│   │       ├── Layout.vue     # 布局组件
│   │       ├── Dashboard.vue  # 仪表盘
│   │       ├── Tasks.vue      # 任务管理
│   │       ├── PerfResults.vue    # 压力测试结果
│   │       └── QualityResults.vue # 质量测试结果
│   ├── index.html        # HTML 入口
│   ├── vite.config.js    # Vite 配置
│   └── package.json      # 前端依赖
│
├── data/                  # 数据存储
│   └ outputs/            # 测试输出文件
│
├── run.py                 # 启动脚本
├── requirements.txt       # Python 依赖
├── .env.example          # 环境变量模板
└ └── README.md           # 项目文档
```

## 📊 数据库设计

### 用户表 (users)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| username | VARCHAR(80) | 用户名（唯一） |
| password_hash | VARCHAR(255) | 密码哈希 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 任务表 (tasks)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| name | VARCHAR(200) | 任务名称 |
| task_type | VARCHAR(50) | 任务类型（perf_test/quality_test） |
| config | TEXT | 任务配置（JSON） |
| schedule_type | VARCHAR(20) | 调度类型（manual/cron/interval） |
| cron_expression | VARCHAR(100) | Cron 表达式 |
| interval_seconds | INT | 间隔秒数 |
| start_time | DATETIME | 开始时间 |
| end_time | DATETIME | 结束时间 |
| is_enabled | BOOLEAN | 是否启用 |
| status | VARCHAR(20) | 状态（idle/running/success/failed） |
| last_run_time | DATETIME | 最后执行时间 |
| next_run_time | DATETIME | 下次执行时间 |

### 服务压力测试结果表 (perf_test_results)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| task_id | INT | 任务 ID（外键） |
| execution_time | DATETIME | 执行时间 |
| concurrency | INT | 并发数 |
| avg_latency | FLOAT | 平均延迟 |
| p99_latency | FLOAT | P99 延迟 |
| avg_ttft | FLOAT | 平均首字延迟 |
| p99_ttft | FLOAT | P99 首字延迟 |
| avg_tpot | FLOAT | 平均每 token 时间 |
| p99_tpot | FLOAT | P99 每 token 时间 |
| rps | FLOAT | 每秒请求数 |
| gen_toks | FLOAT | 生成速度 |
| success_rate | FLOAT | 成功率 |
| output_file | VARCHAR(500) | 输出文件路径 |
| status | VARCHAR(20) | 状态 |

### 模型质量测试结果表 (quality_test_results)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| task_id | INT | 任务 ID（外键） |
| execution_time | DATETIME | 执行时间 |
| infrastructure_recon | VARCHAR(20) | 基础设施探测 |
| models_enumerated | VARCHAR(20) | 模型枚举 |
| token_injection | VARCHAR(20) | Token 注入 |
| extraction_attempts | VARCHAR(20) | 提取尝试 |
| cat_test | VARCHAR(20) | Cat 测试 |
| context_boundary | VARCHAR(100) | 上下文边界 |
| tool_call_substitution | VARCHAR(20) | 工具调用替换 |
| error_response_leakage | VARCHAR(20) | 错误响应泄漏 |
| stream_integrity | VARCHAR(20) | 流完整性 |
| overall_rating | VARCHAR(50) | 总体评级 |
| output_file | VARCHAR(500) | 输出文件路径 |
| status | VARCHAR(20) | 状态 |

## 🚀 快速开始

### 1. 环境准备

#### 后端环境

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装 evalscope（用于压力测试）
pip install evalscope

# 准备 audit.py（用于质量测试）
# 确保 audit.py 在可访问路径
```

#### 数据库准备

```bash
# 创建 MySQL 数据库
mysql -u root -p
CREATE DATABASE model_test_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 前端环境

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 开发模式构建
npm run dev

# 生产模式构建
npm run build
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
vim .env
```

配置示例：

```env
# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_DB=model_test_db

# Flask 配置
SECRET_KEY=your-secret-key
FLASK_ENV=development

# 初始管理员账号
INIT_ADMIN_USERNAME=admin
INIT_ADMIN_PASSWORD=admin123
```

### 3. 启动应用

```bash
# 启动后端服务
python run.py

# 或者使用 Flask 命令
flask run --host=0.0.0.0 --port=5000
```

访问：http://localhost:5000

默认账号：admin / admin123

## 📖 使用指南

### 1. 登录系统

使用初始管理员账号登录，登录后可在用户菜单修改密码。

### 2. 创建任务

#### 服务压力测试任务

1. 点击"新建任务"
2. 选择任务类型：服务压力测试
3. 配置参数：
   - API URL：中转站地址
   - API Key：访问密钥
   - 模型名称：测试模型
   - 并发数：并发请求数
   - 请求数：总请求数
4. 设置调度方式：
   - 手动执行：手动触发
   - Cron 表达式：定时执行（如 `0 */30 * * * *` 每 30 分钟）
   - 固定间隔：按固定间隔执行
5. 设置时间范围（可选）
6. 启用任务

#### 模型质量测试任务

1. 点击"新建任务"
2. 选择任务类型：模型质量测试
3. 配置参数：
   - API URL：中转站地址
   - API Key：访问密钥
   - Audit 路径：audit.py 所在目录
4. 设置调度方式
5. 启用任务

### 3. 执行任务

- **手动执行**：点击"执行"按钮立即运行
- **定时执行**：启用任务后自动按计划执行
- **停止任务**：运行中的任务可点击"停止"

### 4. 查看结果

#### 服务压力测试结果

- **仪表盘**：查看最近测试结果概览
- **压力测试结果页面**：
  - 筛选条件：任务、时间范围
  - 趋势图表：延迟、TTFT、RPS、生成速度
  - 详细列表：每次测试的具体指标
  - 查看日志：点击查看原始输出文件

#### 模型质量测试结果

- **质量测试结果页面**：
  - 筛选条件：任务、时间范围
  - 结果表格：11 项风险检测结果
  - 总体评级：HIGH/MEDIUM/LOW RISK
  - 查看报告：点击查看完整 Markdown 报告

## 🔧 API 文档

### 认证 API

- `POST /api/auth/login` - 登录
- `POST /api/auth/logout` - 登出
- `GET /api/auth/me` - 获取当前用户信息
- `POST /api/auth/change-password` - 修改密码

### 任务 API

- `GET /api/tasks/` - 获取任务列表
- `GET /api/tasks/<id>` - 获取任务详情
- `POST /api/tasks/` - 创建任务
- `PUT /api/tasks/<id>` - 更新任务
- `DELETE /api/tasks/<id>` - 删除任务
- `POST /api/tasks/<id>/run` - 执行任务
- `POST /api/tasks/<id>/stop` - 停止任务

### 结果 API

- `GET /api/results/perf` - 获取压力测试结果
- `GET /api/results/perf/<id>` - 获取单个结果
- `GET /api/results/perf/<id>/file` - 获取输出文件
- `GET /api/results/perf/chart-data` - 获取图表数据
- `GET /api/results/quality` - 获取质量测试结果
- `GET /api/results/quality/<id>` - 获取单个结果
- `GET /api/results/quality/<id>/raw` - 获取原始报告
- `GET /api/results/statistics` - 获取统计信息

## 🛠️ 部署指南

### 开发环境

```bash
# 后端
python run.py

# 前端（开发模式）
cd frontend
npm run dev
```

### 生产环境

#### 1. 构建前端

```bash
cd frontend
npm run build
```

构建产物在 `frontend/dist` 目录。

#### 2. 配置生产环境变量

```env
FLASK_ENV=production
SECRET_KEY=your-production-secret-key
MYSQL_PASSWORD=your-production-password
```

#### 3. 使用生产服务器

推荐使用 **Gunicorn** + **Nginx**：

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动 Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

#### 4. Nginx 配置

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static {
        alias /path/to/api_perf/frontend/dist;
    }
}
```

## 📝 开发指南

### 添加新的任务类型

1. 在 `backend/models.py` 中添加新的结果表模型
2. 在 `backend/executor/__init__.py` 中添加执行逻辑
3. 在 `backend/routes/results.py` 中添加结果查询路由
4. 在前端添加对应的配置表单和结果页面

### 自定义图表

修改 `frontend/src/views/PerfResults.vue` 中的 ECharts 配置。

### 扩展认证方式

继承 `Flask-Login` 的 `UserMixin` 类，实现自定义认证逻辑。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [Flask](https://flask.palletsprojects.com/)
- [Vue.js](https://vuejs.org/)
- [Element Plus](https://element-plus.org/)
- [ECharts](https://echarts.apache.org/)
- [evalscope](https://github.com/modelscope/evalscope)