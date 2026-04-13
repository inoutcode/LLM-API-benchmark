# 项目文件清单

## 📋 后端文件

### 核心文件
- `backend/__init__.py` - Flask 应用初始化
- `backend/models.py` - 数据库模型定义（4个表）
- `backend/config.py` - 配置管理

### 路由文件
- `backend/routes/auth.py` - 认证 API（登录、登出、修改密码）
- `backend/routes/tasks.py` - 任务管理 API（CRUD、执行、停止）
- `backend/routes/results.py` - 结果查询 API（压力测试、质量测试）

### 执行器
- `backend/executor/__init__.py` - 任务执行器（两种任务类型）

## 📋 前端文件

### 入口文件
- `frontend/index.html` - HTML 入口
- `frontend/src/main.js` - Vue 应用入口
- `frontend/src/App.vue` - 根组件

### 配置文件
- `frontend/vite.config.js` - Vite 构建配置
- `frontend/package.json` - 前端依赖配置

### 路由
- `frontend/src/router/index.js` - 路由配置

### 工具
- `frontend/src/utils/api.js` - API 请求封装

### 页面组件
- `frontend/src/views/Login.vue` - 登录页面
- `frontend/src/views/Layout.vue` - 主布局组件
- `frontend/src/views/Dashboard.vue` - 仪表盘
- `frontend/src/views/Tasks.vue` - 任务管理页面
- `frontend/src/views/PerfResults.vue` - 压力测试结果页面
- `frontend/src/views/QualityResults.vue` - 质量测试结果页面

## 📋 配置和启动文件

- `run.py` - 应用启动脚本
- `init_db.py` - 数据库初始化脚本
- `start.sh` - 快速启动脚本
- `Makefile` - 常用命令集合
- `requirements.txt` - Python 依赖
- `.env.example` - 环境变量模板
- `.env` - 环境变量配置（需自行配置）
- `.gitignore` - Git 忽略规则

## 📋 文档文件

- `README_NEW.md` - 完整项目文档
- `ARCHITECTURE_NEW.md` - 架构设计文档
- `QUICKSTART.md` - 快速开始指南
- `PROJECT_SUMMARY.md` - 项目总结
- `FILE_LIST.md` - 本文件

## 📋 数据库表结构

### users 表
- id, username, password_hash, created_at, updated_at

### tasks 表
- id, name, task_type, config
- schedule_type, cron_expression, interval_seconds
- start_time, end_time, is_enabled, status
- last_run_time, next_run_time
- created_at, updated_at

### perf_test_results 表
- id, task_id, execution_time
- concurrency, avg_latency, p99_latency
- avg_ttft, p99_ttft
- avg_tpot, p99_tpot
- rps, gen_toks, success_rate
- output_file, status, error_message
- created_at

### quality_test_results 表
- id, task_id, execution_time
- infrastructure_recon, models_enumerated
- token_injection, extraction_attempts
- cat_test, context_boundary
- tool_call_substitution
- error_response_leakage
- stream_integrity
- overall_rating
- output_file, status, error_message
- created_at

## 📊 统计信息

- **后端文件**: 7 个 Python 文件
- **前端文件**: 10 个 Vue/JS 文件
- **配置文件**: 6 个
- **文档文件**: 5 个
- **数据库表**: 4 个
- **API 接口**: 15+ 个
- **页面组件**: 6 个

## 🚀 快速启动步骤

1. 安装依赖：`make install`
2. 配置数据库：编辑 `.env`
3. 初始化数据库：`make init-db`
4. 构建前端：`make build`
5. 启动应用：`make run`

访问：http://localhost:5000
登录：admin / admin123