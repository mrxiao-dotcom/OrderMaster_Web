CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('decision_maker', 'executor') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_name VARCHAR(100) NOT NULL UNIQUE,
    account_type ENUM('large', 'small') NOT NULL,
    initial_value DECIMAL(15, 2) NOT NULL,
    current_value DECIMAL(15, 2) NOT NULL,
    risk_fund DECIMAL(15, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE contracts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    contract_name VARCHAR(100) NOT NULL,
    period VARCHAR(50) NOT NULL,
    stop_loss_amount DECIMAL(15, 2) NOT NULL,
    entry_time TEXT,
    period_upgrade_time TEXT,
    ma_price DECIMAL(15, 5),
    highest_price DECIMAL(15, 5),
    lowest_price DECIMAL(15, 5),
    actual_entry_price DECIMAL(15, 5),
    stop_loss_price DECIMAL(15, 5),
    bollinger_period VARCHAR(50),
    exit_time DATETIME,
    exit_price DECIMAL(15, 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    contract_id INT NOT NULL,
    account_id INT NOT NULL,
    status ENUM('pending', 'executed', 'exited') NOT NULL DEFAULT 'pending',
    entry_time DATETIME,
    exit_time DATETIME,
    exit_price DECIMAL(15, 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executed_by INT,
    FOREIGN KEY (contract_id) REFERENCES contracts(id),
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    FOREIGN KEY (executed_by) REFERENCES users(id)
);

CREATE TABLE market_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    contract_name VARCHAR(100) NOT NULL,
    price DECIMAL(15, 5) NOT NULL,
    timestamp DATETIME NOT NULL,
    volume DECIMAL(15, 2),
    open_interest DECIMAL(15, 2)
);

CREATE TABLE operation_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    operation_type VARCHAR(50) NOT NULL,
    target_table VARCHAR(50) NOT NULL,
    target_id INT,
    details TEXT,
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);