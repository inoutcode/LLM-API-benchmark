#!/usr/bin/env python3
"""
API 测试脚本
用于验证后端 API 是否正常工作
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000/api"

def test_api():
    """测试 API 接口"""
    
    print("=" * 60)
    print("API 测试开始")
    print("=" * 60)
    
    # 1. 测试登录
    print("\n1. 测试登录...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        
        if response.status_code == 200:
            print("✅ 登录成功")
            token = response.cookies.get('session')
        else:
            print(f"❌ 登录失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return False
    
    # 2. 测试获取当前用户
    print("\n2. 测试获取当前用户...")
    try:
        response = requests.get(f"{BASE_URL}/auth/me", cookies={'session': token})
        
        if response.status_code == 200:
            user = response.json()['user']
            print(f"✅ 当前用户: {user['username']}")
        else:
            print(f"❌ 获取用户失败: {response.text}")
    except Exception as e:
        print(f"❌ 获取用户异常: {e}")
    
    # 3. 测试获取任务列表
    print("\n3. 测试获取任务列表...")
    try:
        response = requests.get(f"{BASE_URL}/tasks/", cookies={'session': token})
        
        if response.status_code == 200:
            tasks = response.json()['tasks']
            print(f"✅ 任务数量: {len(tasks)}")
        else:
            print(f"❌ 获取任务失败: {response.text}")
    except Exception as e:
        print(f"❌ 获取任务异常: {e}")
    
    # 4. 测试创建任务
    print("\n4. 测试创建任务...")
    task_data = {
        "name": "测试任务",
        "task_type": "perf_test",
        "config": json.dumps({
            "url": "https://test.example.com",
            "api_key": "test-key",
            "model": "test-model",
            "parallel": 8,
            "number": 50
        }),
        "schedule_type": "manual",
        "is_enabled": False
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/tasks/",
            json=task_data,
            cookies={'session': token}
        )
        
        if response.status_code == 201:
            task = response.json()['task']
            task_id = task['id']
            print(f"✅ 任务创建成功: ID={task_id}")
        else:
            print(f"❌ 创建任务失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 创建任务异常: {e}")
        return False
    
    # 5. 测试获取统计信息
    print("\n5. 测试获取统计信息...")
    try:
        response = requests.get(f"{BASE_URL}/results/statistics", cookies={'session': token})
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ 统计信息:")
            print(f"   - 总任务数: {stats['total_tasks']}")
            print(f"   - 启用任务: {stats['enabled_tasks']}")
            print(f"   - 运行中: {stats['running_tasks']}")
        else:
            print(f"❌ 获取统计失败: {response.text}")
    except Exception as e:
        print(f"❌ 获取统计异常: {e}")
    
    # 6. 测试删除任务
    print("\n6. 测试删除任务...")
    try:
        response = requests.delete(
            f"{BASE_URL}/tasks/{task_id}",
            cookies={'session': token}
        )
        
        if response.status_code == 200:
            print("✅ 任务删除成功")
        else:
            print(f"❌ 删除任务失败: {response.text}")
    except Exception as e:
        print(f"❌ 删除任务异常: {e}")
    
    # 7. 测试登出
    print("\n7. 测试登出...")
    try:
        response = requests.post(f"{BASE_URL}/auth/logout", cookies={'session': token})
        
        if response.status_code == 200:
            print("✅ 登出成功")
        else:
            print(f"❌ 登出失败: {response.text}")
    except Exception as e:
        print(f"❌ 登出异常: {e}")
    
    print("\n" + "=" * 60)
    print("API 测试完成")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    print("\n请确保应用已启动: python run.py")
    print("按 Enter 键开始测试...")
    input()
    
    success = test_api()
    
    if success:
        print("\n✅ 所有测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败")
        sys.exit(1)
