"""
任务执行器
"""
import subprocess
import os
import re
import json
from datetime import datetime
from pathlib import Path
from threading import Thread
import threading
from ..models import db, Task, PerfTestResult, QualityTestResult
from flask import current_app


class TaskExecutor:
    """任务执行器"""
    
    def __init__(self):
        self.running_tasks = {}
        self.lock = threading.Lock()
    
    def execute_async(self, task):
        """异步执行任务"""
        # 获取当前 app 实例
        app = current_app._get_current_object()
        thread = Thread(target=self._execute_task, args=(app, task.id))
        thread.daemon = True
        thread.start()
    
    def execute_scheduled(self, task_id):
        """调度执行任务"""
        from .. import create_app
        
        app = create_app()
        with app.app_context():
            task = Task.query.get(task_id)
            if task and task.is_enabled:
                self._execute_task(task_id)
    
    def stop(self, task):
        """停止任务"""
        with self.lock:
            if task.id in self.running_tasks:
                process = self.running_tasks[task.id]
                if process:
                    process.terminate()
                del self.running_tasks[task.id]
        
        # 更新任务状态
        task.status = 'idle'
        db.session.commit()
    
    def _update_next_run_time(self, task):
        """更新下次执行时间"""
        from .. import scheduler
        
        job_id = f'task_{task.id}'
        job = scheduler.get_job(job_id)
        
        if job and job.next_run_time:
            # 直接存储本地时间（北京时间）
            task.next_run_time = job.next_run_time.replace(tzinfo=None) if job.next_run_time.tzinfo else job.next_run_time
            db.session.commit()
    
    def _execute_task(self, app, task_id):
        """执行任务"""
        with app.app_context():
            task = Task.query.get(task_id)
            if not task:
                return
            
            try:
                # 更新任务状态
                task.status = 'running'
                task.last_run_time = datetime.now()
                db.session.commit()

                app.logger.info(f"[Task {task_id}] Starting: {task.name}")

                # 根据任务类型执行
                if task.task_type == 'perf_test':
                    result = self._execute_perf_test(task, app)
                elif task.task_type == 'quality_test':
                    result = self._execute_quality_test(task, app)
                else:
                    raise ValueError(f"Unknown task type: {task.task_type}")

                # 更新任务状态
                task.status = 'success'
                db.session.commit()
                app.logger.info(f"[Task {task_id}] Completed successfully")

                # 更新下次执行时间
                self._update_next_run_time(task)

            except Exception as e:
                app.logger.error(f"[Task {task_id}] Failed: {str(e)}")
                task.status = 'failed'
                db.session.commit()

                # 即使失败也要更新下次执行时间
                self._update_next_run_time(task)
    
    def _execute_perf_test(self, task, app):
        """执行服务压力测试"""
        config = json.loads(task.config)

        # 简化日志，只记录关键信息
        app.logger.info(f"[Task {task.id}] Perf test - model: {config.get('model')}, parallel: {config.get('parallel')}")
        
        # 生成唯一的输出目录名（使用任务ID和时间戳）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_output_dir = f"evalscope_outputs/task_{task.id}"
        
        # 构建命令（使用正确的参数名）
        cmd = [
            'evalscope', 'perf',
            '--model', config['model'],
            '--api', config.get('api', 'openai'),
            '--url', config['url'],
            '--api-key', config['api_key'],
            '--tokenizer-path', config.get('tokenizer_path', 'Qwen/Qwen2-1.5B-Instruct'),
            '--parallel', str(config.get('parallel', 8)),
            '-n', str(config.get('number', 50)),
            '--dataset', config.get('dataset', 'random'),
            '--min-prompt-length', str(config.get('min_prompt_length', 10)),
            '--max-prompt-length', str(config.get('max_prompt_length', 20)),
            '--min-tokens', str(config.get('min_tokens', 128)),
            '--max-tokens', str(config.get('max_tokens', 128)),
            '--connect-timeout', str(config.get('connect_timeout', 60)),
            '--read-timeout', str(config.get('read_timeout', 120)),
            '--outputs-dir', unique_output_dir,  # 使用唯一输出目录
            '--stream'
        ]
        
        # 格式化命令为多行显示
        cmd_str = ' \\\n  '.join(['evalscope perf'] + [
            f'--model {config["model"]}',
            f"--api {config.get('api', 'openai')}",
            f"--url {config['url']}",
            f"--api-key {config['api_key'][:10]}...",  # 隐藏部分密钥
            f"--tokenizer-path {config.get('tokenizer_path', 'Qwen/Qwen2-1.5B-Instruct')}",
            f"--parallel {config.get('parallel', 8)}",
            f"-n {config.get('number', 50)}",
            f"--dataset {config.get('dataset', 'random')}",
            f"--min-prompt-length {config.get('min_prompt_length', 10)}",
            f"--max-prompt-length {config.get('max_prompt_length', 20)}",
            f"--min-tokens {config.get('min_tokens', 128)}",
            f"--max-tokens {config.get('max_tokens', 128)}",
            f"--connect-timeout {config.get('connect_timeout', 60)}",
            f"--read-timeout {config.get('read_timeout', 120)}",
            f"--outputs-dir {unique_output_dir}",
            '--stream'
        ])

        # 检查是否使用模拟器（用于测试）
        use_mock = app.config.get('USE_MOCK_EVALSCOPE', False)
        if use_mock:
            cmd = ['./mock_evalscope.sh'] + cmd[1:]
        
        # 创建输出目录和文件（提前创建，支持实时写入）
        output_dir = Path(app.config['UPLOAD_FOLDER']) / f"task_{task.id}"
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"perf_{timestamp}.txt"
        filepath = output_dir / filename
        output_file = str(filepath)
        
        # 执行命令（使用行缓冲实现实时读取）
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1  # 行缓冲
        )
        
        # 记录运行中的任务
        with self.lock:
            self.running_tasks[task.id] = process
        
        # 实时读取输出并写入文件
        output_lines = []
        with open(filepath, 'w', encoding='utf-8') as f:
            for line in iter(process.stdout.readline, ''):
                if not line:
                    break
                f.write(line)
                f.flush()  # 立即刷新到磁盘
                output_lines.append(line)
        
        # 等待进程结束
        process.wait()
        output = ''.join(output_lines)

        # 清理
        with self.lock:
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]

        # 检查进程返回码
        if process.returncode != 0:
            app.logger.warning(f"Process terminated with return code: {process.returncode}")
            raise RuntimeError(f"Process terminated unexpectedly (return code: {process.returncode})")

        # 解析结果
        metrics = self._parse_perf_output(output)

        # 必须解析到性能指标才算成功
        if not metrics:
            app.logger.error("Failed to parse performance metrics from output")
            raise RuntimeError("Failed to parse performance metrics - no valid results found in output")
        
        # 保存结果到数据库
        result = PerfTestResult(
            task_id=task.id,
            execution_time=datetime.now(),
            command=cmd_str,
            output_file=output_file,
            status='success'
        )
        
        result.concurrency = metrics.get('concurrency')
        result.avg_latency = metrics.get('avg_latency')
        result.p99_latency = metrics.get('p99_latency')
        result.avg_ttft = metrics.get('avg_ttft')
        result.p99_ttft = metrics.get('p99_ttft')
        result.avg_tpot = metrics.get('avg_tpot')
        result.p99_tpot = metrics.get('p99_tpot')
        result.rps = metrics.get('rps')
        result.gen_toks = metrics.get('gen_toks')
        result.success_rate = metrics.get('success_rate')
        
        db.session.add(result)
        db.session.commit()
        
        app.logger.info(f"Perf test result saved: {result.id}")
        
        return result
    
    def _execute_quality_test(self, task, app):
        """执行模型质量测试"""
        config = json.loads(task.config)
        
        app.logger.info(f"Executing quality test with config: {config}")
        
        # 确定 audit.py 的路径
        audit_path = config.get('audit_path', '')
        if audit_path:
            # 如果指定了路径，使用指定路径
            audit_script = os.path.join(audit_path, 'audit.py')
            work_dir = audit_path
        else:
            # 否则使用项目根目录下的 audit.py
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            audit_script = os.path.join(project_root, 'audit.py')
            work_dir = project_root
        
        app.logger.info(f"Audit script path: {audit_script}")
        app.logger.info(f"Working directory: {work_dir}")
        
        # 创建输出目录和文件（提前创建，支持实时写入）
        output_dir = Path(app.config['UPLOAD_FOLDER']) / f"task_{task.id}"
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"quality_{timestamp}.txt"
        filepath = output_dir / filename
        output_file = str(filepath)
        
        # 报告文件路径（与日志文件同目录，命名为 quality_{timestamp}_report.md）
        report_path = output_file # str(output_dir / f"quality_{timestamp}_report.md")
        
        # 构建命令
        cmd = [
            'python', audit_script,
            '--key', config['api_key'],
            '--url', config['url'],
            # '--output', report_path
        ]
        
        # 格式化命令为多行显示
        cmd_str = ' \\\n  '.join([
            f'python {audit_script}',
            f"--key {config['api_key'][:10]}...",  # 隐藏部分密钥
            f"--url {config['url']}",
            # f"--output {report_path}"
        ])

        # 执行命令（使用行缓冲实现实时读取）
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,  # 行缓冲
            cwd=work_dir
        )
        
        # 记录运行中的任务
        with self.lock:
            self.running_tasks[task.id] = process
        
        # 实时读取输出并写入文件
        output_lines = []
        with open(filepath, 'w', encoding='utf-8') as f:
            for line in iter(process.stdout.readline, ''):
                if not line:
                    break
                f.write(line)
                f.flush()  # 立即刷新到磁盘
                output_lines.append(line)
        
        # 等待进程结束
        process.wait()
        output = ''.join(output_lines)

        # 清理
        with self.lock:
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]

        # 检查进程返回码
        if process.returncode != 0:
            app.logger.warning(f"Process terminated with return code: {process.returncode}")
            raise RuntimeError(f"Process terminated unexpectedly (return code: {process.returncode})")

        # 从报告文件中解析结果
        risk_summary = {}
        if os.path.exists(report_path):
            with open(report_path, 'r', encoding='utf-8') as f:
                report_content = f.read()
            risk_summary = self._parse_quality_report(report_content)
        else:
            app.logger.warning(f"Report file not found: {report_path}")
            # 尝试从命令行输出解析（兼容旧逻辑）
            risk_summary = self._parse_quality_output(output)
        
        app.logger.info(f"Parsed risk summary: {risk_summary}")
        
        # 保存结果到数据库
        result = QualityTestResult(
            task_id=task.id,
            execution_time=datetime.now(),
            command=cmd_str,
            output_file=output_file,
            status='success'
        )
        
        if risk_summary:
            result.infrastructure_recon = risk_summary.get('item_1')
            result.models_enumerated = risk_summary.get('item_2')
            result.token_injection = risk_summary.get('item_3')
            result.prompt_extraction = risk_summary.get('item_4')
            result.instruction_override = risk_summary.get('item_5')
            result.jailbreak_test = risk_summary.get('item_6')
            result.context_boundary = risk_summary.get('item_7')
            result.tool_call_substitution = risk_summary.get('item_8')
            result.error_response_leakage = risk_summary.get('item_9')
            result.stream_integrity = risk_summary.get('item_10')
            result.overall_rating = risk_summary.get('overall_rating')
            # 保存完整的 Risk Summary JSON
            result.risk_summary_json = json.dumps(risk_summary, ensure_ascii=False)
        
        # 保存报告文件路径
        if os.path.exists(report_path):
            result.report_file = report_path
        
        db.session.add(result)
        db.session.commit()
        
        app.logger.info(f"Quality test result saved: {result.id}")
        
        return result
    
    def _save_output_file(self, task, output, test_type, app):
        """保存输出文件"""
        # 创建输出目录
        output_dir = Path(app.config['UPLOAD_FOLDER']) / f"task_{task.id}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{test_type}_{timestamp}.txt"
        filepath = output_dir / filename
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(output)
        
        app.logger.info(f"Output saved to: {filepath}")
        
        return str(filepath)
    
    def _parse_perf_output(self, output):
        """解析 evalscope perf 输出"""
        # 匹配性能指标表格行的正则表达式
        pattern = re.compile(
            r'│\s*(\d+)\s*│\s*(\S+)\s*│\s*([\d.]+)\s*│\s*'
            r'([\d.]+)\s*│\s*([\d.]+)\s*│\s*'
            r'([\d.]+)\s*│\s*([\d.]+)\s*│\s*'
            r'([\d.]+)\s*│\s*([\d.]+)\s*│\s*'
            r'([\d.]+)\s*│\s*([\d.]+)%\s*│'
        )
        
        for line in output.split('\n'):
            match = pattern.search(line)
            if match:
                return {
                    'concurrency': int(match.group(1)),
                    'rate': match.group(2),
                    'rps': float(match.group(3)),
                    'avg_latency': float(match.group(4)),
                    'p99_latency': float(match.group(5)),
                    'avg_ttft': float(match.group(6)),
                    'p99_ttft': float(match.group(7)),
                    'avg_tpot': float(match.group(8)),
                    'p99_tpot': float(match.group(9)),
                    'gen_toks': float(match.group(10)),
                    'success_rate': float(match.group(11))
                }
        
        return None
    
    def _parse_quality_output(self, output):
        """解析 audit.py 输出"""
        risk_summary = {}
        
        # 解析 Risk Summary 部分
        patterns = {
            'infrastructure_recon': r'Infrastructure recon (\S+)',
            'models_enumerated': r'(\d+) models enumerated',
            'token_injection': r'No token injection detected',
            'extraction_attempts': r'All extraction attempts failed',
            'cat_test': r'Cat test passed',
            'context_boundary': r'Context boundary: ([^\n]+)',
            'tool_call_substitution': r'No tool-call package substitution detected',
            'error_response_leakage': r'Error response leaks ([^\(]+)',
            'stream_integrity': r'Stream integrity ([^\n]+)',
            'overall_rating': r'## (\d+)\. Overall Rating\s+### ([^\n]+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, output)
            if match:
                if key == 'overall_rating':
                    risk_summary[key] = match.group(2).strip()
                elif key == 'context_boundary':
                    risk_summary[key] = match.group(1).strip()
                elif key in ['infrastructure_recon', 'error_response_leakage', 'stream_integrity']:
                    risk_summary[key] = match.group(1).strip()
                elif key == 'models_enumerated':
                    risk_summary[key] = f"{match.group(1)} models"
                else:
                    risk_summary[key] = 'passed'
        
        return risk_summary
    
    def _parse_quality_report(self, report_content):
        """从报告文件中解析 Risk Summary"""
        risk_summary = {}
        
        # 提取 Risk Summary 部分
        risk_section_match = re.search(r'## Risk Summary\s*\n(.*?)(?=\n---|\n## \d)', report_content, re.DOTALL)
        if not risk_section_match:
            return risk_summary
        
        risk_section = risk_section_match.group(1)
        
        # 提取所有列表项（以 "- " 开头的行）
        items = re.findall(r'^-\s+(.+)$', risk_section, re.MULTILINE)
        
        # 将列表项存入 risk_summary（保留完整内容，包括图标）
        for i, item in enumerate(items):
            risk_summary[f'item_{i+1}'] = item.strip()
        
        # 同时提取总体评级
        rating_match = re.search(r'(🔴|🟡|🟢).*?(HIGH|MEDIUM|LOW|CRITICAL)', report_content, re.IGNORECASE)
        if rating_match:
            risk_summary['overall_rating'] = f"{rating_match.group(1)} {rating_match.group(2).upper()}"
        else:
            # 根据红色和黄色标记数量推断评级
            red_count = risk_section.count('🔴')
            yellow_count = risk_section.count('🟡')
            if red_count >= 2:
                risk_summary['overall_rating'] = '🔴 HIGH RISK'
            elif red_count == 1 or yellow_count >= 2:
                risk_summary['overall_rating'] = '🟡 MEDIUM RISK'
            else:
                risk_summary['overall_rating'] = '🟢 LOW RISK'
        
        return risk_summary
