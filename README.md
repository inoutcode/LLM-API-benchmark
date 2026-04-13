# LLM API Benchmark - 大模型 API 测试平台

一个功能完整的前后端分离项目，用于大语言模型 API 的性能压力测试和质量安全测试。

## 🎯 项目简介

本项目提供了一站式的 LLM API 测试解决方案，支持：
- **性能压力测试**：基于 `evalscope perf` 进行高并发压力测试
- **质量安全测试**：基于 `audit.py` 进行模型安全性和质量评估
- **Web 管理界面**：现代化的 Vue3 前端，支持任务管理、结果查看、实时日志

## ✨ 功能特性

### 核心功能
- ✅ **任务管理**：创建、编辑、删除测试任务
- ✅ **定时调度**：支持手动执行、Cron 表达式、固定间隔三种调度方式
- ✅ **实时日志**：任务执行过程中实时查看日志输出
- ✅ **结果可视化**：图表展示性能指标趋势
- ✅ **历史记录**：保存所有测试历史，支持查询和对比

### 性能压力测试（基于 evalscope）
- 并发测试（支持 1-100 并发）
- 自定义请求数量
- 提示词长度配置
- Token 生成数量配置
- 连接和读取超时设置
- 性能指标：
  - **Latency**：请求总延迟（平均、P99）
  - **TTFT**：首字延迟（Time To First Token）
  - **TPOT**：每 Token 时间（Time Per Output Token）
  - **RPS**：每秒请求数（Requests Per Second）
  - **Gen. toks/s**：Token 生成速度
  - **Success Rate**：请求成功率

### 质量安全测试（基于 audit.py）
- 10 项安全检测：
  1. 基础设施侦察
  2. 模型列表枚举
  3. Token 注入检测
  4. Prompt 提取
  5. 指令冲突 + 身份替换
  6. 越狱测试
  7. 上下文长度扫描
  8. 工具调用改写
  9. 错误响应泄漏
  10. 流完整性
- 总体评级和风险摘要
- HTML 详细报告生成

## 🛠️ 技术栈

### 后端
- **框架**：Flask 3.0
- **数据库**：SQLite (SQLAlchemy ORM)
- **认证**：Flask-Login
- **调度**：APScheduler
- **跨域**：Flask-CORS

### 前端
- **框架**：Vue 3 (Composition API)
- **UI 组件**：Element Plus
- **路由**：Vue Router
- **构建工具**：Vite
- **HTTP 客户端**：Axios
- **日期处理**：Day.js

### 测试工具
- **性能测试**：evalscope (ModelScope)
- **质量测试**：audit.py (自定义安全测试脚本)

## 📁 项目结构

```
api_perf/
├── backend/                # 后端代码
│   ├── __init__.py        # Flask 应用初始化
│   ├── config.py          # 配置管理
│   ├── models.py          # 数据库模型
│   ├── executor/          # 任务执行器
│   │   └── __init__.py    # evalscope 和 audit 执行逻辑
│   └── routes/            # API 路由
│       ├── auth.py        # 认证接口
│       ├── tasks.py       # 任务管理接口
│       └── results.py     # 结果查询接口
│
├── frontend/              # 前端代码
│   ├── src/
│   │   ├── views/        # 页面组件
│   │   │   ├── Dashboard.vue      # 仪表盘
│   │   │   ├── Tasks.vue          # 任务管理
│   │   │   ├── PerfResults.vue    # 性能测试结果
│   │   │   ├── QualityResults.vue # 质量测试结果
│   │   │   ├── Login.vue          # 登录页
│   │   │   └── Layout.vue         # 布局组件
│   │   ├── utils/        # 工具函数
│   │   │   └── api.js    # API 封装
│   │   ├── router/       # 路由配置
│   │   ├── App.vue       # 根组件
│   │   └── main.js       # 入口文件
│   ├── index.html        # HTML 模板
│   ├── vite.config.js    # Vite 配置
│   └── package.json      # 前端依赖
│
├── audit.py              # 质量测试脚本
├── run.py                # 应用启动入口
├── init_db.py            # 数据库初始化
├── requirements.txt      # Python 依赖
├── config.json.example   # 配置文件示例
└── README.md             # 项目说明
```

## 🚀 快速开始

### 1. 环境要求

- Python >= 3.8
- Node.js >= 16.0.0
- npm >= 8.0.0

### 2. 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装 evalscope（性能测试）
pip install evalscope

# 安装前端依赖
cd frontend
npm install
```

### 3. 初始化数据库

```bash
python init_db.py
```

### 4. 构建前端

```bash
cd frontend
npm run build
```

### 5. 启动应用

```bash
# 方式 1：使用 Python
python run.py

# 方式 2：使用启动脚本
bash start.sh
```

应用将在 `http://localhost:5000` 启动。

### 7. 访问系统

- 访问地址：http://localhost:5000
- 默认账号：admin
- 默认密码：admin123

## 📖 使用指南

### 创建压力测试任务

1. 点击"新建任务"
2. 选择任务类型：**服务压力测试**
3. 填写配置：
   - LLM API URL：LLM API 地址（ openai 类型需以 v1/chat/completions 结尾 ）
   - API Key：认证密钥
   - 模型名称：要测试的模型
   - 并发数：并发请求数（1-100）
   - 请求数：总请求数量
   - **高级配置**：
     - 最小/最大提示长度
     - 最小/最大生成 Token 数
     - 连接超时
     - 读取超时
4. 设置调度方式（可选）
5. 点击"创建"

### 创建质量测试任务

1. 点击"新建任务"
2. 选择任务类型：**模型质量测试**
3. 填写配置：
   - API URL：API 地址（Base URL即可）
   - API Key：认证密钥
   - Audit 路径：audit.py 所在目录
4. 点击"创建"

### 查看测试结果

- **性能测试结果**：查看延迟、TTFT、TPOT、RPS 等指标的趋势图表
- **质量测试结果**：查看 10 项安全检测的评级和详细报告

## 📊 性能指标说明

| 指标 | 英文 | 说明 |
|------|------|------|
| **延迟** | Latency | 从发送请求到接收完整响应的总时间 |
| **首字延迟** | TTFT (Time To First Token) | 从发送请求到接收第一个 Token 的时间 |
| **每Token时间** | TPOT (Time Per Output Token) | 平均每个 Token 的生成时间 |
| **每秒请求数** | RPS (Requests Per Second) | 系统每秒处理的请求数量 |
| **生成速度** | Gen. toks/s | 每秒生成的 Token 数量 |
| **成功率** | Success Rate | 成功请求占总请求的比例 |

## 🔧 高级配置

### 任务调度

支持三种调度方式：

1. **手动执行**：点击"执行"按钮立即运行
2. **Cron 表达式**：使用标准 Cron 表达式定时执行
   - 格式：`秒 分 时 日 月 周`
   - 示例：`0 0 */2 * * *`（每 2 小时执行一次）
3. **固定间隔**：按固定时间间隔重复执行
   - 单位：秒
   - 示例：1800（每 30 分钟执行一次）

### 数据库配置

默认使用 SQLite，如需使用 MySQL：

```python
# backend/__init__.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:password@localhost/db_name'
```

## 📝 注意事项

1. **API Key 安全**：请妥善保管 API Key，不要提交到版本控制
2. **并发测试**：高并发测试可能对 API 服务造成压力，请谨慎设置并发数
3. **长时间测试**：建议使用后台运行方式，避免终端关闭导致任务中断
4. **磁盘空间**：测试会生成日志和结果文件，注意磁盘空间
5. **网络环境**：确保服务器能够访问目标 API

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [evalscope 文档](https://github.com/modelscope/evalscope)
- [Flask 文档](https://flask.palletsprojects.com/)
- [Vue 3 文档](https://vuejs.org/)
- [Element Plus 文档](https://element-plus.org/)

## 📮 联系方式

如有问题或建议，请提交 [GitHub Issue](https://github.com/inoutcode/LLM-API-benchmark/issues)。
