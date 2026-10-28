CREATE DATABASE IF NOT EXISTS spendsmart;
USE spendsmart;

CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    transaction_type ENUM('income', 'expense') NOT NULL,
    category VARCHAR(50) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    transaction_date DATE NOT NULL,
    notes VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Optional sample data for testing the dashboard.
INSERT INTO transactions
    (title, transaction_type, category, amount, transaction_date, notes)
VALUES
    ('Monthly pocket money', 'income', 'Allowance', 5000.00, CURDATE(), 'Sample income'),
    ('Lunch', 'expense', 'Food', 120.00, CURDATE(), 'Sample expense'),
    ('Bus fare', 'expense', 'Transport', 40.00, CURDATE(), 'Sample expense'),
    ('Notebook', 'expense', 'Study', 85.00, CURDATE(), 'Sample expense');
