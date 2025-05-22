from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.db import get_db, with_db_retry
import sys
import logging

logger = logging.getLogger(__name__)

class User(UserMixin):
    def __init__(self, id, username, password, role):
        self.id = id
        self.username = username
        self.password = password  # 存储原始密码
        self.role = role
        self.is_decision_maker = role == 'decision_maker'
    
    @staticmethod
    @with_db_retry()
    def get_by_username(username):
        try:
            logger.info(f"尝试通过用户名获取用户: {username}")
            db = get_db()
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                user_data = cursor.fetchone()
                
                logger.debug(f"SQL查询结果: {user_data}")
                
                if user_data:
                    try:
                        user = User(
                            id=user_data['id'],
                            username=user_data['username'],
                            password=user_data['password'],  # 使用原始密码
                            role=user_data['role']
                        )
                        logger.info(f"用户对象创建成功: id={user.id}, username={user.username}, role={user.role}")
                        return user
                    except Exception as e:
                        logger.error(f"创建用户对象时出错: {str(e)}")
                        logger.error(traceback.format_exc())
                        return None
                
                logger.warning(f"未找到用户: {username}")
                return None
        except Exception as e:
            logger.error(f"获取用户时出错: {str(e)}")
            logger.error(traceback.format_exc())
            return None

    def get_id(self):
        """Flask-Login需要这个方法"""
        return str(self.id)

    def is_authenticated(self):
        """Flask-Login需要这个方法"""
        return True

    def is_active(self):
        """Flask-Login需要这个方法"""
        return True

    def is_anonymous(self):
        """Flask-Login需要这个方法"""
        return False
    
    @staticmethod
    @with_db_retry()
    def get_by_id(user_id):
        try:
            logger.info(f"尝试通过ID获取用户: {user_id}")
            db = get_db()
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                user_data = cursor.fetchone()
                
                if user_data:
                    logger.info(f"通过ID找到用户: {user_data['username']}")
                    return User(
                        id=user_data['id'],
                        username=user_data['username'],
                        password=user_data['password'],  # 使用原始密码
                        role=user_data['role']
                    )
                logger.warning(f"未找到ID为 {user_id} 的用户")
                return None
        except Exception as e:
            logger.error(f"通过ID获取用户时出错: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    @staticmethod
    @with_db_retry()
    def create(username, password, role='user'):
        try:
            logger.info(f"尝试创建新用户: {username}")
            db = get_db()
            with db.cursor() as cursor:
                query = """
                INSERT INTO users (username, password, role)
                VALUES (%s, %s, %s)
                """
                
                cursor.execute(query, (
                    username,
                    password,  # 直接存储原始密码
                    role
                ))
                
                db.commit()
                user_id = cursor.lastrowid
                logger.info(f"用户创建成功: id={user_id}, username={username}, role={role}")
                return user_id
        except Exception as e:
            logger.error(f"创建用户时出错: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def check_password(self, password):
        # 直接比较原始密码
        return self.password == password

    @staticmethod
    @with_db_retry()
    def get_all():
        try:
            logger.info("获取所有用户列表")
            db = get_db()
            with db.cursor() as cursor:
                cursor.execute('SELECT * FROM users')
                users = cursor.fetchall()
                logger.info(f"成功获取 {len(users)} 个用户")
                return [User(
                    id=user['id'],
                    username=user['username'],
                    password=user['password'],  # 使用原始密码
                    role=user['role']
                ) for user in users]
        except Exception as e:
            logger.error(f"获取用户列表时出错: {str(e)}")
            logger.error(traceback.format_exc())
            raise