#!/usr/bin/env python3
"""
API 性能稳定性测试程序
执行 evalscope perf 测试并记录结果，生成可视化 HTML 报告
"""

import subprocess
import time
import re
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse


class PerfMetrics:
    """性能指标数据类"""
    def __init__(self):
        self.concurrency: int = 0
        self.rate: str = ""
        self.rps: float = 0.0
        self.avg_latency: float = 0.0
        self.p99_latency: float = 0.0
        self.avg_ttft: float = 0.0
        self.p99_ttft: float = 0.0
        self.avg_tpot: float = 0.0
        self.p99_tpot: float = 0.0
        self.gen_toks: float = 0.0
        self.success_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "concurrency": self.concurrency,
            "rate": self.rate,
            "rps": self.rps,
            "avg_latency": self.avg_latency,
            "p99_latency": self.p99_latency,
            "avg_ttft": self.avg_ttft,
            "p99_ttft": self.p99_ttft,
            "avg_tpot": self.avg_tpot,
            "p99_tpot": self.p99_tpot,
            "gen_toks": self.gen_toks,
            "success_rate": self.success_rate
        }


class TestResult:
    """单次测试结果"""
    def __init__(self, test_index: int, start_time: str):
        self.test_index = test_index
        self.start_time = start_time
        self.end_time: str = ""
        self.metrics: List[PerfMetrics] = []
        self.raw_output: str = ""
        self.success: bool = True
        self.error_message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_index": self.test_index,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "metrics": [m.to_dict() for m in self.metrics],
            "success": self.success,
            "error_message": self.error_message
        }


class PerfOutputParser:
    """解析 evalscope perf 输出"""
    
    # 匹配性能指标表格行的正则表达式
    METRICS_PATTERN = re.compile(
        r'│\s*(\d+)\s*│\s*(\S+)\s*│\s*([\d.]+)\s*│\s*'
        r'([\d.]+)\s*│\s*([\d.]+)\s*│\s*'
        r'([\d.]+)\s*│\s*([\d.]+)\s*│\s*'
        r'([\d.]+)\s*│\s*([\d.]+)\s*│\s*'
        r'([\d.]+)\s*│\s*([\d.]+)%\s*│'
    )
    
    @classmethod
    def parse_output(cls, output: str) -> List[PerfMetrics]:
        """解析 evalscope 输出，提取性能指标"""
        metrics_list = []
        
        for line in output.split('\n'):
            match = cls.METRICS_PATTERN.search(line)
            if match:
                metrics = PerfMetrics()
                metrics.concurrency = int(match.group(1))
                metrics.rate = match.group(2)
                metrics.rps = float(match.group(3))
                metrics.avg_latency = float(match.group(4))
                metrics.p99_latency = float(match.group(5))
                metrics.avg_ttft = float(match.group(6))
                metrics.p99_ttft = float(match.group(7))
                metrics.avg_tpot = float(match.group(8))
                metrics.p99_tpot = float(match.group(9))
                metrics.gen_toks = float(match.group(10))
                metrics.success_rate = float(match.group(11))
                metrics_list.append(metrics)
        
        return metrics_list


class StabilityTest:
    """稳定性测试执行器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results: List[TestResult] = []
        self.log_file = Path(config.get('log_file', 'stability_test.log'))
        self.json_file = Path(config.get('json_file', 'test_results.json'))
    
    def build_command(self) -> List[str]:
        """构建 evalscope perf 命令"""
        cmd = [
            'evalscope', 'perf',
            '--api', self.config.get('api', 'openai'),
            '--url', self.config['url'],
            '--api-key', self.config['api_key'],
            '--model', self.config['model'],
            '--parallel', str(self.config.get('parallel', 8)),
            '--number', str(self.config.get('number', 50)),
            '--dataset', self.config.get('dataset', 'random'),
            '--min-prompt-length', str(self.config.get('min_prompt_length', 10)),
            '--max-prompt-length', str(self.config.get('max_prompt_length', 20)),
            '--min-tokens', str(self.config.get('min_tokens', 128)),
            '--max-tokens', str(self.config.get('max_tokens', 128)),
            '--tokenizer-path', self.config.get('tokenizer_path', 'gpt2'),
            '--timeout', str(self.config.get('timeout', 120))
        ]
        return cmd
    
    def run_single_test(self, test_index: int) -> TestResult:
        """执行单次测试"""
        start_time = datetime.now()
        result = TestResult(test_index, start_time.strftime('%Y-%m-%d %H:%M:%S'))
        
        # 记录到日志
        log_entry = f"\n{'='*60}\n第 {test_index} 次测试开始: {result.start_time}\n{'='*60}\n"
        self._write_log(log_entry)
        
        try:
            # 执行 evalscope perf 命令
            cmd = self.build_command()
            print(f"执行命令: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            output, _ = process.communicate()
            result.raw_output = output
            
            # 解析输出
            metrics = PerfOutputParser.parse_output(output)
            result.metrics = metrics
            
            if not metrics:
                result.success = False
                result.error_message = "未能解析到性能指标"
            
            # 写入日志
            self._write_log(output)
            
        except Exception as e:
            result.success = False
            result.error_message = str(e)
            self._write_log(f"错误: {str(e)}\n")
        
        result.end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._write_log(f"第 {test_index} 次测试完成: {result.end_time}\n")
        
        return result
    
    def _write_log(self, content: str):
        """写入日志文件"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(content)
    
    def save_results(self):
        """保存测试结果到 JSON 文件"""
        data = {
            "config": self.config,
            "test_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "total_tests": len(self.results),
            "results": [r.to_dict() for r in self.results]
        }
        
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def run(self, total_tests: int = 48, interval_seconds: int = 1800):
        """
        运行稳定性测试
        
        Args:
            total_tests: 总测试次数
            interval_seconds: 测试间隔时间（秒）
        """
        print(f"开始稳定性测试 - 共 {total_tests} 次，间隔 {interval_seconds} 秒")
        print(f"配置: {self.config}")
        
        start_msg = f"\n稳定性测试开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        self._write_log(start_msg)
        
        for i in range(1, total_tests + 1):
            print(f"\n执行第 {i}/{total_tests} 次测试...")
            
            result = self.run_single_test(i)
            self.results.append(result)
            
            # 保存中间结果
            self.save_results()
            
            # 如果不是最后一次，等待间隔
            if i < total_tests:
                wait_msg = f"等待 {interval_seconds} 秒后进行下一次测试..."
                print(wait_msg)
                self._write_log(f"{wait_msg}\n")
                time.sleep(interval_seconds)
        
        end_msg = f"\n稳定性测试完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        self._write_log(end_msg)
        print(end_msg)


def main():
    parser = argparse.ArgumentParser(description='API 性能稳定性测试程序')
    parser.add_argument('--url', required=True, help='API URL')
    parser.add_argument('--api-key', required=True, help='API Key')
    parser.add_argument('--model', required=True, help='模型名称')
    parser.add_argument('--parallel', type=int, default=8, help='并发数')
    parser.add_argument('--number', type=int, default=50, help='请求数量')
    parser.add_argument('--tests', type=int, default=48, help='总测试次数')
    parser.add_argument('--interval', type=int, default=1800, help='测试间隔（秒）')
    parser.add_argument('--log-file', default='stability_test.log', help='日志文件路径')
    parser.add_argument('--json-file', default='test_results.json', help='结果 JSON 文件路径')
    parser.add_argument('--api', default='openai', help='API 类型')
    parser.add_argument('--dataset', default='random', help='数据集类型')
    parser.add_argument('--min-prompt-length', type=int, default=10, help='最小提示词长度')
    parser.add_argument('--max-prompt-length', type=int, default=20, help='最大提示词长度')
    parser.add_argument('--min-tokens', type=int, default=128, help='最小生成 tokens')
    parser.add_argument('--max-tokens', type=int, default=128, help='最大生成 tokens')
    parser.add_argument('--tokenizer-path', default='gpt2', help='分词器路径')
    parser.add_argument('--timeout', type=int, default=120, help='超时时间（秒）')
    
    args = parser.parse_args()
    
    config = {
        'api': args.api,
        'url': args.url,
        'api_key': args.api_key,
        'model': args.model,
        'parallel': args.parallel,
        'number': args.number,
        'dataset': args.dataset,
        'min_prompt_length': args.min_prompt_length,
        'max_prompt_length': args.max_prompt_length,
        'min_tokens': args.min_tokens,
        'max_tokens': args.max_tokens,
        'tokenizer_path': args.tokenizer_path,
        'timeout': args.timeout,
        'log_file': args.log_file,
        'json_file': args.json_file
    }
    
    tester = StabilityTest(config)
    tester.run(total_tests=args.tests, interval_seconds=args.interval)


if __name__ == '__main__':
    main()