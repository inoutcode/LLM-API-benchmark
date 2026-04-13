#!/usr/bin/env python3
"""
生成 API 性能稳定性测试的可视化 HTML 报告
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import argparse


class HTMLReportGenerator:
    """HTML 报告生成器"""
    
    def __init__(self, json_file: str, output_file: str = "report.html"):
        self.json_file = Path(json_file)
        self.output_file = Path(output_file)
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """加载测试结果数据"""
        with open(self.json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _extract_time_series_data(self) -> Dict[str, List[Any]]:
        """提取时间序列数据"""
        time_series = {
            'test_index': [],
            'start_time': [],
            'avg_latency': [],
            'p99_latency': [],
            'avg_ttft': [],
            'p99_ttft': [],
            'avg_tpot': [],
            'p99_tpot': [],
            'rps': [],
            'gen_toks': [],
            'success_rate': [],
            'concurrency': []
        }
        
        for result in self.data['results']:
            if not result['success'] or not result['metrics']:
                continue
            
            # 取第一个并发级别的数据（通常是最重要的）
            # 也可以计算平均值或取最大并发
            metrics = result['metrics'][0]
            
            time_series['test_index'].append(result['test_index'])
            time_series['start_time'].append(result['start_time'])
            time_series['avg_latency'].append(metrics['avg_latency'])
            time_series['p99_latency'].append(metrics['p99_latency'])
            time_series['avg_ttft'].append(metrics['avg_ttft'])
            time_series['p99_ttft'].append(metrics['p99_ttft'])
            time_series['avg_tpot'].append(metrics['avg_tpot'])
            time_series['p99_tpot'].append(metrics['p99_tpot'])
            time_series['rps'].append(metrics['rps'])
            time_series['gen_toks'].append(metrics['gen_toks'])
            time_series['success_rate'].append(metrics['success_rate'])
            time_series['concurrency'].append(metrics['concurrency'])
        
        return time_series
    
    def _calculate_statistics(self, time_series: Dict[str, List[Any]]) -> Dict[str, Dict[str, float]]:
        """计算统计信息"""
        stats = {}
        
        metrics_keys = ['avg_latency', 'p99_latency', 'avg_ttft', 'p99_ttft', 
                        'avg_tpot', 'p99_tpot', 'rps', 'gen_toks', 'success_rate']
        
        for key in metrics_keys:
            values = [v for v in time_series[key] if v is not None and v > 0]
            if values:
                stats[key] = {
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'count': len(values)
                }
            else:
                stats[key] = {'min': 0, 'max': 0, 'avg': 0, 'count': 0}
        
        return stats
    
    def generate(self):
        """生成 HTML 报告"""
        time_series = self._extract_time_series_data()
        stats = self._calculate_statistics(time_series)
        
        html_content = self._build_html(time_series, stats)
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"报告已生成: {self.output_file}")
    
    def _build_html(self, time_series: Dict[str, List[Any]], 
                    stats: Dict[str, Dict[str, float]]) -> str:
        """构建 HTML 内容"""
        
        # 准备图表数据
        labels = time_series['start_time']
        
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API 性能稳定性测试报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .header h1 {{
            color: #2d3748;
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            color: #718096;
            font-size: 14px;
        }}
        
        .config-info {{
            background: #f7fafc;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            font-size: 13px;
            color: #4a5568;
        }}
        
        .config-info strong {{
            color: #2d3748;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .stat-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .stat-card h3 {{
            color: #718096;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
        }}
        
        .stat-card .value {{
            font-size: 24px;
            font-weight: 600;
            color: #2d3748;
        }}
        
        .stat-card .detail {{
            font-size: 12px;
            color: #a0aec0;
            margin-top: 5px;
        }}
        
        .chart-container {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .chart-container h2 {{
            color: #2d3748;
            font-size: 18px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e2e8f0;
        }}
        
        .chart-wrapper {{
            position: relative;
            height: 350px;
        }}
        
        .charts-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
        }}
        
        .full-width {{
            grid-column: 1 / -1;
        }}
        
        .footer {{
            text-align: center;
            color: white;
            padding: 20px;
            margin-top: 20px;
            font-size: 13px;
        }}
        
        .success {{
            color: #48bb78;
        }}
        
        .warning {{
            color: #ed8936;
        }}
        
        .error {{
            color: #f56565;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 API 性能稳定性测试报告</h1>
            <div class="subtitle">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            <div class="config-info">
                <strong>测试配置:</strong> 
                模型: {self.data['config'].get('model', 'N/A')} | 
                URL: {self.data['config'].get('url', 'N/A')} | 
                并发数: {self.data['config'].get('parallel', 'N/A')} | 
                请求数: {self.data['config'].get('number', 'N/A')} |
                总测试次数: {self.data['total_tests']}
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>平均延迟 (Avg Latency)</h3>
                <div class="value">{stats['avg_latency']['avg']:.2f}s</div>
                <div class="detail">最小: {stats['avg_latency']['min']:.2f}s | 最大: {stats['avg_latency']['max']:.2f}s</div>
            </div>
            <div class="stat-card">
                <h3>P99 延迟</h3>
                <div class="value">{stats['p99_latency']['avg']:.2f}s</div>
                <div class="detail">最小: {stats['p99_latency']['min']:.2f}s | 最大: {stats['p99_latency']['max']:.2f}s</div>
            </div>
            <div class="stat-card">
                <h3>平均 TTFT</h3>
                <div class="value">{stats['avg_ttft']['avg']:.2f}s</div>
                <div class="detail">最小: {stats['avg_ttft']['min']:.2f}s | 最大: {stats['avg_ttft']['max']:.2f}s</div>
            </div>
            <div class="stat-card">
                <h3>P99 TTFT</h3>
                <div class="value">{stats['p99_ttft']['avg']:.2f}s</div>
                <div class="detail">最小: {stats['p99_ttft']['min']:.2f}s | 最大: {stats['p99_ttft']['max']:.2f}s</div>
            </div>
            <div class="stat-card">
                <h3>平均 RPS</h3>
                <div class="value">{stats['rps']['avg']:.2f}</div>
                <div class="detail">最小: {stats['rps']['min']:.2f} | 最大: {stats['rps']['max']:.2f}</div>
            </div>
            <div class="stat-card">
                <h3>生成速度 (Tokens/s)</h3>
                <div class="value">{stats['gen_toks']['avg']:.2f}</div>
                <div class="detail">最小: {stats['gen_toks']['min']:.2f} | 最大: {stats['gen_toks']['max']:.2f}</div>
            </div>
            <div class="stat-card">
                <h3>平均 TPOT</h3>
                <div class="value">{stats['avg_tpot']['avg']:.4f}s</div>
                <div class="detail">最小: {stats['avg_tpot']['min']:.4f}s | 最大: {stats['avg_tpot']['max']:.4f}s</div>
            </div>
            <div class="stat-card">
                <h3>成功率</h3>
                <div class="value success">{stats['success_rate']['avg']:.1f}%</div>
                <div class="detail">最小: {stats['success_rate']['min']:.1f}% | 最大: {stats['success_rate']['max']:.1f}%</div>
            </div>
        </div>
        
        <div class="charts-row">
            <div class="chart-container">
                <h2>📈 延迟趋势 (Latency)</h2>
                <div class="chart-wrapper">
                    <canvas id="latencyChart"></canvas>
                </div>
            </div>
            
            <div class="chart-container">
                <h2>⏱️ TTFT 趋势 (首字延迟)</h2>
                <div class="chart-wrapper">
                    <canvas id="ttftChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="charts-row">
            <div class="chart-container">
                <h2>🚀 RPS 趋势 (每秒请求数)</h2>
                <div class="chart-wrapper">
                    <canvas id="rpsChart"></canvas>
                </div>
            </div>
            
            <div class="chart-container">
                <h2>⚡ 生成速度趋势 (Tokens/s)</h2>
                <div class="chart-wrapper">
                    <canvas id="genToksChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="charts-row">
            <div class="chart-container">
                <h2>🎯 TPOT 趋势 (每 Token 时间)</h2>
                <div class="chart-wrapper">
                    <canvas id="tpotChart"></canvas>
                </div>
            </div>
            
            <div class="chart-container">
                <h2>✅ 成功率趋势</h2>
                <div class="chart-wrapper">
                    <canvas id="successRateChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="footer">
            API Performance Stability Test Report | Generated by api_perf_test.py
        </div>
    </div>
    
    <script>
        const labels = {json.dumps(labels)};
        
        // 通用图表配置
        const defaultConfig = {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{
                    position: 'top',
                }},
            }},
            scales: {{
                y: {{
                    beginAtZero: false,
                }},
                x: {{
                    ticks: {{
                        maxRotation: 45,
                        minRotation: 45,
                        autoSkip: true,
                        maxTicksLimit: 10
                    }}
                }}
            }}
        }};
        
        // 延迟图表
        new Chart(document.getElementById('latencyChart'), {{
            type: 'line',
            data: {{
                labels: labels,
                datasets: [
                    {{
                        label: '平均延迟 (s)',
                        data: {json.dumps(time_series['avg_latency'])},
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                        tension: 0.3,
                        fill: true
                    }},
                    {{
                        label: 'P99 延迟 (s)',
                        data: {json.dumps(time_series['p99_latency'])},
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.1)',
                        tension: 0.3,
                        fill: true
                    }}
                ]
            }},
            options: defaultConfig
        }});
        
        // TTFT 图表
        new Chart(document.getElementById('ttftChart'), {{
            type: 'line',
            data: {{
                labels: labels,
                datasets: [
                    {{
                        label: '平均 TTFT (s)',
                        data: {json.dumps(time_series['avg_ttft'])},
                        borderColor: 'rgb(54, 162, 235)',
                        backgroundColor: 'rgba(54, 162, 235, 0.1)',
                        tension: 0.3,
                        fill: true
                    }},
                    {{
                        label: 'P99 TTFT (s)',
                        data: {json.dumps(time_series['p99_ttft'])},
                        borderColor: 'rgb(255, 159, 64)',
                        backgroundColor: 'rgba(255, 159, 64, 0.1)',
                        tension: 0.3,
                        fill: true
                    }}
                ]
            }},
            options: defaultConfig
        }});
        
        // RPS 图表
        new Chart(document.getElementById('rpsChart'), {{
            type: 'line',
            data: {{
                labels: labels,
                datasets: [{{
                    label: 'RPS',
                    data: {json.dumps(time_series['rps'])},
                    borderColor: 'rgb(153, 102, 255)',
                    backgroundColor: 'rgba(153, 102, 255, 0.1)',
                    tension: 0.3,
                    fill: true
                }}]
            }},
            options: defaultConfig
        }});
        
        // 生成速度图表
        new Chart(document.getElementById('genToksChart'), {{
            type: 'line',
            data: {{
                labels: labels,
                datasets: [{{
                    label: 'Tokens/s',
                    data: {json.dumps(time_series['gen_toks'])},
                    borderColor: 'rgb(255, 206, 86)',
                    backgroundColor: 'rgba(255, 206, 86, 0.1)',
                    tension: 0.3,
                    fill: true
                }}]
            }},
            options: defaultConfig
        }});
        
        // TPOT 图表
        new Chart(document.getElementById('tpotChart'), {{
            type: 'line',
            data: {{
                labels: labels,
                datasets: [
                    {{
                        label: '平均 TPOT (s)',
                        data: {json.dumps(time_series['avg_tpot'])},
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                        tension: 0.3,
                        fill: true
                    }},
                    {{
                        label: 'P99 TPOT (s)',
                        data: {json.dumps(time_series['p99_tpot'])},
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.1)',
                        tension: 0.3,
                        fill: true
                    }}
                ]
            }},
            options: defaultConfig
        }});
        
        // 成功率图表
        new Chart(document.getElementById('successRateChart'), {{
            type: 'line',
            data: {{
                labels: labels,
                datasets: [{{
                    label: '成功率 (%)',
                    data: {json.dumps(time_series['success_rate'])},
                    borderColor: 'rgb(72, 187, 120)',
                    backgroundColor: 'rgba(72, 187, 120, 0.1)',
                    tension: 0.3,
                    fill: true
                }}]
            }},
            options: {{
                ...defaultConfig,
                scales: {{
                    ...defaultConfig.scales,
                    y: {{
                        ...defaultConfig.scales.y,
                        min: 0,
                        max: 100
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>'''


def main():
    parser = argparse.ArgumentParser(description='生成 API 性能稳定性测试报告')
    parser.add_argument('--json-file', required=True, help='测试结果 JSON 文件路径')
    parser.add_argument('--output', default='report.html', help='输出 HTML 文件路径')
    
    args = parser.parse_args()
    
    generator = HTMLReportGenerator(args.json_file, args.output)
    generator.generate()


if __name__ == '__main__':
    main()
