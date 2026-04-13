.PHONY: help install init-db run dev build clean

# 默认目标
help:
	@echo "模型质量测试管理后台"
	@echo ""
	@echo "使用方法:"
	@echo "  make install      - 安装 Python 依赖"
	@echo "  make init-db      - 初始化数据库"
	@echo "  make run          - 启动应用"
	@echo "  make dev          - 开发模式（前后端分离）"
	@echo "  make build        - 构建前端"
	@echo "  make clean        - 清理临时文件"
	@echo ""
	@echo "快速开始:"
	@echo "  1. make install"
	@echo "  2. 配置 .env 文件"
	@echo "  3. make init-db"
	@echo "  4. make build"
	@echo "  5. make run"

# 安装依赖
install:
	@echo "安装 Python 依赖..."
	pip3 install -r requirements.txt
	@echo "✅ 依赖安装完成"

# 初始化数据库
init-db:
	@echo "初始化数据库..."
	python3 init_db.py

# 启动应用
run:
	@echo "启动应用..."
	python3 run.py

# 开发模式
dev:
	@echo "启动开发模式..."
	@echo "后端: http://localhost:5000"
	@echo "前端: http://localhost:3000"
	@echo ""
	@# 启动后端
	@python3 run.py &
	@# 启动前端开发服务器
	@cd frontend && npm run dev

# 构建前端
build:
	@echo "构建前端..."
	cd frontend && npm install && npm run build
	@echo "✅ 前端构建完成"

# 清理
clean:
	@echo "清理临时文件..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ 清理完成"

# 创建数据库
create-db:
	@echo "创建数据库..."
	@echo "请输入 MySQL root 密码:"
	mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS model_test_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
	@echo "✅ 数据库创建完成"