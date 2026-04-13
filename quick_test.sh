#!/bin/bash

# 快速测试脚本 - 验证工具是否正常工作

echo "======================================"
echo "  快速测试 - 验证工具功能"
echo "======================================"
echo ""

# 创建测试数据
echo "创建模拟测试数据..."
python3 << 'EOF'
import json
from datetime import datetime, timedelta

# 创建模拟测试结果
results = []
base_time = datetime.now()

for i in range(5):
    result = {
        "test_index": i + 1,
        "start_time": (base_time + timedelta(minutes=i*30)).strftime('%Y-%m-%d %H:%M:%S'),
        "end_time": (base_time + timedelta(minutes=i*30, seconds=120)).strftime('%Y-%m-%d %H:%M:%S'),
        "metrics": [
            {
                "concurrency": 10,
                "rate": "INF",
                "rps": 0.07 + i * 0.01,
                "avg_latency": 45.0 + i * 2.0,
                "p99_latency": 150.0 + i * 5.0,
                "avg_ttft": 1.4 + i * 0.1,
                "p99_ttft": 2.5 + i * 0.2,
                "avg_tpot": 0.024,
                "p99_tpot": 0.029,
                "gen_toks": 120.0 + i * 5.0,
                "success_rate": 100.0
            }
        ],
        "success": True,
        "error_message": ""
    }
    results.append(result)

data = {
    "config": {
        "api": "openai",
        "url": "https://test.example.com",
        "model": "test-model",
        "parallel": 8,
        "number": 50
    },
    "test_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    "total_tests": 5,
    "results": results
}

with open('test_results.json', 'w') as f:
    json.dump(data, f, indent=2)

print("模拟测试数据已创建: test_results.json")
EOF

# 生成报告
echo ""
echo "生成 HTML 报告..."
python3 generate_report.py --json-file test_results.json --output test_report.html

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 测试成功！"
    echo "报告已生成: test_report.html"
    echo ""
    
    # 询问是否打开报告
    read -p "是否打开报告？ (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v open &> /dev/null; then
            open test_report.html
        elif command -v xdg-open &> /dev/null; then
            xdg-open test_report.html
        else
            echo "请手动打开 test_report.html"
        fi
    fi
else
    echo ""
    echo "❌ 测试失败"
    exit 1
fi
