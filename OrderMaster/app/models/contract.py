from app.utils.db import get_db
import sys
import logging
from app.models.order import Order

logger = logging.getLogger(__name__)
class Contract:
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
    
    @staticmethod
    def get_by_id(contract_id):
        logger.info(f"通过ID获取合约: {contract_id}")
        db = get_db()
        cursor = db.cursor()
        
        try:
            # 修改查询以包含关联账户信息和订单数据
            query = """
            SELECT c.*, 
                COALESCE(GROUP_CONCAT(DISTINCT a.account_name), '') as associated_accounts,
                COALESCE(GROUP_CONCAT(DISTINCT o.id), '') as order_ids,
                COALESCE(GROUP_CONCAT(DISTINCT o.status), '') as order_statuses,
                COALESCE(GROUP_CONCAT(DISTINCT a.id), '') as account_ids
            FROM contracts c
            LEFT JOIN orders o ON c.id = o.contract_id
            LEFT JOIN accounts a ON o.account_id = a.id
            WHERE c.id = %s
            GROUP BY c.id
            """
            logger.debug(f"执行SQL查询: {query} 参数: {contract_id}")
            cursor.execute(query, (contract_id,))
            contract = cursor.fetchone()
            
            if contract:
                # 加载订单数据
                contract['orders'] = Order.get_by_contract(contract_id)
                logger.info(f"合约 {contract_id} 的订单数量: {len(contract['orders'])}")
            
            return contract
        except Exception as e:
            logger.error(f"通过ID获取合约时出错: {str(e)}")
            logger.error(traceback.format_exc())
            raise
        finally:
            cursor.close()

    @staticmethod
    def get_exited_contracts():
        logger.info("开始获取已出场合约列表")
        db = get_db()
        cursor = db.cursor()
        
        try:
            query = """
            SELECT c.*, 
                COALESCE(GROUP_CONCAT(DISTINCT a.account_name), '') as associated_accounts
            FROM contracts c
            LEFT JOIN orders o ON c.id = o.contract_id
            LEFT JOIN accounts a ON o.account_id = a.id
            WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.contract_id = c.id AND o.status != 'exited')
            AND EXISTS (SELECT 1 FROM orders o WHERE o.contract_id = c.id)
            GROUP BY c.id
            ORDER BY c.created_at DESC
            """
            
            cursor.execute(query)
            contracts = cursor.fetchall()
            logger.info(f"查询到的已出场合约数量: {len(contracts)}")
            
            # 为每个合约加载订单数据
            for contract in contracts:
                contract['orders'] = Order.get_by_contract(contract['id'])
                logger.debug(f"合约 {contract['id']} 的订单数量: {len(contract['orders'])}")
            
            return contracts
        except Exception as e:
            logger.error(f"获取已出场合约时出错: {str(e)}")
            logger.error(traceback.format_exc())
            raise
        finally:
            cursor.close()
    
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