from flask import Flask, redirect, url_for
from flask_login import LoginManager
from config import DB_CONFIG
from app.utils.db import init_app as init_db
import logging
import sys

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['DB_CONFIG'] = DB_CONFIG
    
    # 初始化数据库连接
    init_db(app)
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),  # 输出到控制台
            logging.FileHandler('app.log', encoding='utf-8')  # 输出到文件
        ]
    )
    
    # 设置 Werkzeug 的日志级别
    logging.getLogger('werkzeug').setLevel(logging.INFO)
    
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    from app.routes.auth import auth_bp
    from app.routes.orders import orders_bp
    from app.routes.accounts import accounts_bp
    from app.routes.statistics import statistics_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(accounts_bp)
    app.register_blueprint(statistics_bp)
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.get_by_id(user_id)
    
    @app.route('/')
    def index():
        return redirect(url_for('orders.overview'))
    
    return app