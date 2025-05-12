from app.utils.db import get_db

class Account:
    @staticmethod
    def get_by_id(account_id):
        db = get_db()
        cursor = db.cursor()
        
        query = "SELECT * FROM accounts WHERE id = %s"
        cursor.execute(query, (account_id,))
        account = cursor.fetchone()
        cursor.close()
        
        return account
    
    @staticmethod
    def get_all():
        db = get_db()
        cursor = db.cursor()
        
        query = "SELECT * FROM accounts ORDER BY account_name"
        cursor.execute(query)
        accounts = cursor.fetchall()
        cursor.close()
        
        return accounts
    
    @staticmethod
    def get_available_accounts():
        db = get_db()
        cursor = db.cursor()
        
        query = "SELECT * FROM accounts ORDER BY account_name"
        cursor.execute(query)
        accounts = cursor.fetchall()
        cursor.close()
        
        return accounts
    
    @staticmethod
    def create(account_data):
        db = get_db()
        cursor = db.cursor()
        
        query = """
        INSERT INTO accounts (account_name, account_type, initial_value, current_value, risk_fund)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            account_data['account_name'],
            account_data['account_type'],
            account_data['initial_value'],
            account_data['current_value'],
            account_data['risk_fund']
        ))
        
        account_id = cursor.lastrowid
        db.commit()
        cursor.close()
        
        return account_id
    
    @staticmethod
    def update(account_id, account_data):
        db = get_db()
        cursor = db.cursor()
        
        query = """
        UPDATE accounts
        SET account_name = %s,
            account_type = %s,
            current_value = %s,
            risk_fund = %s
        WHERE id = %s
        """
        
        cursor.execute(query, (
            account_data['account_name'],
            account_data['account_type'],
            account_data['current_value'],
            account_data['risk_fund'],
            account_id
        ))
        
        db.commit()
        cursor.close()