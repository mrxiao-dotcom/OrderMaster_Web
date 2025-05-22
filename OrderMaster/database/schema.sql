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
    contract_name VARCHAR(100) NOT NULL COLLATE 'utf8mb4_0900_ai_ci',
    period VARCHAR(50) NOT NULL COLLATE 'utf8mb4_0900_ai_ci',
    stop_loss_amount DECIMAL(15, 2) NOT NULL,
    entry_time TEXT NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
    period_upgrade_time TEXT NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
    ma_price DECIMAL(15, 5) NULL DEFAULT NULL,
    actual_entry_price DECIMAL(15, 5) NULL DEFAULT NULL,
    stop_loss_price DECIMAL(15, 5) NULL DEFAULT NULL,
    bollinger_period VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
    exit_time DATETIME NULL DEFAULT NULL,
    exit_price DECIMAL(15, 5) NULL DEFAULT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL DEFAULT NULL,
    price DECIMAL(10, 4) NULL DEFAULT NULL,
    PRIMARY KEY (id) USING BTREE,
    INDEX created_by (created_by) USING BTREE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON UPDATE NO ACTION ON DELETE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

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