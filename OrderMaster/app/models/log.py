from app.utils.db import get_db
from flask import request
from flask_login import current_user
import json

class OperationLog:
    @staticmethod
    def log_operation(operation_type, target_table, target_id=None, details=None):
        """
        记录用户操作
        
        参数:
            operation_type: 操作类型 (如 'login', 'create', 'update', 'delete', 'execute', 'exit')
            target_table: 目标表 (如 'users', 'contracts', 'orders', 'accounts')
            target_id: 目标记录ID
            details: 操作详情 (可以是字典或字符串)
        """
        db = get_db()
        cursor = db.cursor()
        
        # 如果用户已登录，获取用户ID，否则设为NULL
        user_id = current_user.id if hasattr(current_user, 'id') else None
        
        # 获取客户端IP地址
        ip_address = request.remote_addr
        
        # 如果details是字典，转换为JSON字符串
        if isinstance(details, dict):
            details = json.dumps(details, ensure_ascii=False)
        
        query = """
        INSERT INTO operation_logs 
        (user_id, operation_type, target_table, target_id, details, ip_address)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            user_id,
            operation_type,
            target_table,
            target_id,
            details,
            ip_address
        ))
        
        db.commit()
        cursor.close()
    
    @staticmethod
    def get_logs(filters=None, limit=100, offset=0):
        """
        获取操作日志
        
        参数:
            filters: 过滤条件字典
            limit: 限制返回记录数
            offset: 偏移量
        """
        db = get_db()
        cursor = db.cursor()
        
        query = """
        SELECT l.*, u.username 
        FROM operation_logs l
        LEFT JOIN users u ON l.user_id = u.id
        """
        
        params = []
        
        # 添加过滤条件
        if filters:
            conditions = []
            for key, value in filters.items():
                if key == 'user_id' and value:
                    conditions.append("l.user_id = %s")
                    params.append(value)
                elif key == 'operation_type' and value:
                    conditions.append("l.operation_type = %s")
                    params.append(value)
                elif key == 'target_table' and value:
                    conditions.append("l.target_table = %s")
                    params.append(value)
                elif key == 'date_from' and value:
                    conditions.append("l.created_at >= %s")
                    params.append(value)
                elif key == 'date_to' and value:
                    conditions.append("l.created_at <= %s")
                    params.append(value)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        # 添加排序和分页
        query += " ORDER BY l.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        logs = cursor.fetchall()
        cursor.close()
        
        return logs