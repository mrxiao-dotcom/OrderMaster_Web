from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.db import get_db, with_db_retry
import sys

class User(UserMixin):
    def __init__(self, id, username, password, role):
        self.id = id
        self.username = username
        self.password = password  # 存储原始密码
        self.password_hash = generate_password_hash(password)  # 生成密码哈希
        self.role = role
        self.is_decision_maker = role == 'decision_maker'
    
    @staticmethod
    @with_db_retry()
    def get_by_username(username):
        try:
            print(f"尝试通过用户名获取用户: {username}", file=sys.stderr)
            db = get_db()
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                user_data = cursor.fetchone()
                
                print(f"SQL查询结果: {user_data}", file=sys.stderr)
                
                if user_data:
                    try:
                        user = User(
                            id=user_data['id'],
                            username=user_data['username'],
                            password=user_data['password'],  # 使用原始密码字段
                            role=user_data['role']
                        )
                        print(f"用户对象创建成功: id={user.id}, username={user.username}, role={user.role}", file=sys.stderr)
                        return user
                    except Exception as e:
                        print(f"创建用户对象时出错: {str(e)}", file=sys.stderr)
                        import traceback
                        print(traceback.format_exc(), file=sys.stderr)
                        return None
                
                print(f"未找到用户: {username}", file=sys.stderr)
                return None
        except Exception as e:
            print(f"获取用户时出错: {str(e)}", file=sys.stderr)
            import traceback
            print(traceback.format_exc(), file=sys.stderr)
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
            print(f"尝试通过ID获取用户: {user_id}", file=sys.stderr)
            db = get_db()
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                user_data = cursor.fetchone()
                
                if user_data:
                    print(f"通过ID找到用户: {user_data['username']}", file=sys.stderr)
                    return User(
                        id=user_data['id'],
                        username=user_data['username'],
                        password=user_data['password'],  # 使用原始密码字段
                        role=user_data['role']
                    )
                return None
        except Exception as e:
            print(f"通过ID获取用户时出错: {str(e)}", file=sys.stderr)
            import traceback
            print(traceback.format_exc(), file=sys.stderr)
            return None
    
    @staticmethod
    @with_db_retry()
    def create(username, password, role='user'):
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
            return user_id

    def check_password(self, password):
        # 直接比较原始密码
        return self.password == password

    @staticmethod
    @with_db_retry()
    def get_all():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute('SELECT * FROM users')
            users = cursor.fetchall()
            return [User(
                id=user['id'],
                username=user['username'],
                password=user['password'],  # 使用原始密码字段
                role=user['role']
            ) for user in users]