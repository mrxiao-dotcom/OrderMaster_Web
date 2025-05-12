import pymysql
from flask import g, current_app
import time
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def get_db(max_retries=3, retry_delay=1):
    """
    获取数据库连接，带重试机制
    :param max_retries: 最大重试次数
    :param retry_delay: 重试间隔（秒）
    :return: 数据库连接
    """
    if 'db' not in g:
        retries = 0
        last_error = None
        
        while retries < max_retries:
            try:
                g.db = pymysql.connect(
                    host=current_app.config['DB_CONFIG']['host'],
                    user=current_app.config['DB_CONFIG']['user'],
                    password=current_app.config['DB_CONFIG']['password'],
                    database=current_app.config['DB_CONFIG']['database'],
                    port=current_app.config['DB_CONFIG']['port'],
                    connect_timeout=5,  # 设置连接超时时间
                    cursorclass=pymysql.cursors.DictCursor
                )
                logger.info(f"数据库连接成功: {current_app.config['DB_CONFIG']['host']}")
                return g.db
            except Exception as e:
                last_error = e
                retries += 1
                logger.error(f"数据库连接失败 (尝试 {retries}/{max_retries}): {str(e)}")
                if retries < max_retries:
                    time.sleep(retry_delay)
        
        # 如果所有重试都失败了，记录错误并抛出异常
        logger.error(f"数据库连接最终失败: {str(last_error)}")
        raise last_error
    
    return g.db

def close_db(e=None):
    """
    关闭数据库连接
    """
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
            logger.info("数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接时出错: {str(e)}")

def with_db_retry(max_retries=3, retry_delay=1):
    """
    数据库操作重试装饰器
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            last_error = None
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except pymysql.OperationalError as e:
                    last_error = e
                    retries += 1
                    logger.error(f"数据库操作失败 (尝试 {retries}/{max_retries}): {str(e)}")
                    if retries < max_retries:
                        time.sleep(retry_delay)
                        # 尝试重新连接
                        try:
                            close_db()
                        except:
                            pass
                        get_db()
            
            logger.error(f"数据库操作最终失败: {str(last_error)}")
            raise last_error
        return wrapper
    return decorator

def init_app(app):
    """
    初始化数据库连接
    """
    app.teardown_appcontext(close_db)
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )