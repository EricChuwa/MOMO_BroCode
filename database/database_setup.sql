-- ============================================================
--  MoMo SMS Data Processing System
--  Team  : BroCode
--  Names : Eric Chuwa, Albert Afiti, Raphael Mumo
--  File  : database_setup.sql
--  Date  : May 2025
-- ============================================================
--  Run this file to create the full database from scratch.
--  It will DROP and recreate momo_brocode each time it runs.
-- ============================================================

DROP DATABASE IF EXISTS momo_brocode;
CREATE DATABASE momo_brocode;
USE momo_brocode;


-- ============================================================
--  TABLE 1: Users
-- ============================================================

CREATE TABLE Users (
    user_id      INT          AUTO_INCREMENT PRIMARY KEY,
    full_name    VARCHAR(150) NOT NULL,
    phone_number VARCHAR(20)  DEFAULT NULL,
    user_type    ENUM('PERSONAL','MERCHANT','AGENT','BANK','SYSTEM') NOT NULL,
    created_at   DATETIME     DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
--  TABLE 2: Transaction_Category
-- ============================================================

CREATE TABLE Transaction_Category (
    category_id   INT          AUTO_INCREMENT PRIMARY KEY,
    category_code VARCHAR(50)  NOT NULL UNIQUE,
    direction     ENUM('CREDIT','DEBIT','NEUTRAL') NOT NULL,
    category_name VARCHAR(100) NOT NULL
);


-- ============================================================
--  TABLE 3: Accounts
--    - 36521838    (MoMo wallet)
--    - 20077201001 (linked I&M Bank account)
-- ============================================================

CREATE TABLE Accounts (
    account_id     INT         AUTO_INCREMENT PRIMARY KEY,
    user_id        INT         NOT NULL,
    account_number VARCHAR(20) NOT NULL UNIQUE,
    account_type   ENUM('MOMO_WALLET','BANK_LINKED') NOT NULL,

    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);


-- ============================================================
--  TABLE 4: Transactions
-- ============================================================

CREATE TABLE Transactions (
    transaction_id   BIGINT        AUTO_INCREMENT PRIMARY KEY,
    category_id      INT           NOT NULL,
    account_id       INT           DEFAULT NULL,
    amount           DECIMAL(15,2) NOT NULL CHECK (amount >= 0),
    fee              DECIMAL(15,2) NOT NULL DEFAULT 0.00 CHECK (fee >= 0),
    status           ENUM('COMPLETED','FAILED','REVERSED','PENDING') NOT NULL,
    transaction_date DATETIME      NOT NULL,
    balance_after    DECIMAL(15,2) DEFAULT NULL,
    merchant_code    VARCHAR(20)   DEFAULT NULL,

    FOREIGN KEY (category_id) REFERENCES Transaction_Category(category_id),
    FOREIGN KEY (account_id)  REFERENCES Accounts(account_id)
);


-- ============================================================
--  TABLE 5: Transaction_Participants
-- ============================================================

CREATE TABLE Transaction_Participants (
    participant_id INT    AUTO_INCREMENT PRIMARY KEY,
    transaction_id BIGINT NOT NULL,
    user_id        INT    NOT NULL,
    role           ENUM('SENDER','RECEIVER','AGENT') NOT NULL,

    FOREIGN KEY (transaction_id) REFERENCES Transactions(transaction_id),
    FOREIGN KEY (user_id)        REFERENCES Users(user_id)
);


-- ============================================================
--  TABLE 6: System_Logs
-- ============================================================

CREATE TABLE System_Logs (
    log_id         BIGINT      AUTO_INCREMENT PRIMARY KEY,
    transaction_id BIGINT      DEFAULT NULL,
    log_level      ENUM('INFO','WARNING','ERROR') NOT NULL,
    source         VARCHAR(50) NOT NULL,
    message        TEXT        NOT NULL,
    created_at     DATETIME    DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (transaction_id) REFERENCES Transactions(transaction_id)
);

DELIMITER //

CREATE TRIGGER auto_log_failed_or_reversed
AFTER INSERT ON Transactions
FOR EACH ROW
BEGIN
    IF NEW.status = 'FAILED' OR NEW.status = 'REVERSED' THEN
        INSERT INTO System_Logs (transaction_id, log_level, source, message)
        VALUES (
            NEW.transaction_id,
            'WARNING',
            'TRIGGER',
            CONCAT('Transaction ', NEW.transaction_id,
                   ' has status: ', NEW.status,
                   ' — amount: ', NEW.amount, ' RWF')
        );
    END IF;
END//

DELIMITER ;


-- ============================================================
--  SAMPLE DATA
--  All values taken directly from modified_sms_v2.xml
-- ============================================================

-- Users -------------------------------------------------------

INSERT INTO Users (full_name, phone_number, user_type) VALUES
    ('Abebe Chala CHEBUDIE',      '250795963036', 'PERSONAL'),
    ('Jane Smith',                 NULL,           'PERSONAL'),
    ('Samuel Carter',              '250791666666', 'PERSONAL'),
    ('Cynthia UMUGANWA',           '250790698110', 'PERSONAL'),
    ('Dieudonne MUGIRANEZA',       '250789447277', 'PERSONAL'),
    ('Mediatrice UWAYISENGA',      '250788658286', 'PERSONAL'),
    ('Robert Brown',               '250788999999', 'PERSONAL'),
    ('Agent Sophia',               '250790777777', 'AGENT'),
    ('Agent John',                 '250789888888', 'AGENT'),
    ('DIRECT PAYMENT LTD',         NULL,           'MERCHANT'),
    ('ESICIA LTD KPAY',            NULL,           'MERCHANT'),
    ('IREMBO Ltd',                 NULL,           'MERCHANT'),
    ('INTOUCH COMMUNICATIONS LTD', NULL,           'MERCHANT'),
    ('MTN System',                 NULL,           'SYSTEM');


-- Accounts ----------------------------------------------------

INSERT INTO Accounts (user_id, account_number, account_type) VALUES
    (1, '36521838',    'MOMO_WALLET'),
    (1, '20077201001', 'BANK_LINKED');


-- Transaction_Category ----------------------------------------

INSERT INTO Transaction_Category (category_code, direction, category_name) VALUES
    ('INCOMING_TRANSFER',  'CREDIT',  'Incoming Transfer'),
    ('BANK_DEPOSIT',       'CREDIT',  'Bank Deposit'),
    ('TRANSFER_TO_MOBILE', 'DEBIT',   'Transfer to Mobile'),
    ('MERCHANT_PAYMENT',   'DEBIT',   'Merchant Payment'),
    ('CASH_WITHDRAWAL',    'DEBIT',   'Cash Withdrawal'),
    ('AIRTIME_PURCHASE',   'DEBIT',   'Airtime Purchase'),
    ('DATA_BUNDLE',        'DEBIT',   'Data Bundle'),
    ('PAYMENT_TO_CODE',    'DEBIT',   'Payment to Code'),
    ('BANK_TRANSFER_OUT',  'DEBIT',   'Bank Transfer Out'),
    ('REVERSAL',           'NEUTRAL', 'Transaction Reversal'),
    ('FAILED_TRANSACTION', 'NEUTRAL', 'Failed Transaction');


-- Transactions ------------------------------------------------

INSERT INTO Transactions
    (category_id, account_id, amount, fee, status, transaction_date, balance_after, merchant_code)
VALUES
    (1,  1,    2000.00,  0.00,   'COMPLETED', '2024-05-10 16:30:51', 2000.00,  NULL),
    (2,  1,   40000.00,  0.00,   'COMPLETED', '2024-05-11 18:43:49', 40400.00, NULL),
    (3,  1,   10000.00,  100.00, 'COMPLETED', '2024-05-11 20:34:47', 28300.00, NULL),
    (4,  1,     600.00,  0.00,   'COMPLETED', '2024-05-12 19:23:50', 6040.00,  NULL),
    (5,  1,   20000.00,  350.00, 'COMPLETED', '2024-05-26 02:10:27', NULL,     NULL),
    (6,  1,    2000.00,  0.00,   'COMPLETED', '2024-05-12 11:41:28', 25280.00, NULL),
    (8,  1,     500.00,  0.00,   'COMPLETED', '2024-05-12 13:26:13', 18090.00, '95464'),
    (9,  2,   50000.00,  0.00,   'COMPLETED', '2024-10-23 09:59:01', NULL,     NULL),
    (10, 1,    3000.00,  0.00,   'REVERSED',  '2024-10-07 14:37:00', 10312.00, NULL),
    (11, NULL, 14200.00, 0.00,   'FAILED',    '2024-09-21 15:49:01', NULL,     NULL);


-- Transaction_Participants ------------------------------------

INSERT INTO Transaction_Participants (transaction_id, user_id, role) VALUES
    (1,  2,  'SENDER'),    -- Jane Smith sent
    (1,  1,  'RECEIVER'),  -- Abebe received
    (2,  14, 'SENDER'),    -- MTN System bank deposit
    (2,  1,  'RECEIVER'),  -- Abebe received
    (3,  1,  'SENDER'),    -- Abebe sent
    (3,  3,  'RECEIVER'),  -- Samuel Carter received
    (4,  1,  'SENDER'),    -- Abebe paid
    (4,  10, 'RECEIVER'),  -- DIRECT PAYMENT LTD received
    (5,  1,  'SENDER'),    -- Abebe withdrew
    (5,  8,  'AGENT'),     -- Agent Sophia facilitated
    (6,  1,  'SENDER'),    -- Abebe bought airtime
    (6,  14, 'RECEIVER'),  -- MTN System received
    (7,  1,  'SENDER'),    -- Abebe paid to code
    (7,  4,  'RECEIVER'),  -- Cynthia UMUGANWA received
    (8,  1,  'SENDER'),    -- Abebe bank transfer
    (9,  1,  'SENDER'),    -- Abebe (reversal)
    (9,  6,  'RECEIVER'),  -- Mediatrice UWAYISENGA
    (10, 1,  'SENDER'),    -- Abebe (failed attempt)
    (10, 11, 'RECEIVER');  -- ESICIA LTD KPAY


-- System_Logs -------------------------------------------------

INSERT INTO System_Logs (transaction_id, log_level, source, message) VALUES
    (NULL, 'INFO',    'PARSER',      'Loaded 1691 messages from modified_sms_v2.xml'),
    (NULL, 'INFO',    'CATEGORIZER', 'Matched 11 categories across 1691 messages'),
    (NULL, 'WARNING', 'PARSER',      'Skipped 1 OTP message — not a financial transaction'),
    (NULL, 'ERROR',   'LOADER',      'phone_number masked for tx 1 — stored name only');


-- ============================================================
--  CRUD QUERIES
-- ============================================================

-- READ: all transactions with their category
SELECT
    t.transaction_id,
    tc.category_name,
    tc.direction,
    t.amount,
    t.fee,
    t.status,
    t.transaction_date,
    t.balance_after
FROM Transactions t
JOIN Transaction_Category tc ON tc.category_id = t.category_id
ORDER BY t.transaction_date;

-- ============================================================
-- READ: who was involved in each transaction
-- ============================================================
SELECT
    t.transaction_id,
    t.amount,
    t.status,
    u.full_name AS participant,
    tp.role
FROM Transaction_Participants tp
JOIN Transactions t ON t.transaction_id = tp.transaction_id
JOIN Users u        ON u.user_id        = tp.user_id
ORDER BY t.transaction_id, tp.role;

-- ============================================================
-- READ: total spent per category
-- ============================================================
SELECT
    tc.category_name,
    COUNT(*)      AS num_transactions,
    SUM(t.amount) AS total_spent,
    SUM(t.fee)    AS total_fees
FROM Transactions t
JOIN Transaction_Category tc ON tc.category_id = t.category_id
WHERE tc.direction = 'DEBIT'
  AND t.status     = 'COMPLETED'
GROUP BY tc.category_name
ORDER BY total_spent DESC;

-- ============================================================
-- READ: confirm the trigger wrote WARNING logs automatically
-- ============================================================
SELECT * FROM System_Logs WHERE source = 'TRIGGER';

-- ============================================================
-- UPDATE: fix a user phone number
-- ============================================================
UPDATE Users
SET    phone_number = '250791234567'
WHERE  user_id = 2;

-- ============================================================
-- DELETE: remove a specific log entry
-- ============================================================
DELETE FROM System_Logs
WHERE  log_id = 3;


-- ============================================================
--  END OF FILE
-- ============================================================