#!/bin/bash
# 模拟 evalscope perf 命令输出

echo "Starting performance test..."
echo ""
echo "Test Configuration:"
echo "  API: openai"
echo "  URL: $2"
echo "  Model: $6"
echo "  Parallel: $8"
echo "  Number: ${10}"
echo ""
echo "Running test..."
sleep 2
echo ""
echo "Performance Metrics:"
echo "│ Concurrency │ Rate │   RPS   │ Avg Latency │ P99 Latency │ Avg TTFT │ P99 TTFT │ Avg TPOT │ P99 TPOT │ Gen Toks │ Success │"
echo "│─────────────┼──────┼─────────┼─────────────┼─────────────┼──────────┼──────────┼──────────┼──────────┼──────────┼─────────│"
echo "│           8 │  1.0 │   15.23 │       0.524 │       0.892 │    0.123 │    0.234 │    0.045 │    0.067 │    45.67 │    98% │"
echo ""
echo "Test completed successfully!"
