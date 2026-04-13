#!/usr/bin/env python3
"""
从配置文件运行 API 性能稳定性测试
"""

import json
import argparse
from pathlib import Path
from api_perf_test import StabilityTest


def load_config(config_file: str) -> dict:
    """加载配置文件"""
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description='从配置文件运行 API 性能稳定性测试')
    parser.add_argument('--config', default='config.json', help='配置文件路径')
    parser.add_argument('--tests', type=int, help='总测试次数（覆盖配置文件）')
    parser.add_argument('--interval', type=int, help='测试间隔（秒，覆盖配置文件）')
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    
    # 获取测试计划
    test_schedule = config.pop('test_schedule', {})
    total_tests = args.tests or test_schedule.get('total_tests', 48)
    interval_seconds = args.interval or test_schedule.get('interval_seconds', 1800)
    
    print(f"配置加载成功: {args.config}")
    print(f"测试计划: {total_tests} 次，间隔 {interval_seconds} 秒")
    if 'description' in test_schedule:
        print(f"描述: {test_schedule['description']}")
    
    # 运行测试
    tester = StabilityTest(config)
    tester.run(total_tests=total_tests, interval_seconds=interval_seconds)


if __name__ == '__main__':
    main()
