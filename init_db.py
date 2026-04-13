#!/usr/bin/env python3
"""
数据库初始化脚本
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend import create_app, db
from backend.models import User

def init_database():
    """初始化数据库"""
    app = create_app('development')
    
    with app.app_context():
        # 创建所有表
        print("创建数据库表...")
        db.create_all()
        
        # 检查是否需要创建初始管理员
        username = app.config['INIT_ADMIN_USERNAME']
        if not User.query.filter_by(username=username).first():
            print(f"创建初始管理员账号: {username}")
            admin = User(username=username)
            admin.set_password(app.config['INIT_ADMIN_PASSWORD'])
            db.session.add(admin)
            db.session.commit()
            print(f"✅ 管理员账号创建成功")
        else:
            print(f"ℹ️  管理员账号已存在: {username}")
        
        print("\n✅ 数据库初始化完成！")


if __name__ == '__main__':
    init_database()
