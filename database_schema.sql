-- Rental Management System Database Schema
-- SQLite Database Design

-- Table: products
-- Stores information about beds and equipment available for rent
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('bed', 'equipment')),
    rental_price REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: renters
-- Stores information about people renting products
CREATE TABLE IF NOT EXISTS renters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    address TEXT,
    id_number TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: rentals
-- Stores rental agreements
CREATE TABLE IF NOT EXISTS rentals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    renter_id INTEGER NOT NULL,
    billing_type TEXT NOT NULL CHECK(billing_type IN ('monthly', 'yearly')),
    rental_price REAL NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'returned')),
    payment_status TEXT NOT NULL DEFAULT 'unpaid' CHECK(payment_status IN ('paid', 'unpaid')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (renter_id) REFERENCES renters(id) ON DELETE CASCADE
);

-- Table: payments
-- Tracks monthly/yearly payments for each rental
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rental_id INTEGER NOT NULL,
    payment_date DATE NOT NULL,
    amount REAL NOT NULL,
    payment_month TEXT NOT NULL, -- Format: YYYY-MM
    status TEXT NOT NULL DEFAULT 'unpaid' CHECK(status IN ('paid', 'unpaid')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rental_id) REFERENCES rentals(id) ON DELETE CASCADE
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_rentals_status ON rentals(status);
CREATE INDEX IF NOT EXISTS idx_rentals_dates ON rentals(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_rental ON payments(rental_id);
CREATE INDEX IF NOT EXISTS idx_payments_month ON payments(payment_month);

-- Views for reporting
CREATE VIEW IF NOT EXISTS active_rentals AS
SELECT 
    r.id as rental_id,
    p.name as product_name,
    p.type as product_type,
    rn.full_name as renter_name,
    rn.phone as renter_phone,
    r.billing_type,
    r.rental_price,
    r.start_date,
    r.end_date,
    r.status
FROM rentals r
JOIN products p ON r.product_id = p.id
JOIN renters rn ON r.renter_id = rn.id
WHERE r.status = 'active';

CREATE VIEW IF NOT EXISTS unpaid_payments AS
SELECT 
    py.id as payment_id,
    py.rental_id,
    p.name as product_name,
    rn.full_name as renter_name,
    rn.phone as renter_phone,
    py.payment_month,
    py.amount,
    py.payment_date
FROM payments py
JOIN rentals r ON py.rental_id = r.id
JOIN products p ON r.product_id = p.id
JOIN renters rn ON r.renter_id = rn.id
WHERE py.status = 'unpaid'
ORDER BY py.payment_month;
