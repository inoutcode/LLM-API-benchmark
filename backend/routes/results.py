"""
测试结果路由
"""
from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required
from datetime import datetime, timezone
from ..models import db, Task, PerfTestResult, QualityTestResult
import os


results_bp = Blueprint('results', __name__)


def parse_time_param(time_str):
    """
    解析时间参数，支持多种格式：
    - ISO 8601 格式（带或不带时区）：'2026-04-13T08:31:16Z' 或 '2026-04-13T08:31:16'
    - Unix timestamp（秒）：'1744525876'
    - Unix timestamp（毫秒）：'1744525876000'
    
    返回 naive datetime（无时区信息），以便与数据库时间比较
    """
    if not time_str:
        return None
    
    # 尝试解析为数字（timestamp）
    try:
        timestamp = float(time_str)
        # 判断是秒还是毫秒（毫秒时间戳通常大于 1e12）
        if timestamp > 1e12:
            timestamp = timestamp / 1000
        # 从 timestamp 创建 naive datetime（假设为本地时间）
        return datetime.fromtimestamp(timestamp)
    except ValueError:
        pass
    
    # 尝试解析为 ISO 8601 格式
    try:
        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        # 如果有时区信息，转换为本地时间并去掉时区
        if dt.tzinfo is not None:
            dt = dt.astimezone().replace(tzinfo=None)
        return dt
    except ValueError:
        pass
    
    # 尝试解析为普通日期时间字符串
    try:
        return datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        pass
    
    return None


@results_bp.route('/perf', methods=['GET'])
@login_required
def get_perf_results():
    """获取服务压力测试结果"""
    task_id = request.args.get('task_id', type=int)
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    model = request.args.get('model')  # 添加模型名称参数
    limit = request.args.get('limit', 100, type=int)
    
    query = PerfTestResult.query
    
    if task_id:
        query = query.filter_by(task_id=task_id)
    
    # 按模型名称筛选（通过关联的 Task 表）
    if model:
        query = query.join(Task).filter(Task.config.contains(f'"model": "{model}"'))
    
    if start_time:
        parsed_start = parse_time_param(start_time)
        if parsed_start:
            query = query.filter(PerfTestResult.execution_time >= parsed_start)
    
    if end_time:
        parsed_end = parse_time_param(end_time)
        if parsed_end:
            query = query.filter(PerfTestResult.execution_time <= parsed_end)
    
    results = query.order_by(PerfTestResult.execution_time.desc()).limit(limit).all()
    
    return jsonify({
        'results': [result.to_dict() for result in results]
    }), 200


@results_bp.route('/perf/models', methods=['GET'])
@login_required
def get_perf_models():
    """获取所有压力测试任务的模型名称列表"""
    import json
    
    # 查询所有压力测试任务的配置
    tasks = Task.query.filter_by(task_type='perf_test').all()
    
    models = set()
    for task in tasks:
        try:
            config = json.loads(task.config)
            if 'model' in config:
                models.add(config['model'])
        except:
            pass
    
    return jsonify({
        'models': sorted(list(models))
    }), 200


@results_bp.route('/perf/<int:result_id>', methods=['GET'])
@login_required
def get_perf_result(result_id):
    """获取单个服务压力测试结果"""
    result = PerfTestResult.query.get_or_404(result_id)
    return jsonify({'result': result.to_dict()}), 200


@results_bp.route('/perf/<int:result_id>/file', methods=['GET'])
@login_required
def get_perf_result_file(result_id):
    """获取服务压力测试结果文件"""
    result = PerfTestResult.query.get_or_404(result_id)
    
    if not result.output_file or not os.path.exists(result.output_file):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(result.output_file, as_attachment=True)


@results_bp.route('/perf/<int:result_id>/content', methods=['GET'])
@login_required
def get_perf_result_content(result_id):
    """获取服务压力测试结果文件内容"""
    result = PerfTestResult.query.get_or_404(result_id)
    
    if not result.output_file or not os.path.exists(result.output_file):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        with open(result.output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({'content': content}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to read file: {str(e)}'}), 500


@results_bp.route('/perf/chart-data', methods=['GET'])
@login_required
def get_perf_chart_data():
    """获取服务压力测试图表数据"""
    task_id = request.args.get('task_id', type=int)
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    model = request.args.get('model')  # 添加模型名称参数
    
    query = PerfTestResult.query.filter_by(status='success')
    
    if task_id:
        query = query.filter_by(task_id=task_id)
    
    # 按模型名称筛选（通过关联的 Task 表）
    if model:
        query = query.join(Task).filter(Task.config.contains(f'"model": "{model}"'))
    
    if start_time:
        parsed_start = parse_time_param(start_time)
        if parsed_start:
            query = query.filter(PerfTestResult.execution_time >= parsed_start)
    
    if end_time:
        parsed_end = parse_time_param(end_time)
        if parsed_end:
            query = query.filter(PerfTestResult.execution_time <= parsed_end)
    
    results = query.order_by(PerfTestResult.execution_time.asc()).all()
    
    # 构建图表数据
    chart_data = {
        'labels': [r.execution_time.strftime('%Y-%m-%d %H:%M') for r in results],
        'datasets': {
            'avg_latency': [r.avg_latency for r in results],
            'p99_latency': [r.p99_latency for r in results],
            'avg_ttft': [r.avg_ttft for r in results],
            'p99_ttft': [r.p99_ttft for r in results],
            'avg_tpot': [r.avg_tpot for r in results],
            'p99_tpot': [r.p99_tpot for r in results],
            'rps': [r.rps for r in results],
            'gen_toks': [r.gen_toks for r in results],
            'success_rate': [r.success_rate for r in results]
        }
    }
    
    return jsonify({'chart_data': chart_data}), 200


@results_bp.route('/quality', methods=['GET'])
@login_required
def get_quality_results():
    """获取模型质量测试结果"""
    task_id = request.args.get('task_id', type=int)
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    limit = request.args.get('limit', 100, type=int)
    
    query = QualityTestResult.query
    
    if task_id:
        query = query.filter_by(task_id=task_id)
    
    if start_time:
        parsed_start = parse_time_param(start_time)
        if parsed_start:
            query = query.filter(QualityTestResult.execution_time >= parsed_start)
    
    if end_time:
        parsed_end = parse_time_param(end_time)
        if parsed_end:
            query = query.filter(QualityTestResult.execution_time <= parsed_end)
    
    results = query.order_by(QualityTestResult.execution_time.desc()).limit(limit).all()
    
    return jsonify({
        'results': [result.to_dict() for result in results]
    }), 200


@results_bp.route('/quality/<int:result_id>', methods=['GET'])
@login_required
def get_quality_result(result_id):
    """获取单个模型质量测试结果"""
    result = QualityTestResult.query.get_or_404(result_id)
    return jsonify({'result': result.to_dict()}), 200


@results_bp.route('/quality/<int:result_id>/file', methods=['GET'])
@login_required
def get_quality_result_file(result_id):
    """获取模型质量测试结果文件"""
    result = QualityTestResult.query.get_or_404(result_id)
    
    if not result.output_file or not os.path.exists(result.output_file):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(result.output_file, as_attachment=True)


@results_bp.route('/quality/<int:result_id>/raw', methods=['GET'])
@login_required
def get_quality_result_raw(result_id):
    """获取模型质量测试原始报告内容"""
    result = QualityTestResult.query.get_or_404(result_id)
    
    if not result.output_file or not os.path.exists(result.output_file):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        with open(result.output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            'content': content,
            'filename': os.path.basename(result.output_file)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@results_bp.route('/statistics', methods=['GET'])
@login_required
def get_statistics():
    """获取统计信息"""
    total_tasks = Task.query.count()
    enabled_tasks = Task.query.filter_by(is_enabled=True).count()
    running_tasks = Task.query.filter_by(status='running').count()
    
    total_perf_results = PerfTestResult.query.count()
    total_quality_results = QualityTestResult.query.count()
    
    return jsonify({
        'total_tasks': total_tasks,
        'enabled_tasks': enabled_tasks,
        'running_tasks': running_tasks,
        'total_perf_results': total_perf_results,
        'total_quality_results': total_quality_results
    }), 200