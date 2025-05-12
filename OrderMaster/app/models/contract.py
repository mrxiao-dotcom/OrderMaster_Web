from app.utils.db import get_db

class Contract:
    @staticmethod
    def get_active_contracts():
        db = get_db()
        cursor = db.cursor()
        
        query = """
        SELECT DISTINCT c.*, 
               (SELECT COUNT(*) FROM orders o WHERE o.contract_id = c.id AND o.status = 'executed') as active_orders_count,
               (SELECT COUNT(*) FROM orders o WHERE o.contract_id = c.id AND o.status != 'pending') as non_pending_count
        FROM contracts c
        JOIN orders o ON c.id = o.contract_id
        WHERE o.status IN ('pending', 'executed')
        ORDER BY c.created_at DESC
        """
        
        cursor.execute(query)
        contracts = cursor.fetchall()
        
        # 获取每个合约的订单信息
        for contract in contracts:
            order_query = """
            SELECT o.*, a.account_name, a.account_type
            FROM orders o
            JOIN accounts a ON o.account_id = a.id
            WHERE o.contract_id = %s
            ORDER BY o.created_at DESC
            """
            cursor.execute(order_query, (contract['id'],))
            contract['orders'] = cursor.fetchall()
            # 设置can_edit属性：只有当所有订单都是pending状态时才能编辑
            contract['can_edit'] = contract['non_pending_count'] == 0
        
        cursor.close()
        return contracts
    
    @staticmethod
    def get_exited_contracts():
        db = get_db()
        cursor = db.cursor()
        
        query = """
        SELECT c.*
        FROM contracts c
        WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.contract_id = c.id AND o.status != 'exited')
        AND EXISTS (SELECT 1 FROM orders o WHERE o.contract_id = c.id)
        ORDER BY c.created_at DESC
        """
        
        cursor.execute(query)
        contracts = cursor.fetchall()
        cursor.close()
        
        return contracts
    
    @staticmethod
    def get_by_id(contract_id):
        db = get_db()
        cursor = db.cursor()
        
        query = "SELECT * FROM contracts WHERE id = %s"
        cursor.execute(query, (contract_id,))
        contract = cursor.fetchone()
        cursor.close()
        
        return contract
    
    @staticmethod
    def create(contract_data):
        db = get_db()
        cursor = db.cursor()
        
        query = """
        INSERT INTO contracts (
            contract_name, period, stop_loss_amount, bollinger_period, created_by,
            entry_time, period_upgrade_time, ma_price, price, actual_entry_price, stop_loss_price
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            contract_data['contract_name'],
            contract_data['period'],
            contract_data['stop_loss_amount'],
            contract_data['bollinger_period'],
            contract_data['created_by'],
            contract_data.get('entry_time'),
            contract_data.get('period_upgrade_time'),
            contract_data.get('ma_price'),
            contract_data.get('price'),  # 使用单个价格字段替代最高价和最低价
            contract_data.get('actual_entry_price'),
            contract_data.get('stop_loss_price')
        ))
        
        contract_id = cursor.lastrowid
        db.commit()
        cursor.close()
        
        return contract_id
    
    @staticmethod
    def update(contract_id, contract_data):
        db = get_db()
        cursor = db.cursor()
        
        query = """
        UPDATE contracts
        SET contract_name = %s,
            period = %s,
            stop_loss_amount = %s,
            bollinger_period = %s,
            entry_time = %s,
            period_upgrade_time = %s,
            ma_price = %s,
            price = %s,
            actual_entry_price = %s,
            stop_loss_price = %s
        WHERE id = %s
        """
        
        cursor.execute(query, (
            contract_data['contract_name'],
            contract_data['period'],
            contract_data['stop_loss_amount'],
            contract_data['bollinger_period'],
            contract_data.get('entry_time'),
            contract_data.get('period_upgrade_time'),
            contract_data.get('ma_price'),
            contract_data.get('price'),  # 使用单个价格字段替代最高价和最低价
            contract_data.get('actual_entry_price'),
            contract_data.get('stop_loss_price'),
            contract_id
        ))
        
        db.commit()
        cursor.close()