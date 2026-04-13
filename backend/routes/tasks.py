"""
任务管理路由
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required
from datetime import datetime
import json
from ..models import db, Task
from ..executor import TaskExecutor
from .. import scheduler


tasks_bp = Blueprint('tasks', __name__)
executor = TaskExecutor()


@tasks_bp.route('/', methods=['GET'])
@login_required
def get_tasks():
    """获取所有任务"""
    task_type = request.args.get('type')
    status = request.args.get('status')
    model = request.args.get('model')  # 添加模型名称筛选
    
    query = Task.query
    
    if task_type:
        query = query.filter_by(task_type=task_type)
    if status:
        query = query.filter_by(status=status)
    
    # 按模型名称筛选
    if model:
        query = query.filter(Task.config.contains(f'"model": "{model}"'))
    
    tasks = query.order_by(Task.created_at.desc()).all()
    
    return jsonify({
        'tasks': [task.to_dict() for task in tasks]
    }), 200


@tasks_bp.route('/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    """获取单个任务详情"""
    task = Task.query.get_or_404(task_id)
    return jsonify({'task': task.to_dict()}), 200


@tasks_bp.route('/', methods=['POST'])
@login_required
def create_task():
    """创建新任务"""
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['name', 'task_type', 'config']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # 验证任务类型
    if data['task_type'] not in ['perf_test', 'quality_test']:
        return jsonify({'error': 'Invalid task_type, must be perf_test or quality_test'}), 400
    
    # 验证配置
    try:
        config = json.loads(data['config']) if isinstance(data['config'], str) else data['config']
    except Exception as e:
        return jsonify({'error': f'Invalid config JSON: {str(e)}'}), 400
    
    # 创建任务
    task = Task(
        name=data['name'],
        task_type=data['task_type'],
        config=json.dumps(config),
        schedule_type=data.get('schedule_type', 'manual'),
        cron_expression=data.get('cron_expression'),
        interval_seconds=data.get('interval_seconds'),
        is_enabled=data.get('is_enabled', False)
    )
    
    # 处理时间字段
    if data.get('start_time'):
        task.start_time = datetime.fromisoformat(data['start_time'])
    if data.get('end_time'):
        task.end_time = datetime.fromisoformat(data['end_time'])
    
    db.session.add(task)
    db.session.commit()
    
    # 如果启用且有定时设置，添加到调度器
    if task.is_enabled and task.schedule_type != 'manual':
        schedule_task(task)
    
    return jsonify({
        'message': 'Task created successfully',
        'task': task.to_dict()
    }), 201


@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    """更新任务"""
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    
    # 更新字段
    if 'name' in data:
        task.name = data['name']
    
    if 'config' in data:
        try:
            config = json.loads(data['config']) if isinstance(data['config'], str) else data['config']
            task.config = json.dumps(config)
        except Exception as e:
            return jsonify({'error': f'Invalid config JSON: {str(e)}'}), 400
    
    if 'schedule_type' in data:
        task.schedule_type = data['schedule_type']
    
    if 'cron_expression' in data:
        task.cron_expression = data['cron_expression']
    
    if 'interval_seconds' in data:
        task.interval_seconds = data['interval_seconds']
    
    if 'start_time' in data:
        task.start_time = datetime.fromisoformat(data['start_time']) if data['start_time'] else None
    
    if 'end_time' in data:
        task.end_time = datetime.fromisoformat(data['end_time']) if data['end_time'] else None
    
    was_enabled = task.is_enabled
    if 'is_enabled' in data:
        task.is_enabled = data['is_enabled']
    
    db.session.commit()
    
    # 更新调度
    if was_enabled and not task.is_enabled:
        # 从调度器移除
        unschedule_task(task)
    elif task.is_enabled and task.schedule_type != 'manual':
        # 添加或更新调度
        schedule_task(task)
    
    return jsonify({
        'message': 'Task updated successfully',
        'task': task.to_dict()
    }), 200


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    """删除任务"""
    task = Task.query.get_or_404(task_id)
    
    # 从调度器移除
    unschedule_task(task)
    
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'message': 'Task deleted successfully'}), 200


@tasks_bp.route('/<int:task_id>/run', methods=['POST'])
@login_required
def run_task(task_id):
    """立即执行任务"""
    task = Task.query.get_or_404(task_id)
    
    if task.status == 'running':
        return jsonify({'error': 'Task is already running'}), 400
    
    # 异步执行任务
    executor.execute_async(task)
    
    return jsonify({'message': 'Task started successfully'}), 200


@tasks_bp.route('/<int:task_id>/output-file', methods=['GET'])
@login_required
def get_task_output_file(task_id):
    """获取正在执行任务的输出文件路径"""
    from pathlib import Path
    from flask import current_app
    
    task = Task.query.get_or_404(task_id)
    
    # 只有 running 状态的任务才返回输出文件
    if task.status != 'running':
        return jsonify({'error': 'Task is not running'}), 400
    
    # 查找最新的输出文件
    output_dir = Path(current_app.config['UPLOAD_FOLDER']) / f"task_{task_id}"
    if not output_dir.exists():
        return jsonify({'error': 'Output directory not found'}), 404
    
    # 根据任务类型查找文件
    prefix = 'perf_' if task.task_type == 'perf_test' else 'quality_'
    files = sorted(output_dir.glob(f"{prefix}*.txt"), reverse=True)
    
    if not files:
        return jsonify({'error': 'No output file found'}), 404
    
    return jsonify({'output_file': str(files[0])}), 200


@tasks_bp.route('/<int:task_id>/output-content', methods=['GET'])
@login_required
def get_task_output_content(task_id):
    """获取正在执行任务的输出内容（支持实时读取）"""
    from pathlib import Path
    from flask import current_app
    
    task = Task.query.get_or_404(task_id)
    
    # 查找最新的输出文件
    output_dir = Path(current_app.config['UPLOAD_FOLDER']) / f"task_{task_id}"
    if not output_dir.exists():
        return jsonify({'content': '', 'exists': False}), 200
    
    # 根据任务类型查找文件
    prefix = 'perf_' if task.task_type == 'perf_test' else 'quality_'
    files = sorted(output_dir.glob(f"{prefix}*.txt"), reverse=True)
    
    if not files:
        return jsonify({'content': '', 'exists': False}), 200
    
    try:
        with open(files[0], 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({'content': content, 'exists': True, 'file': str(files[0])}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tasks_bp.route('/<int:task_id>/stop', methods=['POST'])
@login_required
def stop_task(task_id):
    """停止任务"""
    task = Task.query.get_or_404(task_id)
    
    if task.status != 'running':
        return jsonify({'error': 'Task is not running'}), 400
    
    # 停止任务
    executor.stop(task)
    
    return jsonify({'message': 'Task stopped successfully'}), 200


def schedule_task(task):
    """将任务添加到调度器"""
    job_id = f'task_{task.id}'
    
    # 先移除旧的调度
    unschedule_task(task)
    
    if task.schedule_type == 'cron' and task.cron_expression:
        # Cron 调度
        job = scheduler.add_job(
            run_scheduled_task,
            'cron',
            id=job_id,
            args=[task.id],
            **parse_cron_expression(task.cron_expression),
            replace_existing=True
        )
        # 更新下次执行时间 - 直接存储本地时间
        task.next_run_time = job.next_run_time.replace(tzinfo=None) if job.next_run_time.tzinfo else job.next_run_time
        db.session.commit()
    elif task.schedule_type == 'interval' and task.interval_seconds:
        # 间隔调度 - 立即执行第一次
        from datetime import datetime
        job = scheduler.add_job(
            run_scheduled_task,
            'interval',
            id=job_id,
            args=[task.id],
            seconds=task.interval_seconds,
            replace_existing=True,
            next_run_time=datetime.now()  # 立即执行第一次
        )
        # 更新下次执行时间 - 直接存储本地时间
        task.next_run_time = job.next_run_time.replace(tzinfo=None) if job.next_run_time.tzinfo else job.next_run_time
        db.session.commit()


def run_scheduled_task(task_id):
    """执行调度任务（独立函数，可被序列化）"""
    from .. import create_app
    
    app = create_app()
    with app.app_context():
        task = Task.query.get(task_id)
        if task and task.is_enabled:
            executor.execute_async(task)


def unschedule_task(task):
    """从调度器移除任务"""
    job_id = f'task_{task.id}'
    
    try:
        scheduler.remove_job(job_id)
    except Exception:
        pass  # 任务可能不存在


def parse_cron_expression(cron_expr):
    """解析 Cron 表达式"""
    # 简单实现，支持标准 cron 格式：分 时 日 月 周
    parts = cron_expr.split()
    
    if len(parts) == 5:
        return {
            'minute': parts[0],
            'hour': parts[1],
            'day': parts[2],
            'month': parts[3],
            'day_of_week': parts[4]
        }
    
    return {}