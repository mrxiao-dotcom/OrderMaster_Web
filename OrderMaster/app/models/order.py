from app.utils.db import get_db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Order:
    @staticmethod
    def get_by_id(order_id):
        db = get_db()
        cursor = db.cursor()
        
        query = """
        SELECT o.*, c.contract_name, a.account_name 
        FROM orders o
        JOIN contracts c ON o.contract_id = c.id
        JOIN accounts a ON o.account_id = a.id
        WHERE o.id = %s
        """
        cursor.execute(query, (order_id,))
        order = cursor.fetchone()
        cursor.close()
        
        return order
    
    @staticmethod
    def get_by_contract(contract_id):
        db = get_db()
        cursor = db.cursor()
        logger.info(f"获取合约 {contract_id} 的订单数据")
        
        # 简化查询，只取每个账户最新的一条订单
        query = """
        SELECT o.*, a.account_name, a.account_type
        FROM orders o
        JOIN accounts a ON o.account_id = a.id
        WHERE o.contract_id = %s
        AND o.id IN (
            SELECT MAX(id) FROM orders 
            WHERE contract_id = %s 
            GROUP BY account_id
        )
        ORDER BY o.account_id
        """
        
        try:
            cursor.execute(query, (contract_id, contract_id))
            orders = cursor.fetchall()
            logger.info(f"查询到 {len(orders)} 条订单")
            
            # 调试输出所有订单ID和账户ID
            for order in orders:
                logger.debug(f"订单ID:{order['id']}, 账户ID:{order['account_id']}, 账户名:{order['account_name']}")
                
            return orders
        except Exception as e:
            logger.error(f"获取合约订单时出错: {str(e)}")
            return []
        finally:
            cursor.close()
    
    @staticmethod
    def create(order_data):
        db = get_db()
        cursor = db.cursor()
        
        query = """
        INSERT INTO orders (contract_id, account_id, status)
        VALUES (%s, %s, %s)
        """
        
        cursor.execute(query, (
            order_data['contract_id'],
            order_data['account_id'],
            order_data['status']
        ))
        
        order_id = cursor.lastrowid
        db.commit()
        cursor.close()
        
        return order_id
    
    @staticmethod
    def execute(order_id, executed_by):
        db = get_db()
        cursor = db.cursor()
        
        now = datetime.now()
        
        query = """
        UPDATE orders
        SET status = 'executed', entry_time = %s, executed_by = %s
        WHERE id = %s
        """
        
        cursor.execute(query, (now, executed_by, order_id))
        db.commit()
        cursor.close()
    
    @staticmethod
    def exit(order_id, exit_price, executed_by):
        db = get_db()
        cursor = db.cursor()
        
        now = datetime.now()
        
        query = """
        UPDATE orders
        SET status = 'exited', exit_time = %s, exit_price = %s
        WHERE id = %s
        """
        
        cursor.execute(query, (now, exit_price, order_id))
        db.commit()
        cursor.close()
    
    @staticmethod
    def all_pending_by_contract(contract_id):
        db = get_db()
        cursor = db.cursor()
        
        query = """
        SELECT COUNT(*) as count
        FROM orders
        WHERE contract_id = %s AND status != 'pending'
        """
        
        cursor.execute(query, (contract_id,))
        result = cursor.fetchone()
        cursor.close()
        
        # 如果没有非pending状态的订单，返回True
        return result['count'] == 0
    
    @staticmethod
    def delete(order_id):
        db = get_db()
        cursor = db.cursor()
        
        query = "DELETE FROM orders WHERE id = %s"
        cursor.execute(query, (order_id,))
        
        db.commit()
        cursor.close()

    @staticmethod
    def get_active_contracts():
        logger.info("开始获取活跃合约列表")
        db = get_db()
        cursor = db.cursor()
        try:
            sql = """
            SELECT * FROM contracts
            WHERE exit_time IS NULL
            ORDER BY created_at DESC
            """
            cursor.execute(sql)
            contracts = cursor.fetchall()
            logger.info(f"查询到的合约数量: {len(contracts)}")
            for contract in contracts:
                contract['orders'] = Order.get_by_contract(contract['id'])
                account_names = [order['account_name'] for order in contract['orders']]
                contract['associated_accounts'] = ', '.join(account_names)
            return contracts
        except Exception as e:
            logger.error(f"获取活跃合约时出错: {str(e)}")
            raise
        finally:
            cursor.close()