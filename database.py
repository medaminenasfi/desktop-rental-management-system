"""
Database Handler for Rental Management System
Manages all database operations using SQLite
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import os


class DatabaseHandler:
    """Handles all database operations for the rental management system"""
    
    def __init__(self, db_name: str = "rental_management.db"):
        """Initialize database connection"""
        self.db_name = db_name
        self.connection = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            raise
    
    def create_tables(self):
        """Create all necessary tables"""
        schema_file = "database_schema.sql"
        
        if os.path.exists(schema_file):
            with open(schema_file, 'r') as f:
                schema = f.read()
                self.cursor.executescript(schema)
        else:
            # Fallback: Create tables directly
            self._create_tables_directly()
        
        # Add payment_status column if it doesn't exist (migration)
        self._migrate_payment_status()
        
        self.connection.commit()
    
    def _migrate_payment_status(self):
        """Add payment_status column to existing rentals table if missing"""
        try:
            # Check if column exists
            self.cursor.execute("PRAGMA table_info(rentals)")
            columns = [column[1] for column in self.cursor.fetchall()]
            
            if 'payment_status' not in columns:
                # Add the column with default value
                self.cursor.execute("""
                    ALTER TABLE rentals 
                    ADD COLUMN payment_status TEXT NOT NULL DEFAULT 'unpaid' 
                    CHECK(payment_status IN ('paid', 'unpaid'))
                """)
                print("Database migrated: payment_status column added to rentals table")
        except sqlite3.Error as e:
            print(f"Migration note: {e}")
    
    def _create_tables_directly(self):
        """Create tables directly if schema file not found"""
        tables = [
            """CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('bed', 'equipment')),
                rental_price REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS renters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                id_number TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS rentals (
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
            )""",
            """CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rental_id INTEGER NOT NULL,
                payment_date DATE NOT NULL,
                amount REAL NOT NULL,
                payment_month TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'unpaid' CHECK(status IN ('paid', 'unpaid')),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (rental_id) REFERENCES rentals(id) ON DELETE CASCADE
            )"""
        ]
        
        for table in tables:
            self.cursor.execute(table)
    
    # ==================== PRODUCT OPERATIONS ====================
    
    def add_product(self, name: str, product_type: str, rental_price: float) -> int:
        """Add a new product"""
        query = "INSERT INTO products (name, type, rental_price) VALUES (?, ?, ?)"
        self.cursor.execute(query, (name, product_type, rental_price))
        self.connection.commit()
        return self.cursor.lastrowid
    
    def get_all_products(self) -> List[Dict]:
        """Get all products"""
        query = "SELECT * FROM products ORDER BY name"
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Get product by ID"""
        query = "SELECT * FROM products WHERE id = ?"
        self.cursor.execute(query, (product_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_product(self, product_id: int, name: str, product_type: str, rental_price: float):
        """Update product information"""
        query = "UPDATE products SET name = ?, type = ?, rental_price = ? WHERE id = ?"
        self.cursor.execute(query, (name, product_type, rental_price, product_id))
        self.connection.commit()
    
    def delete_product(self, product_id: int):
        """Delete a product"""
        query = "DELETE FROM products WHERE id = ?"
        self.cursor.execute(query, (product_id,))
        self.connection.commit()
    
    # ==================== RENTER OPERATIONS ====================
    
    def add_renter(self, full_name: str, phone: str = "", email: str = "", 
                   address: str = "", id_number: str = "") -> int:
        """Add a new renter"""
        query = """INSERT INTO renters (full_name, phone, email, address, id_number) 
                   VALUES (?, ?, ?, ?, ?)"""
        self.cursor.execute(query, (full_name, phone, email, address, id_number))
        self.connection.commit()
        return self.cursor.lastrowid
    
    def get_all_renters(self) -> List[Dict]:
        """Get all renters"""
        query = "SELECT * FROM renters ORDER BY full_name"
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_renter_by_id(self, renter_id: int) -> Optional[Dict]:
        """Get renter by ID"""
        query = "SELECT * FROM renters WHERE id = ?"
        self.cursor.execute(query, (renter_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_renter(self, renter_id: int, full_name: str, phone: str = "", 
                      email: str = "", address: str = "", id_number: str = ""):
        """Update renter information"""
        query = """UPDATE renters SET full_name = ?, phone = ?, email = ?, 
                   address = ?, id_number = ? WHERE id = ?"""
        self.cursor.execute(query, (full_name, phone, email, address, id_number, renter_id))
        self.connection.commit()
    
    def delete_renter(self, renter_id: int):
        """Delete a renter"""
        query = "DELETE FROM renters WHERE id = ?"
        self.cursor.execute(query, (renter_id,))
        self.connection.commit()
    
    # ==================== RENTAL OPERATIONS ====================
    
    def add_rental(self, product_id: int, renter_id: int, billing_type: str, 
                   rental_price: float, start_date: str, end_date: str = None) -> int:
        """Add a new rental and create payment schedule"""
        query = """INSERT INTO rentals (product_id, renter_id, billing_type, rental_price, 
                   start_date, end_date, status) VALUES (?, ?, ?, ?, ?, ?, 'active')"""
        self.cursor.execute(query, (product_id, renter_id, billing_type, rental_price, 
                                   start_date, end_date))
        rental_id = self.cursor.lastrowid
        
        # Create payment schedule
        self._create_payment_schedule(rental_id, billing_type, rental_price, start_date, end_date)
        
        self.connection.commit()
        return rental_id
    
    def _create_payment_schedule(self, rental_id: int, billing_type: str, 
                                 rental_price: float, start_date: str, end_date: str = None):
        """Create payment schedule based on billing type"""
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now() + timedelta(days=365)
        
        current_date = start
        
        if billing_type == 'monthly':
            while current_date <= end:
                payment_month = current_date.strftime("%Y-%m")
                payment_date = current_date.strftime("%Y-%m-%d")
                
                query = """INSERT INTO payments (rental_id, payment_date, amount, payment_month, status)
                          VALUES (?, ?, ?, ?, 'unpaid')"""
                self.cursor.execute(query, (rental_id, payment_date, rental_price, payment_month))
                
                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
        
        elif billing_type == 'yearly':
            while current_date <= end:
                payment_month = current_date.strftime("%Y-%m")
                payment_date = current_date.strftime("%Y-%m-%d")
                
                query = """INSERT INTO payments (rental_id, payment_date, amount, payment_month, status)
                          VALUES (?, ?, ?, ?, 'unpaid')"""
                self.cursor.execute(query, (rental_id, payment_date, rental_price, payment_month))
                
                # Move to next year
                current_date = current_date.replace(year=current_date.year + 1)
    
    def get_all_rentals(self) -> List[Dict]:
        """Get all rentals with related information"""
        query = """
        SELECT 
            r.id, r.product_id, r.renter_id, r.billing_type, r.rental_price,
            r.start_date, r.end_date, r.status, r.created_at,
            p.name as product_name, p.type as product_type,
            rn.full_name as renter_name, rn.phone as renter_phone
        FROM rentals r
        JOIN products p ON r.product_id = p.id
        JOIN renters rn ON r.renter_id = rn.id
        ORDER BY r.created_at DESC
        """
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_active_rentals(self) -> List[Dict]:
        """Get all active rentals"""
        query = """
        SELECT 
            r.id, r.product_id, r.renter_id, r.billing_type, r.rental_price,
            r.start_date, r.end_date, r.status,
            p.name as product_name, p.type as product_type,
            rn.full_name as renter_name, rn.phone as renter_phone
        FROM rentals r
        JOIN products p ON r.product_id = p.id
        JOIN renters rn ON r.renter_id = rn.id
        WHERE r.status = 'active'
        ORDER BY r.start_date DESC
        """
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_rental_by_id(self, rental_id: int) -> Optional[Dict]:
        """Get rental by ID"""
        query = """
        SELECT 
            r.*, 
            p.name as product_name, p.type as product_type,
            rn.full_name as renter_name, rn.phone as renter_phone, rn.email as renter_email
        FROM rentals r
        JOIN products p ON r.product_id = p.id
        JOIN renters rn ON r.renter_id = rn.id
        WHERE r.id = ?
        """
        self.cursor.execute(query, (rental_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_rental_status(self, rental_id: int, status: str):
        """Update rental status"""
        query = "UPDATE rentals SET status = ? WHERE id = ?"
        self.cursor.execute(query, (status, rental_id))
        self.connection.commit()
    
    def update_rental_payment_status(self, rental_id: int, payment_status: str):
        """Update rental payment status"""
        try:
            query = "UPDATE rentals SET payment_status = ? WHERE id = ?"
            self.cursor.execute(query, (payment_status, rental_id))
            self.connection.commit()
            print(f"Updated rental {rental_id} payment status to {payment_status}")
        except sqlite3.Error as e:
            print(f"Database error updating payment status: {e}")
            self.connection.rollback()
            raise
    
    def delete_rental(self, rental_id: int):
        """Delete a rental and associated payments"""
        query = "DELETE FROM rentals WHERE id = ?"
        self.cursor.execute(query, (rental_id,))
        self.connection.commit()
    
    # ==================== PAYMENT OPERATIONS ====================
    
    def get_payments_by_rental(self, rental_id: int) -> List[Dict]:
        """Get all payments for a rental"""
        query = """SELECT * FROM payments 
                   WHERE rental_id = ? 
                   ORDER BY payment_month"""
        self.cursor.execute(query, (rental_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_unpaid_payments(self) -> List[Dict]:
        """Get all unpaid payments"""
        query = """
        SELECT 
            py.id, py.rental_id, py.payment_month, py.amount, py.payment_date,
            p.name as product_name,
            rn.full_name as renter_name, rn.phone as renter_phone
        FROM payments py
        JOIN rentals r ON py.rental_id = r.id
        JOIN products p ON r.product_id = p.id
        JOIN renters rn ON r.renter_id = rn.id
        WHERE py.status = 'unpaid' AND r.status = 'active'
        ORDER BY py.payment_month
        """
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_unpaid_rentals_with_totals(self) -> List[Dict]:
        """Get all unpaid rentals with monthly payment amounts"""
        query = """
        SELECT 
            r.id, r.rental_price, r.billing_type,
            p.name as product_name,
            rn.full_name as renter_name, rn.phone as renter_phone
        FROM rentals r
        JOIN products p ON r.product_id = p.id
        JOIN renters rn ON r.renter_id = rn.id
        WHERE r.payment_status = 'unpaid' AND r.status = 'active'
        ORDER BY rn.full_name
        """
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def mark_payment_paid(self, payment_id: int, notes: str = ""):
        """Mark a payment as paid"""
        query = "UPDATE payments SET status = 'paid', notes = ? WHERE id = ?"
        self.cursor.execute(query, (notes, payment_id))
        self.connection.commit()
    
    def mark_payment_unpaid(self, payment_id: int):
        """Mark a payment as unpaid"""
        query = "UPDATE payments SET status = 'unpaid' WHERE id = ?"
        self.cursor.execute(query, (payment_id,))
        self.connection.commit()
    
    # ==================== STATISTICS & REPORTS ====================
    
    def get_total_unpaid_amount(self) -> float:
        """Get total amount owed across all unpaid rentals for all periods"""
        query = """
        SELECT 
            r.rental_price,
            r.billing_type,
            r.start_date,
            CASE 
                WHEN r.end_date IS NULL THEN date('now')
                ELSE r.end_date 
            END as end_date
        FROM rentals r
        WHERE r.payment_status = 'unpaid' AND r.status = 'active'
        """
        self.cursor.execute(query)
        rentals = self.cursor.fetchall()
        
        total_unpaid = 0.0
        current_date = datetime.now()
        
        for rental in rentals:
            start_date = datetime.strptime(rental['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(rental['end_date'], '%Y-%m-%d') if rental['end_date'] else current_date
            
            # Calculate the number of periods owed
            if rental['billing_type'] == 'monthly':
                # Calculate months owed (including partial month as full month)
                months_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                if end_date.day > start_date.day:
                    months_diff += 1
                months_diff = max(1, months_diff)  # At least 1 month
                total_unpaid += rental['rental_price'] * months_diff
            else:  # yearly
                # Calculate years owed
                years_diff = end_date.year - start_date.year
                if end_date.month > start_date.month or (end_date.month == start_date.month and end_date.day > start_date.day):
                    years_diff += 1
                years_diff = max(1, years_diff)  # At least 1 year
                total_unpaid += rental['rental_price'] * years_diff
        
        return total_unpaid
    
    def get_tenant_totals(self) -> List[Dict]:
        """Get totals for each tenant showing amount received and amount still owed"""
        query = """
        SELECT 
            rt.id as renter_id,
            rt.full_name as renter_name,
            rt.phone as renter_phone,
            COUNT(r.id) as total_rentals,
            SUM(CASE WHEN r.payment_status = 'paid' THEN 1 ELSE 0 END) as paid_rentals,
            SUM(CASE WHEN r.payment_status = 'unpaid' THEN 1 ELSE 0 END) as unpaid_rentals
        FROM renters rt
        LEFT JOIN rentals r ON rt.id = r.renter_id AND r.status = 'active'
        GROUP BY rt.id, rt.full_name, rt.phone
        ORDER BY rt.full_name
        """
        self.cursor.execute(query)
        tenants = self.cursor.fetchall()
        
        tenant_totals = []
        current_date = datetime.now()
        
        for tenant in tenants:
            # Calculate total amount received (paid rentals)
            paid_query = """
            SELECT 
                r.rental_price,
                r.billing_type,
                r.start_date,
                CASE 
                    WHEN r.end_date IS NULL THEN date('now')
                    ELSE r.end_date 
                END as end_date
            FROM rentals r
            WHERE r.renter_id = ? AND r.payment_status = 'paid' AND r.status = 'active'
            """
            self.cursor.execute(paid_query, (tenant['renter_id'],))
            paid_rentals = self.cursor.fetchall()
            
            total_received = 0.0
            for rental in paid_rentals:
                start_date = datetime.strptime(rental['start_date'], '%Y-%m-%d')
                end_date = datetime.strptime(rental['end_date'], '%Y-%m-%d') if rental['end_date'] else current_date
                
                if rental['billing_type'] == 'monthly':
                    months_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                    if end_date.day > start_date.day:
                        months_diff += 1
                    months_diff = max(1, months_diff)
                    total_received += rental['rental_price'] * months_diff
                else:  # yearly
                    years_diff = end_date.year - start_date.year
                    if end_date.month > start_date.month or (end_date.month == start_date.month and end_date.day > start_date.day):
                        years_diff += 1
                    years_diff = max(1, years_diff)
                    total_received += rental['rental_price'] * years_diff
            
            # Calculate total amount still owed (unpaid rentals)
            unpaid_query = """
            SELECT 
                r.rental_price,
                r.billing_type,
                r.start_date,
                CASE 
                    WHEN r.end_date IS NULL THEN date('now')
                    ELSE r.end_date 
                END as end_date
            FROM rentals r
            WHERE r.renter_id = ? AND r.payment_status = 'unpaid' AND r.status = 'active'
            """
            self.cursor.execute(unpaid_query, (tenant['renter_id'],))
            unpaid_rentals = self.cursor.fetchall()
            
            total_owed = 0.0
            for rental in unpaid_rentals:
                start_date = datetime.strptime(rental['start_date'], '%Y-%m-%d')
                end_date = datetime.strptime(rental['end_date'], '%Y-%m-%d') if rental['end_date'] else current_date
                
                if rental['billing_type'] == 'monthly':
                    months_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                    if end_date.day > start_date.day:
                        months_diff += 1
                    months_diff = max(1, months_diff)
                    total_owed += rental['rental_price'] * months_diff
                else:  # yearly
                    years_diff = end_date.year - start_date.year
                    if end_date.month > start_date.month or (end_date.month == start_date.month and end_date.day > start_date.day):
                        years_diff += 1
                    years_diff = max(1, years_diff)
                    total_owed += rental['rental_price'] * years_diff
            
            tenant_totals.append({
                'renter_id': tenant['renter_id'],
                'renter_name': tenant['renter_name'],
                'renter_phone': tenant['renter_phone'],
                'total_rentals': tenant['total_rentals'],
                'paid_rentals': tenant['paid_rentals'],
                'unpaid_rentals': tenant['unpaid_rentals'],
                'total_received': total_received,
                'total_owed': total_owed,
                'total_amount': total_received + total_owed
            })
        
        return tenant_totals
    
    def get_rental_financial_summary(self, rental_id: int) -> Dict:
        """Get financial summary for a specific rental"""
        query = """
        SELECT 
            r.rental_price,
            r.billing_type,
            r.payment_status,
            r.start_date,
            CASE 
                WHEN r.end_date IS NULL THEN date('now')
                ELSE r.end_date 
            END as end_date
        FROM rentals r
        WHERE r.id = ?
        """
        self.cursor.execute(query, (rental_id,))
        rental = self.cursor.fetchone()
        
        if not rental:
            return {'total_to_pay': 0.0, 'total_received': 0.0}
        
        current_date = datetime.now()
        start_date = datetime.strptime(rental['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(rental['end_date'], '%Y-%m-%d') if rental['end_date'] else current_date
        
        # Calculate total amount to pay based on periods
        if rental['billing_type'] == 'monthly':
            months_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            if end_date.day > start_date.day:
                months_diff += 1
            months_diff = max(1, months_diff)
            total_to_pay = rental['rental_price'] * months_diff
        else:  # yearly
            years_diff = end_date.year - start_date.year
            if end_date.month > start_date.month or (end_date.month == start_date.month and end_date.day > start_date.day):
                years_diff += 1
            years_diff = max(1, years_diff)
            total_to_pay = rental['rental_price'] * years_diff
        
        # Calculate total received (if paid, it's the total amount)
        total_received = total_to_pay if rental['payment_status'] == 'paid' else 0.0
        
        return {
            'total_to_pay': total_to_pay,
            'total_received': total_received,
            'still_owed': total_to_pay - total_received
        }
    
    def get_total_income(self) -> float:
        """Calculate total income from paid payments"""
        query = "SELECT SUM(amount) as total FROM payments WHERE status = 'paid'"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return result['total'] if result['total'] else 0.0
    
    def get_income_by_rental(self, rental_id: int) -> Tuple[float, float]:
        """Get paid and expected income for a rental"""
        query_paid = """SELECT SUM(amount) as total FROM payments 
                       WHERE rental_id = ? AND status = 'paid'"""
        self.cursor.execute(query_paid, (rental_id,))
        paid = self.cursor.fetchone()['total'] or 0.0
        
        query_expected = """SELECT SUM(amount) as total FROM payments 
                           WHERE rental_id = ?"""
        self.cursor.execute(query_expected, (rental_id,))
        expected = self.cursor.fetchone()['total'] or 0.0
        
        return paid, expected
    
    def get_dashboard_stats(self) -> Dict:
        """Get statistics for dashboard"""
        stats = {}
        
        # Total products
        self.cursor.execute("SELECT COUNT(*) as count FROM products")
        stats['total_products'] = self.cursor.fetchone()['count']
        
        # Active rentals
        self.cursor.execute("SELECT COUNT(*) as count FROM rentals WHERE status = 'active'")
        stats['active_rentals'] = self.cursor.fetchone()['count']
        
        # Total renters
        self.cursor.execute("SELECT COUNT(*) as count FROM renters")
        stats['total_renters'] = self.cursor.fetchone()['count']
        
        # Paid rentals
        self.cursor.execute("SELECT COUNT(*) as count FROM rentals WHERE payment_status = 'paid' AND status = 'active'")
        stats['paid_rentals'] = self.cursor.fetchone()['count']
        
        # Unpaid rentals
        self.cursor.execute("SELECT COUNT(*) as count FROM rentals WHERE payment_status = 'unpaid' AND status = 'active'")
        stats['unpaid_rentals'] = self.cursor.fetchone()['count']
        
        # Unpaid payments count (legacy support)
        self.cursor.execute("SELECT COUNT(*) as count FROM payments WHERE status = 'unpaid'")
        stats['unpaid_count'] = self.cursor.fetchone()['count']
        
        # Total income
        stats['total_income'] = self.get_total_income()
        
        return stats
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
