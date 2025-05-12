import pymysql
import time
import requests
from datetime import datetime
import logging
from config import DB_CONFIG

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='market_data_collector.log'
)

logger = logging.getLogger('market_data_collector')

def get_db_connection():
    return pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        cursorclass=pymysql.cursors.DictCursor
    )

def get_active_contracts():
    """获取所有活跃的合约"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT DISTINCT c.contract_name
    FROM contracts c
    JOIN orders o ON c.id = o.contract_id
    WHERE o.status IN ('pending', 'executed')
    """
    
    cursor.execute(query)
    contracts = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return [contract['contract_name'] for contract in contracts]

def fetch_market_data(contract_name):
    """从行情API获取市场数据"""
    try:
        # 这里替换为实际的行情API
        response = requests.get(f"https://api.example.com/market_data/{contract_name}")
        data = response.json()
        
        return {
            'price': data['last_price'],
            'volume': data['volume'],
            'open_interest': data['open_interest']
        }
    except Exception as e:
        logger.error(f"获取{contract_name}行情数据失败: {str(e)}")
        return None

def save_market_data(contract_name, market_data):
    """保存市场数据到数据库"""
    if not market_data:
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
        INSERT INTO market_data (contract_name, price, timestamp, volume, open_interest)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            contract_name,
            market_data['price'],
            datetime.now(),
            market_data['volume'],
            market_data['open_interest']
        ))
        
        conn.commit()
        logger.info(f"保存{contract_name}行情数据成功")
    except Exception as e:
        conn.rollback()
        logger.error(f"保存{contract_name}行情数据失败: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def main():
    logger.info("开始采集市场数据")
    
    try:
        active_contracts = get_active_contracts()
        logger.info(f"获取到{len(active_contracts)}个活跃合约")
        
        for contract_name in active_contracts:
            market_data = fetch_market_data(contract_name)
            save_market_data(contract_name, market_data)
            
            # 避免API请求过于频繁
            time.sleep(1)
    except Exception as e:
        logger.error(f"采集市场数据过程中发生错误: {str(e)}")
    
    logger.info("市场数据采集完成")

if __name__ == "__main__":
    main()