"""
数据库模型定义
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model, UserMixin):
    """用户表"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Task(db.Model):
    """任务表"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    task_type = db.Column(db.String(50), nullable=False)  # 'perf_test' or 'quality_test'
    
    # 任务配置（JSON 格式）
    config = db.Column(db.Text, nullable=False)
    
    # 定时设置
    schedule_type = db.Column(db.String(20), default='manual')  # 'manual', 'cron', 'interval'
    cron_expression = db.Column(db.String(100))  # Cron 表达式
    interval_seconds = db.Column(db.Integer)  # 间隔秒数
    
    # 时间范围
    start_time = db.Column(db.DateTime)  # 开始时间
    end_time = db.Column(db.DateTime)  # 结束时间
    
    # 状态
    is_enabled = db.Column(db.Boolean, default=False)  # 是否启用
    status = db.Column(db.String(20), default='idle')  # 'idle', 'running', 'success', 'failed'
    last_run_time = db.Column(db.DateTime)  # 最后执行时间
    next_run_time = db.Column(db.DateTime)  # 下次执行时间
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联
    perf_results = db.relationship('PerfTestResult', backref='task', lazy='dynamic', 
                                   cascade='all, delete-orphan')
    quality_results = db.relationship('QualityTestResult', backref='task', lazy='dynamic',
                                      cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'task_type': self.task_type,
            'config': self.config,
            'schedule_type': self.schedule_type,
            'cron_expression': self.cron_expression,
            'interval_seconds': self.interval_seconds,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'is_enabled': self.is_enabled,
            'status': self.status,
            'last_run_time': self.last_run_time.isoformat() if self.last_run_time else None,
            'next_run_time': self.next_run_time.isoformat() if self.next_run_time else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class PerfTestResult(db.Model):
    """服务压力测试结果表"""
    __tablename__ = 'perf_test_results'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    
    # 执行信息
    execution_time = db.Column(db.DateTime, nullable=False)  # 执行时间
    command = db.Column(db.Text)  # 执行命令
    
    # 性能指标
    concurrency = db.Column(db.Integer)  # 并发数
    avg_latency = db.Column(db.Float)  # 平均延迟
    p99_latency = db.Column(db.Float)  # P99延迟
    avg_ttft = db.Column(db.Float)  # 平均首字延迟
    p99_ttft = db.Column(db.Float)  # P99首字延迟
    avg_tpot = db.Column(db.Float)  # 平均每token时间
    p99_tpot = db.Column(db.Float)  # P99每token时间
    rps = db.Column(db.Float)  # 每秒请求数
    gen_toks = db.Column(db.Float)  # 生成速度
    success_rate = db.Column(db.Float)  # 成功率
    
    # 文件路径
    output_file = db.Column(db.String(500))  # 原始输出文件路径
    
    # 状态
    status = db.Column(db.String(20), default='success')  # 'success', 'failed'
    error_message = db.Column(db.Text)  # 错误信息
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        # 从关联的 Task 获取任务名称和模型名称
        task_name = self.task.name if self.task else None
        model_name = None
        if self.task and self.task.config:
            try:
                import json
                config = json.loads(self.task.config)
                model_name = config.get('model')
            except:
                pass
        
        return {
            'id': self.id,
            'task_id': self.task_id,
            'task_name': task_name,
            'model_name': model_name,
            'execution_time': self.execution_time.isoformat(),
            'command': self.command,
            'concurrency': self.concurrency,
            'avg_latency': self.avg_latency,
            'p99_latency': self.p99_latency,
            'avg_ttft': self.avg_ttft,
            'p99_ttft': self.p99_ttft,
            'avg_tpot': self.avg_tpot,
            'p99_tpot': self.p99_tpot,
            'rps': self.rps,
            'gen_toks': self.gen_toks,
            'success_rate': self.success_rate,
            'output_file': self.output_file,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat()
        }


class QualityTestResult(db.Model):
    """模型质量测试结果表"""
    __tablename__ = 'quality_test_results'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    
    # 执行信息
    execution_time = db.Column(db.DateTime, nullable=False)  # 执行时间
    command = db.Column(db.Text)  # 执行命令
    
    # Risk Summary (10项检测)
    infrastructure_recon = db.Column(db.String(200))  # 1. 基础设施侦察
    models_enumerated = db.Column(db.String(200))  # 2. 模型列表枚举
    token_injection = db.Column(db.String(200))  # 3. Token 注入检测
    prompt_extraction = db.Column(db.String(200))  # 4. Prompt 提取
    instruction_override = db.Column(db.String(200))  # 5. 指令冲突 + 身份替换
    jailbreak_test = db.Column(db.String(200))  # 6. 越狱测试
    context_boundary = db.Column(db.String(200))  # 7. 上下文长度扫描
    tool_call_substitution = db.Column(db.String(200))  # 8. 工具调用改写
    error_response_leakage = db.Column(db.String(200))  # 9. 错误响应泄漏
    stream_integrity = db.Column(db.String(200))  # 10. 流完整性
    overall_rating = db.Column(db.String(50))  # 总体评级
    risk_summary_json = db.Column(db.Text)  # 完整的 Risk Summary JSON
    
    # 文件路径
    output_file = db.Column(db.String(500))  # 原始输出文件路径
    report_file = db.Column(db.String(500))  # 报告文件路径
    
    # 状态
    status = db.Column(db.String(20), default='success')  # 'success', 'failed'
    error_message = db.Column(db.Text)  # 错误信息
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        # 从关联的 Task 获取任务名称
        task_name = self.task.name if self.task else None
        
        return {
            'id': self.id,
            'task_id': self.task_id,
            'task_name': task_name,
            'execution_time': self.execution_time.isoformat(),
            'command': self.command,
            'infrastructure_recon': self.infrastructure_recon,
            'models_enumerated': self.models_enumerated,
            'token_injection': self.token_injection,
            'prompt_extraction': self.prompt_extraction,
            'instruction_override': self.instruction_override,
            'jailbreak_test': self.jailbreak_test,
            'context_boundary': self.context_boundary,
            'tool_call_substitution': self.tool_call_substitution,
            'error_response_leakage': self.error_response_leakage,
            'stream_integrity': self.stream_integrity,
            'overall_rating': self.overall_rating,
            'risk_summary_json': self.risk_summary_json,
            'output_file': self.output_file,
            'report_file': self.report_file,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat()
        }
