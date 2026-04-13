# API 性能稳定性测试工具

基于 `evalscope perf` 的 API 性能稳定性测试工具，支持长时间测试和可视化报告生成。

## 功能特性

- ✅ 自动执行多次性能测试
- ✅ 解析 evalscope perf 输出
- ✅ 保存结构化测试结果（JSON）
- ✅ 生成可视化 HTML 报告
- ✅ 支持自定义测试参数
- ✅ 实时日志记录

## 文件说明

```
api_perf/
├── api_perf_test.py      # 主测试程序
├── generate_report.py    # HTML 报告生成器
├── requirements.txt      # 依赖包
└── README.md            # 使用说明
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 运行稳定性测试

```bash
python api_perf_test.py \
  --url "https://tokensea.ai" \
  --api-key "sk-xxxx" \
  --model "Qwen2.5-0.5B-Instruct" \
  --parallel 8 \
  --number 50 \
  --tests 48 \
  --interval 1800
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--url` | API URL | 必填 |
| `--api-key` | API Key | 必填 |
| `--model` | 模型名称 | 必填 |
| `--parallel` | 并发数 | 8 |
| `--number` | 每次测试的请求数 | 50 |
| `--tests` | 总测试次数 | 48 |
| `--interval` | 测试间隔（秒） | 1800 (30分钟) |
| `--log-file` | 日志文件路径 | stability_test.log |
| `--json-file` | 结果 JSON 文件路径 | test_results.json |
| `--api` | API 类型 | openai |
| `--dataset` | 数据集类型 | random |
| `--min-prompt-length` | 最小提示词长度 | 10 |
| `--max-prompt-length` | 最大提示词长度 | 20 |
| `--min-tokens` | 最小生成 tokens | 128 |
| `--max-tokens` | 最大生成 tokens | 128 |
| `--tokenizer-path` | 分词器路径 | gpt2 |
| `--timeout` | 超时时间（秒） | 120 |

### 2. 生成 HTML 报告

测试完成后，使用生成的 JSON 文件创建可视化报告：

```bash
python generate_report.py \
  --json-file test_results.json \
  --output report.html
```

然后在浏览器中打开 `report.html` 查看报告。

## 测试输出

### 1. 日志文件 (stability_test.log)

包含所有测试的原始输出和 evalscope perf 的完整日志。

### 2. 结果文件 (test_results.json)

结构化的测试结果，包含：
- 测试配置
- 每次测试的时间戳
- 解析后的性能指标
- 成功/失败状态

### 3. HTML 报告 (report.html)

可视化报告包含：
- 测试概览和配置信息
- 关键指标统计卡片
- 6 个趋势图表：
  - 延迟趋势（平均和 P99）
  - TTFT 趋势（平均和 P99）
  - RPS 趋势
  - 生成速度趋势
  - TPOT 趋势（平均和 P99）
  - 成功率趋势

## 性能指标说明

| 指标 | 说明 |
|------|------|
| **Latency** | 请求总延迟 |
| **TTFT** | Time To First Token，首字延迟 |
| **TPOT** | Time Per Output Token，每 token 时间 |
| **RPS** | Requests Per Second，每秒请求数 |
| **Gen. toks/s** | 生成 token 速度 |
| **Success Rate** | 请求成功率 |

## 示例

### 运行 24 小时测试（每 30 分钟一次）

```bash
python api_perf_test.py \
  --url "https://api.example.com" \
  --api-key "sk-xxxxx" \
  --model "gpt-3.5-turbo" \
  --tests 48 \
  --interval 1800
```

### 快速测试（5 次，间隔 1 分钟）

```bash
python api_perf_test.py \
  --url "https://api.example.com" \
  --api-key "sk-xxxxx" \
  --model "gpt-3.5-turbo" \
  --tests 5 \
  --interval 60
```

## 注意事项

1. 确保已安装 `evalscope` 工具
2. API Key 请妥善保管，不要提交到版本控制
3. 长时间测试建议使用 `nohup` 或 `screen` 运行
4. 测试过程中会生成大量日志，注意磁盘空间

## 后台运行示例

```bash
nohup python api_perf_test.py \
  --url "https://api.example.com" \
  --api-key "sk-xxxxx" \
  --model "gpt-3.5-turbo" \
  --tests 48 \
  --interval 1800 \
  > test_output.log 2>&1 &
```

## 许可证

MIT License
