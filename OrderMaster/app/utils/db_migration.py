from app.utils.db import get_db

def migrate_datetime_to_string():
    """
    将合约表中的日期时间字段从DATETIME类型改为VARCHAR类型
    """
    db = get_db()
    cursor = db.cursor()
    
    try:
        # 1. 创建临时表
        cursor.execute("""
        CREATE TABLE contracts_temp (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_name TEXT NOT NULL,
            period TEXT NOT NULL,
            stop_loss_amount REAL NOT NULL,
            bollinger_period INTEGER NOT NULL,
            created_by INTEGER NOT NULL,
            entry_time VARCHAR(10),
            cycle_time VARCHAR(10),
            ma_price REAL,
            price REAL,
            actual_entry_price REAL,
            stop_loss_price REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active',
            exited_at TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
        """)
        
        # 2. 转换并复制数据
        cursor.execute("""
        INSERT INTO contracts_temp (
            id, contract_name, period, stop_loss_amount, bollinger_period,
            created_by, entry_time, cycle_time, ma_price, price,
            actual_entry_price, stop_loss_price, created_at, status, exited_at
        )
        SELECT 
            id, contract_name, period, stop_loss_amount, bollinger_period,
            created_by,
            CASE 
                WHEN entry_time IS NOT NULL THEN strftime('%m%d.%H%M', entry_time)
                ELSE NULL
            END as entry_time,
            CASE 
                WHEN cycle_time IS NOT NULL THEN strftime('%m%d.%H%M', cycle_time)
                ELSE NULL
            END as cycle_time,
            ma_price, price, actual_entry_price, stop_loss_price,
            created_at, status, exited_at
        FROM contracts
        """)
        
        # 3. 删除原表
        cursor.execute("DROP TABLE contracts")
        
        # 4. 重命名临时表
        cursor.execute("ALTER TABLE contracts_temp RENAME TO contracts")
        
        db.commit()
        print("数据库迁移成功：日期时间字段已转换为字符串格式")
        
    except Exception as e:
        db.rollback()
        print(f"数据库迁移失败：{str(e)}")
        raise
    finally:
        cursor.close()

if __name__ == '__main__':
    migrate_datetime_to_string()