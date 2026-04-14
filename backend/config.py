"""
配置文件
"""
import os
from datetime import timedelta


class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 数据库配置
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'password'
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'model_test_db'
    
    # 使用 SQLite 作为默认数据库（开发环境）
    USE_SQLITE = os.environ.get('USE_SQLITE', 'true').lower() == 'true'
    
    if USE_SQLITE:
        basedir = os.path.abspath(os.path.dirname(__file__))
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '..', 'app.db')
    else:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@"
            f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # 生产环境设为 False
    
    # Session 配置
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 文件存储路径
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'outputs')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    
    # 任务执行配置
    TASK_TIMEOUT = 3600  # 任务超时时间（秒）
    MAX_CONCURRENT_TASKS = 5  # 最大并发任务数
    
    # 模拟模式（用于测试，不执行真实命令）
    USE_MOCK_EVALSCOPE = os.environ.get('USE_MOCK_EVALSCOPE', 'false').lower() == 'true'
    
    # 初始管理员账号（首次启动时创建）
    INIT_ADMIN_USERNAME = os.environ.get('INIT_ADMIN_USERNAME') or 'admin'
    INIT_ADMIN_PASSWORD = os.environ.get('INIT_ADMIN_PASSWORD') or 'admin123'
    
    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        # 创建必要的目录
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = False  # 关闭 SQL 日志，避免日志过多


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    
    # 生产环境必须设置 SECRET_KEY
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # 确保设置了 SECRET_KEY
        assert os.environ.get('SECRET_KEY'), 'SECRET_KEY must be set in production!'


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
