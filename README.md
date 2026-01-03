# Rental Management System - Complete Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Database Design](#database-design)
4. [Installation Guide](#installation-guide)
5. [User Guide](#user-guide)
6. [API Reference](#api-reference)
7. [Development Notes](#development-notes)

---

## 1. Project Overview

### 1.1 Purpose
The Rental Management System is a desktop application designed to manage the rental of beds and equipment for small businesses. It provides complete tracking of products, rentals, payments, and generates reminders for unpaid monthly payments.

### 1.2 Key Features
- ✅ **Product Management**: Add, edit, delete products (beds and equipment)
- ✅ **Renter Management**: Store and manage renter information
- ✅ **Rental Tracking**: Create rentals with monthly or yearly billing
- ✅ **Payment Management**: Track payments, mark as paid/unpaid
- ✅ **Cost Calculation**: Automatic calculation of monthly and yearly costs
- ✅ **Payment Reminders**: Display unpaid monthly payments
- ✅ **Dashboard**: Statistics and quick overview
- ✅ **Offline Operation**: Works completely offline with local SQLite database

### 1.3 Technology Stack
- **Language**: Python 3.8+
- **GUI Framework**: PyQt5
- **Database**: SQLite3
- **Architecture**: MVC (Model-View-Controller) pattern

---

## 2. System Architecture

### 2.1 Application Structure
```
rental-management/
│
├── main.py                    # Main application entry point
├── database.py                # Database handler (Model layer)
├── database_schema.sql        # Database schema definition
│
├── product_window.py          # Product management UI
├── rental_window.py           # Rental creation UI
├── payment_window.py          # Payment tracking UI
│
├── UML_DIAGRAMS.md           # UML diagrams documentation
├── README.md                  # This file
│
└── rental_management.db       # SQLite database (auto-created)
```

### 2.2 Design Patterns
- **MVC Pattern**: Separation of data (Model), UI (View), and logic (Controller)
- **Repository Pattern**: DatabaseHandler acts as a repository for data access
- **Observer Pattern**: UI refreshes when data changes

---

## 3. Database Design

### 3.1 Tables

#### Products Table
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('bed', 'equipment')),
    rental_price REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Renters Table
```sql
CREATE TABLE renters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    address TEXT,
    id_number TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Rentals Table
```sql
CREATE TABLE rentals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    renter_id INTEGER NOT NULL,
    billing_type TEXT NOT NULL CHECK(billing_type IN ('monthly', 'yearly')),
    rental_price REAL NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'returned')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (renter_id) REFERENCES renters(id) ON DELETE CASCADE
);
```

#### Payments Table
```sql
CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rental_id INTEGER NOT NULL,
    payment_date DATE NOT NULL,
    amount REAL NOT NULL,
    payment_month TEXT NOT NULL,  -- Format: YYYY-MM
    status TEXT NOT NULL DEFAULT 'unpaid' CHECK(status IN ('paid', 'unpaid')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rental_id) REFERENCES rentals(id) ON DELETE CASCADE
);
```

### 3.2 Relationships
- One **Product** → Many **Rentals** (1:N)
- One **Renter** → Many **Rentals** (1:N)
- One **Rental** → Many **Payments** (1:N)

### 3.3 Views
- **active_rentals**: Shows all active rentals with product and renter info
- **unpaid_payments**: Shows all unpaid payments with rental details

---

## 4. Installation Guide

### 4.1 Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### 4.2 Installation Steps

#### Step 1: Install Python
Download and install Python from [python.org](https://www.python.org/downloads/)

#### Step 2: Install PyQt5
```bash
pip install PyQt5
```

#### Step 3: Download Application Files
Place all application files in a single directory:
- main.py
- database.py
- database_schema.sql
- product_window.py
- rental_window.py
- payment_window.py

#### Step 4: Run the Application
```bash
python main.py
```

### 4.3 Requirements File
Create a `requirements.txt` file:
```
PyQt5==5.15.9
```

Install all dependencies:
```bash
pip install -r requirements.txt
```

---

## 5. User Guide

### 5.1 Dashboard
The main dashboard displays:
- **Statistics Cards**: Total products, active rentals, total renters, unpaid payments, total income
- **Recent Active Rentals**: List of currently active rentals
- **Payment Reminders**: List of unpaid monthly payments
- **Quick Actions**: Buttons to create products, rentals, or view payments

### 5.2 Product Management

#### Adding a Product
1. Click "➕ Add Product" button
2. Enter product name
3. Select type (bed or equipment)
4. Enter rental price
5. Click "💾 Save"

#### Editing a Product
1. Go to "📦 Products" tab
2. Select a product from the table
3. Click "✏️ Edit Product"
4. Modify details
5. Click "💾 Save"

#### Deleting a Product
1. Select a product from the table
2. Click "🗑️ Delete Product"
3. Confirm deletion

### 5.3 Rental Management

#### Creating a Rental
1. Click "📋 New Rental" button
2. Select a product from dropdown
3. Choose existing renter OR create new renter:
   - **Existing**: Select from dropdown
   - **New**: Uncheck "Select Existing Renter" and fill in details
4. Select billing type (monthly or yearly)
5. Set rental price (auto-filled from product)
6. Choose start date and end date
7. Review cost summary
8. Click "💾 Create Rental"

**Note**: Payment schedule is automatically created based on billing type.

#### Marking as Returned
1. Go to "📋 Rentals" tab
2. Select a rental
3. Click "✅ Mark as Returned"
4. Confirm

### 5.4 Payment Management

#### Viewing Payments
1. Click "💰 View Payments" or go to "💰 Payments" tab
2. Select a rental from dropdown
3. View all payments with status (PAID/UNPAID)

#### Marking Payment as Paid
1. Select rental
2. Select one or more payments from the table
3. Click "✅ Mark as Paid"
4. Confirm

#### Payment Summary
The payment window shows:
- **Paid**: Total amount paid
- **Unpaid**: Total amount unpaid
- **Total**: Total expected amount

### 5.5 Cost Calculations

#### Monthly Rental
- User sets monthly price
- System creates one payment per month from start to end date
- Yearly cost = Monthly price × 12

#### Yearly Rental
- User sets yearly price
- System creates one payment per year
- Monthly equivalent = Yearly price ÷ 12

---

## 6. API Reference

### 6.1 DatabaseHandler Class

#### Product Methods
```python
add_product(name: str, product_type: str, rental_price: float) -> int
get_all_products() -> List[Dict]
get_product_by_id(product_id: int) -> Optional[Dict]
update_product(product_id: int, name: str, product_type: str, rental_price: float)
delete_product(product_id: int)
```

#### Renter Methods
```python
add_renter(full_name: str, phone: str, email: str, address: str, id_number: str) -> int
get_all_renters() -> List[Dict]
get_renter_by_id(renter_id: int) -> Optional[Dict]
update_renter(renter_id: int, full_name: str, phone: str, email: str, address: str, id_number: str)
delete_renter(renter_id: int)
```

#### Rental Methods
```python
add_rental(product_id: int, renter_id: int, billing_type: str, 
           rental_price: float, start_date: str, end_date: str) -> int
get_all_rentals() -> List[Dict]
get_active_rentals() -> List[Dict]
get_rental_by_id(rental_id: int) -> Optional[Dict]
update_rental_status(rental_id: int, status: str)
```

#### Payment Methods
```python
get_payments_by_rental(rental_id: int) -> List[Dict]
get_unpaid_payments() -> List[Dict]
mark_payment_paid(payment_id: int, notes: str)
mark_payment_unpaid(payment_id: int)
```

#### Statistics Methods
```python
get_total_income() -> float
get_income_by_rental(rental_id: int) -> Tuple[float, float]
get_dashboard_stats() -> Dict
```

### 6.2 Example Usage

```python
from database import DatabaseHandler

# Initialize database
db = DatabaseHandler()

# Add a product
product_id = db.add_product("Queen Bed", "bed", 50.0)

# Add a renter
renter_id = db.add_renter("John Doe", "555-1234", "john@email.com", "123 Main St", "ID123")

# Create a rental
rental_id = db.add_rental(
    product_id=product_id,
    renter_id=renter_id,
    billing_type="monthly",
    rental_price=50.0,
    start_date="2026-01-01",
    end_date="2026-12-31"
)

# Get unpaid payments
unpaid = db.get_unpaid_payments()

# Mark payment as paid
db.mark_payment_paid(payment_id=1, notes="Paid by cash")

# Get statistics
stats = db.get_dashboard_stats()
print(f"Total Income: ${stats['total_income']:.2f}")
```

---

## 7. Development Notes

### 7.1 Code Organization

#### main.py
- Main application window
- Dashboard with statistics
- Navigation tabs
- Quick actions

#### database.py
- All database operations
- CRUD operations for all entities
- Payment schedule generation
- Statistics calculations

#### Window Classes
- **ProductWindow**: Add/edit products
- **RentalWindow**: Create new rentals
- **PaymentWindow**: View and manage payments

### 7.2 Key Design Decisions

#### Automatic Payment Schedule
When a rental is created, the system automatically generates payment records based on:
- **Monthly**: One payment per month from start to end date
- **Yearly**: One payment per year

All payments are initially marked as "unpaid".

#### Cascade Deletion
When a product or renter is deleted, all associated rentals and payments are also deleted (ON DELETE CASCADE).

#### Status Management
- Rentals: **active** or **returned**
- Payments: **paid** or **unpaid**

### 7.3 Styling
The application uses a modern, clean design with:
- Color-coded statistics cards
- Responsive tables with sorting
- Modal dialogs for data entry
- Hover effects on buttons
- Custom fonts and spacing

### 7.4 Future Enhancements
Potential features to add:
1. **Export to PDF/Excel**: Generate reports
2. **Email Reminders**: Automatic email notifications for unpaid payments
3. **Multi-user Support**: User authentication and roles
4. **Advanced Reporting**: Charts and graphs
5. **Backup/Restore**: Database backup functionality
6. **Search/Filter**: Advanced filtering in tables
7. **Print Receipts**: Generate payment receipts
8. **SMS Notifications**: Send payment reminders via SMS

### 7.5 Error Handling
The application includes error handling for:
- Database connection failures
- Invalid input validation
- Missing required fields
- Constraint violations
- File access errors

### 7.6 Performance Considerations
- Indexed columns for faster queries
- Efficient SQL joins
- Lazy loading of data
- Auto-refresh with 30-second timer

### 7.7 Security Notes
- Local database (no network exposure)
- Single-user system (no authentication required)
- Data stored in local file system
- No sensitive data encryption (can be added if needed)

---

## 8. Troubleshooting

### Common Issues

#### Application won't start
**Problem**: Missing PyQt5
**Solution**: 
```bash
pip install PyQt5
```

#### Database error on startup
**Problem**: Corrupted database file
**Solution**: Delete `rental_management.db` and restart the application

#### Cannot create rental
**Problem**: No products or renters exist
**Solution**: Create at least one product and one renter first

#### Payments not showing
**Problem**: No rental selected
**Solution**: Select a rental from the dropdown in Payment window

---

## 9. Support and Contact

For questions, bug reports, or feature requests:
- Check the documentation first
- Review the UML diagrams for system understanding
- Examine the source code comments
- Test with sample data

---

## 10. License

This is a sample application for educational purposes.
Free to use, modify, and distribute.

---

**Version**: 1.0  
**Date**: January 2026  
**Author**: Ayoub - Rental Management System
