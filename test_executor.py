"""
测试任务执行器
"""
import sys
import time
from backend.executor import TaskExecutor
from backend import create_app, db
from backend.models import Task

def test_executor():
    """测试任务执行"""
    app = create_app()
    
    with app.app_context():
        # 获取第一个任务
        task = Task.query.first()
        
        if not task:
            print("❌ 没有找到任务，请先创建一个任务")
            return
        
        print(f"📋 测试任务: {task.name} (ID: {task.id})")
        print(f"   类型: {task.task_type}")
        print(f"   配置: {task.config}")
        print()
        
        # 创建执行器
        executor = TaskExecutor()
        
        print("🚀 开始执行任务...")
        executor.execute_async(task)
        
        # 等待执行完成
        print("⏳ 等待执行完成...")
        time.sleep(5)
        
        # 检查结果
        db.session.refresh(task)
        print(f"\n📊 执行结果:")
        print(f"   状态: {task.status}")
        print(f"   最后执行时间: {task.last_run_time}")
        
        if task.task_type == 'perf_test':
            results = task.perf_results.all()
            print(f"   结果数量: {len(results)}")
            if results:
                result = results[-1]
                print(f"   最新结果 ID: {result.id}")
                print(f"   输出文件: {result.output_file}")
        else:
            results = task.quality_results.all()
            print(f"   结果数量: {len(results)}")
            if results:
                result = results[-1]
                print(f"   最新结果 ID: {result.id}")
                print(f"   输出文件: {result.output_file}")

if __name__ == '__main__':
    test_executor()
