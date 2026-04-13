#!/bin/bash

# API 性能稳定性测试一键启动脚本

echo "======================================"
echo "  API 性能稳定性测试工具"
echo "======================================"
echo ""

# 检查配置文件
if [ ! -f "config.json" ]; then
    echo "错误: 未找到 config.json 配置文件"
    echo "请先创建配置文件，参考 config.json.example"
    exit 1
fi

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3"
    exit 1
fi

# 检查 evalscope
if ! command -v evalscope &> /dev/null; then
    echo "警告: 未找到 evalscope 命令"
    echo "请确保已安装 evalscope: pip install evalscope"
    read -p "是否继续？ (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 询问是否运行测试
read -p "是否开始运行测试？ (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "开始运行测试..."
    echo ""
    
    # 运行测试
    python3 run_test.py --config config.json
    
    # 检查测试是否成功
    if [ $? -eq 0 ]; then
        echo ""
        echo "测试完成！"
        
        # 询问是否生成报告
        read -p "是否生成 HTML 报告？ (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo ""
            echo "生成 HTML 报告..."
            python3 generate_report.py --json-file test_results.json --output report.html
            
            if [ $? -eq 0 ]; then
                echo ""
                echo "报告生成成功: report.html"
                
                # 询问是否打开报告
                read -p "是否打开报告？ (y/n) " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    if command -v open &> /dev/null; then
                        open report.html
                    elif command -v xdg-open &> /dev/null; then
                        xdg-open report.html
                    else
                        echo "请手动打开 report.html"
                    fi
                fi
            fi
        fi
    else
        echo ""
        echo "测试过程中出现错误，请检查日志文件"
        exit 1
    fi
else
    echo "已取消测试"
fi

echo ""
echo "完成！"
