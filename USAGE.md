# API 性能稳定性测试工具 - 快速开始

## 🚀 快速开始

### 1. 配置测试参数

复制示例配置文件并修改：

```bash
cp config.json.example config.json
```

编辑 `config.json`，填入你的 API 信息：

```json
{
  "api": "openai",
  "url": "https://your-api-url.com",
  "api_key": "YOUR_API_KEY_HERE",  // ⚠️ 替换为你的 API Key
  "model": "your-model-name",
  "parallel": 8,
  "number": 50,
  "test_schedule": {
    "total_tests": 48,           // 测试次数
    "interval_seconds": 1800,    // 间隔时间（秒）
    "description": "24小时测试，每30分钟一次"
  }
}
```

### 2. 运行测试

#### 方式一：一键运行（推荐）

```bash
./run_all.sh
```

#### 方式二：使用配置文件

```bash
python3 run_test.py --config config.json
```

#### 方式三：命令行参数

```bash
python3 api_perf_test.py \
  --url "https://your-api-url.com" \
  --api-key "YOUR_API_KEY" \
  --model "your-model" \
  --tests 48 \
  --interval 1800
```

### 3. 生成报告

测试完成后，自动或手动生成 HTML 报告：

```bash
python3 generate_report.py --json-file test_results.json --output report.html
```

## 📊 报告内容

HTML 报告包含以下可视化图表：

1. **延迟趋势图** - 平均延迟和 P99 延迟随时间变化
2. **TTFT 趋势图** - 首字延迟（Time To First Token）
3. **RPS 趋势图** - 每秒请求数
4. **生成速度图** - Token 生成速度
5. **TPOT 趋势图** - 每 Token 时间
6. **成功率图** - 请求成功率

## 🧪 快速测试

验证工具是否正常工作：

```bash
./quick_test.sh
```

这将创建模拟数据并生成测试报告。

## 📁 输出文件

- `stability_test.log` - 详细测试日志
- `test_results.json` - 结构化测试结果
- `report.html` - 可视化 HTML 报告

## ⚙️ 高级用法

### 后台运行长时间测试

```bash
nohup python3 run_test.py --config config.json > test_output.log 2>&1 &
```

### 自定义测试参数

```bash
# 快速测试（5次，间隔1分钟）
python3 api_perf_test.py \
  --url "https://api.example.com" \
  --api-key "sk-xxxx" \
  --model "gpt-3.5-turbo" \
  --tests 5 \
  --interval 60

# 高并发测试
python3 api_perf_test.py \
  --url "https://api.example.com" \
  --api-key "sk-xxxx" \
  --model "gpt-3.5-turbo" \
  --parallel 16 \
  --number 100
```

## 📋 性能指标说明

| 指标 | 全称 | 说明 |
|------|------|------|
| **Latency** | Latency | 请求总延迟（从发送到接收完整响应） |
| **TTFT** | Time To First Token | 首字延迟（从发送到接收第一个 token） |
| **TPOT** | Time Per Output Token | 每 token 时间（生成速度的倒数） |
| **RPS** | Requests Per Second | 每秒请求数 |
| **Gen. toks/s** | Generated Tokens/s | Token 生成速度 |
| **Success Rate** | Success Rate | 请求成功率 |

## 🔧 故障排查

### 问题：找不到 evalscope 命令

**解决方案**：安装 evalscope

```bash
pip install evalscope
```

### 问题：API Key 错误

**解决方案**：检查 `config.json` 中的 `api_key` 是否正确

### 问题：测试失败

**解决方案**：查看日志文件 `stability_test.log` 获取详细错误信息

## 📝 注意事项

1. ⚠️ **API Key 安全**：不要将包含真实 API Key 的 `config.json` 提交到版本控制
2. 💾 **磁盘空间**：长时间测试会产生大量日志，注意磁盘空间
3. 🌐 **网络连接**：HTML 报告需要网络连接加载 Chart.js
4. ⏰ **测试时间**：长时间测试建议使用 `nohup` 或 `screen`

## 📞 获取帮助

查看完整文档：

```bash
python3 api_perf_test.py --help
python3 generate_report.py --help
```

## 📄 许可证

MIT License
