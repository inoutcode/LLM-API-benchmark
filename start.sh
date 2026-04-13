#!/bin/bash

# 模型质量测试管理后台 - 快速启动脚本

echo "======================================"
echo "  模型质量测试管理后台"
echo "======================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3"
    exit 1
fi

# 检查 MySQL
echo "检查 MySQL 连接..."
if ! command -v mysql &> /dev/null; then
    echo "⚠️  警告: 未找到 mysql 命令，请确保 MySQL 已安装并运行"
fi

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 文件，使用 .env.example 创建..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件，请编辑配置数据库连接信息"
    echo ""
    read -p "是否现在编辑 .env 文件？ (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ${EDITOR:-vim} .env
    fi
fi

# 加载环境变量
export $(cat .env | grep -v '^#' | xargs)

# 检查 Python 依赖
echo ""
echo "检查 Python 依赖..."
if ! python3 -c "import flask" &> /dev/null; then
    echo "⚠️  Flask 未安装"
    read -p "是否安装依赖？ (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip3 install -r requirements.txt
    else
        echo "❌ 请先安装依赖: pip3 install -r requirements.txt"
        exit 1
    fi
fi

# 初始化数据库
echo ""
read -p "是否初始化数据库？ (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 init_db.py
fi

# 检查前端构建
if [ ! -d "frontend/dist" ]; then
    echo ""
    echo "⚠️  前端未构建"
    read -p "是否构建前端？ (需要 Node.js) (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v npm &> /dev/null; then
            cd frontend
            npm install
            npm run build
            cd ..
        else
            echo "❌ 未找到 npm，请先安装 Node.js"
            exit 1
        fi
    fi
fi

# 启动应用
echo ""
echo "启动应用..."
echo "访问地址: http://localhost:5000"
echo "默认账号: admin / admin123"
echo ""

python3 run.py
