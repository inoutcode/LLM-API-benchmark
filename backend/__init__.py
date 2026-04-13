"""
Flask 应用初始化
"""
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from datetime import timezone
import logging
import os

from .models import db, User
from .config import config


# 初始化扩展
login_manager = LoginManager()
scheduler = BackgroundScheduler()


def create_app(config_name='default'):
    """创建 Flask 应用"""
    app = Flask(__name__, 
                static_folder='../frontend/dist',
                static_url_path='',
                template_folder='../frontend/dist')
    
    # 加载配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 初始化扩展
    db.init_app(app)
    CORS(app, supports_credentials=True)
    login_manager.init_app(app)
    login_manager.session_protection = 'strong'
    
    # 配置日志
    setup_logging(app)
    
    # 初始化调度器
    init_scheduler(app)
    
    # 注册蓝图
    from .routes.auth import auth_bp
    from .routes.tasks import tasks_bp
    from .routes.results import results_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(results_bp, url_prefix='/api/results')
    
    # 创建数据库表和初始用户
    with app.app_context():
        db.create_all()
        create_initial_admin(app)
    
    # 前端路由处理（SPA）- 必须放在所有 API 路由之后
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        # 所有非 API 路由都返回 index.html（让 Vue Router 处理）
        try:
            return app.send_static_file('index.html')
        except:
            return app.send_static_file('index.html')
    
    # 404 错误处理 - 返回 index.html（SPA 路由）
    @app.errorhandler(404)
    def not_found(e):
        # 如果是 API 请求，返回 JSON 错误
        if hasattr(e, 'description') and 'api' in str(e.description):
            return {'error': 'Not found'}, 404
        # 否则返回 index.html（SPA 路由）
        return app.send_static_file('index.html')
    
    return app


def setup_logging(app):
    """配置日志"""
    if not app.debug:
        # 生产环境日志配置
        import logging
        from logging.handlers import RotatingFileHandler
        
        # 创建日志目录
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # 文件处理器
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'app.log'),
            maxBytes=10240000,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')


def init_scheduler(app):
    """初始化任务调度器"""
    # 如果调度器已经在运行，跳过配置
    if scheduler.running:
        return
    
    # 配置调度器
    jobstores = {
        'default': SQLAlchemyJobStore(url=app.config['SQLALCHEMY_DATABASE_URI'])
    }
    executors = {
        'default': ThreadPoolExecutor(5)
    }
    job_defaults = {
        'coalesce': True,
        'max_instances': 3
    }
    
    scheduler.configure(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
        timezone=timezone.utc
    )
    
    # 启动调度器
    scheduler.start()
    app.logger.info('Scheduler started')


def create_initial_admin(app):
    """创建初始管理员账号"""
    username = app.config['INIT_ADMIN_USERNAME']
    password = app.config['INIT_ADMIN_PASSWORD']
    
    # 检查是否已存在
    if not User.query.filter_by(username=username).first():
        admin = User(username=username)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        app.logger.info(f'Initial admin user created: {username}')


@login_manager.user_loader
def load_user(user_id):
    """加载用户"""
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    """未授权处理"""
    from flask import jsonify
    return jsonify({'error': 'Unauthorized', 'message': 'Please login first'}), 401
