# UML Diagrams for Rental Management System

## 1. Use Case Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                 Rental Management System                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│    ┌──────┐                                                 │
│    │Admin │                                                 │
│    │/Mgr  │                                                 │
│    └──┬───┘                                                 │
│       │                                                      │
│       ├──────> (Manage Products)                           │
│       │         ├── Add Product                             │
│       │         ├── Edit Product                            │
│       │         └── Delete Product                          │
│       │                                                      │
│       ├──────> (Manage Rentals)                            │
│       │         ├── Create Rental                           │
│       │         ├── View Rentals                            │
│       │         └── Mark as Returned                        │
│       │                                                      │
│       ├──────> (Manage Renters)                            │
│       │         ├── Add Renter                              │
│       │         ├── Edit Renter                             │
│       │         └── View Renter Info                        │
│       │                                                      │
│       ├──────> (Manage Payments)                           │
│       │         ├── View Payments                           │
│       │         ├── Mark Payment Paid                       │
│       │         └── View Unpaid Payments                    │
│       │                                                      │
│       ├──────> (View Dashboard)                            │
│       │         ├── View Statistics                         │
│       │         ├── View Payment Reminders                  │
│       │         └── View Recent Rentals                     │
│       │                                                      │
│       └──────> (Generate Reports)                          │
│                 ├── Calculate Total Income                  │
│                 └── View Cost Breakdown                     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 2. Class Diagram

```
┌───────────────────────────────────────────────────────────────────────┐
│                          CLASS DIAGRAM                                 │
└───────────────────────────────────────────────────────────────────────┘

┌────────────────────────────┐
│    DatabaseHandler         │
├────────────────────────────┤
│ - db_name: str            │
│ - connection: Connection   │
│ - cursor: Cursor          │
├────────────────────────────┤
│ + __init__(db_name)       │
│ + connect()               │
│ + create_tables()         │
│ + add_product()           │
│ + get_all_products()      │
│ + update_product()        │
│ + delete_product()        │
│ + add_renter()            │
│ + get_all_renters()       │
│ + add_rental()            │
│ + get_all_rentals()       │
│ + get_payments()          │
│ + mark_payment_paid()     │
│ + get_dashboard_stats()   │
│ + close()                 │
└────────────────────────────┘
         △
         │ uses
         │
┌────────┴──────────────────────────────────────────────┐
│                                                        │
│                                                        │
┌───────────────────┐  ┌──────────────────┐  ┌─────────────────┐
│   MainWindow      │  │  ProductWindow   │  │  RentalWindow   │
├───────────────────┤  ├──────────────────┤  ├─────────────────┤
│ - db: DB Handler  │  │ - db: DBHandler  │  │ - db: DBHandler │
│ - tabs: TabWidget │  │ - product: Dict  │  │ - parent: Widget│
├───────────────────┤  ├──────────────────┤  ├─────────────────┤
│ + init_ui()       │  │ + init_ui()      │  │ + init_ui()     │
│ + load_dashboard()│  │ + save_product() │  │ + save_rental() │
│ + load_products() │  │ + apply_styles() │  │ + load_data()   │
│ + load_rentals()  │  └──────────────────┘  │ + calculate()   │
│ + open_product()  │                         └─────────────────┘
│ + open_rental()   │  ┌──────────────────┐
│ + apply_styles()  │  │  PaymentWindow   │
└───────────────────┘  ├──────────────────┤
                       │ - db: DBHandler  │
                       │ - rental_id: int │
                       ├──────────────────┤
                       │ + init_ui()      │
                       │ + load_payments()│
                       │ + mark_paid()    │
                       │ + update_summary()│
                       └──────────────────┘
```

## 3. Entity-Relationship Diagram (ERD)

```
┌─────────────────────────────────────────────────────────────────┐
│                  DATABASE SCHEMA - ERD                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────┐
│     PRODUCTS        │
├─────────────────────┤
│ PK id (INT)        │
│    name (TEXT)     │
│    type (TEXT)     │
│    rental_price    │
│    created_at      │
└──────────┬──────────┘
           │
           │ 1
           │
           │ *
┌──────────▼──────────┐         ┌─────────────────────┐
│     RENTALS         │         │      RENTERS        │
├─────────────────────┤         ├─────────────────────┤
│ PK id (INT)        │    *    │ PK id (INT)        │
│ FK product_id      │◄────┐   │    full_name       │
│ FK renter_id       │─────┼──►│    phone           │
│    billing_type    │     1   │    email           │
│    rental_price    │         │    address         │
│    start_date      │         │    id_number       │
│    end_date        │         │    created_at      │
│    status          │         └─────────────────────┘
│    created_at      │
└──────────┬──────────┘
           │
           │ 1
           │
           │ *
┌──────────▼──────────┐
│     PAYMENTS        │
├─────────────────────┤
│ PK id (INT)        │
│ FK rental_id       │
│    payment_date    │
│    amount          │
│    payment_month   │
│    status          │
│    notes           │
│    created_at      │
└─────────────────────┘

Relationships:
- One PRODUCT can have many RENTALS (1:*)
- One RENTER can have many RENTALS (1:*)
- One RENTAL can have many PAYMENTS (1:*)
```

## 4. Sequence Diagram - Create Rental

```
User        RentalWindow    DatabaseHandler    Database
 │               │                │               │
 │──Select Product──►            │               │
 │               │                │               │
 │──Enter Renter Info──►         │               │
 │               │                │               │
 │──Set Dates & Price──►         │               │
 │               │                │               │
 │──Click Create──►              │               │
 │               │                │               │
 │               │──add_renter()──►              │
 │               │                │──INSERT───────►
 │               │                │◄──renter_id───│
 │               │                │               │
 │               │──add_rental()──►              │
 │               │                │──INSERT───────►
 │               │                │◄──rental_id───│
 │               │                │               │
 │               │──create_payment_schedule()──► │
 │               │                │──INSERT───────►
 │               │                │   (multiple)  │
 │               │                │◄──success─────│
 │               │◄──rental_id────│               │
 │               │                │               │
 │◄──Success Msg──               │               │
```

## 5. Activity Diagram - Payment Processing

```
        ┌─────────┐
        │  START  │
        └────┬────┘
             │
        ┌────▼────────────────┐
        │ Select Rental       │
        └────┬────────────────┘
             │
        ┌────▼────────────────┐
        │ Load Payments       │
        └────┬────────────────┘
             │
        ┌────▼────────────────┐
        │ Display Payment List│
        └────┬────────────────┘
             │
        ┌────▼────────────────┐
        │ Select Payment(s)   │
        └────┬────────────────┘
             │
        ┌────▼────────────────┐
     ┌──│ Mark as Paid?       │
     │  └────┬────────────────┘
     │       │ Yes
     │  ┌────▼────────────────┐
     │  │ Update Status = Paid│
     │  └────┬────────────────┘
     │       │
     │  ┌────▼────────────────┐
     │  │ Save to Database    │
     │  └────┬────────────────┘
     │       │
     │  ┌────▼────────────────┐
     │  │ Refresh Display     │
     │  └────┬────────────────┘
     │       │
     │  ┌────▼────────────────┐
     │  │ Update Dashboard    │
     │  └────┬────────────────┘
     │       │
     │       ▼
     │  ┌─────────┐
     └─►│   END   │
        └─────────┘
```

## 6. State Diagram - Rental Status

```
                    ┌──────────────┐
                    │    [NEW]     │
                    └──────┬───────┘
                           │
                           │ Create Rental
                           ▼
    ┌─────────────┐    ┌───────────────┐    ┌─────────────┐
    │   PENDING   │───►│    ACTIVE     │───►│  RETURNED   │
    └─────────────┘    └───────┬───────┘    └─────────────┘
          │                    │                     │
          │                    │                     │
          │           ┌────────▼────────┐           │
          └──────────►│   CANCELLED     │◄──────────┘
                      └─────────────────┘
                      
States:
- NEW: Rental being created
- PENDING: Rental created but not started
- ACTIVE: Ongoing rental with active payments
- RETURNED: Product returned, rental complete
- CANCELLED: Rental cancelled before completion
```

## 7. Component Diagram

```
┌───────────────────────────────────────────────────────────┐
│                    Application Layer                      │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Main      │  │  Product    │  │   Rental    │     │
│  │   Window    │  │   Window    │  │   Window    │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
│         │                │                │             │
│         └────────────────┼────────────────┘             │
│                          │                              │
└──────────────────────────┼──────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────┐
│                    Business Logic Layer                  │
├──────────────────────────┼──────────────────────────────┤
│                          │                              │
│                 ┌────────▼──────────┐                   │
│                 │  DatabaseHandler  │                   │
│                 │                   │                   │
│                 │ - Product CRUD    │                   │
│                 │ - Renter CRUD     │                   │
│                 │ - Rental CRUD     │                   │
│                 │ - Payment CRUD    │                   │
│                 │ - Reports/Stats   │                   │
│                 └────────┬──────────┘                   │
│                          │                              │
└──────────────────────────┼──────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────┐
│                    Data Access Layer                     │
├──────────────────────────┼──────────────────────────────┤
│                          │                              │
│                 ┌────────▼──────────┐                   │
│                 │   SQLite Database │                   │
│                 │                   │                   │
│                 │  - products       │                   │
│                 │  - renters        │                   │
│                 │  - rentals        │                   │
│                 │  - payments       │                   │
│                 └───────────────────┘                   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## 8. Deployment Diagram

```
┌─────────────────────────────────────────────────┐
│           Windows/Linux/macOS Desktop           │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌───────────────────────────────────────┐    │
│  │     Python 3.x Runtime Environment     │    │
│  ├───────────────────────────────────────┤    │
│  │                                         │    │
│  │  ┌─────────────────────────────────┐  │    │
│  │  │  Rental Management Application  │  │    │
│  │  │                                 │  │    │
│  │  │  - main.py                      │  │    │
│  │  │  - database.py                  │  │    │
│  │  │  - product_window.py            │  │    │
│  │  │  - rental_window.py             │  │    │
│  │  │  - payment_window.py            │  │    │
│  │  └─────────────────────────────────┘  │    │
│  │              ▲                         │    │
│  │              │ uses                    │    │
│  │              ▼                         │    │
│  │  ┌─────────────────────────────────┐  │    │
│  │  │        PyQt5 Framework          │  │    │
│  │  └─────────────────────────────────┘  │    │
│  │              ▲                         │    │
│  │              │ uses                    │    │
│  │              ▼                         │    │
│  │  ┌─────────────────────────────────┐  │    │
│  │  │       SQLite3 Library           │  │    │
│  │  └─────────────────────────────────┘  │    │
│  │              ▲                         │    │
│  │              │ stores                  │    │
│  │              ▼                         │    │
│  └───────────────────────────────────────┘    │
│                                                 │
│  ┌───────────────────────────────────────┐    │
│  │     Local File System                 │    │
│  ├───────────────────────────────────────┤    │
│  │  - rental_management.db               │    │
│  │  - database_schema.sql                │    │
│  └───────────────────────────────────────┘    │
│                                                 │
└─────────────────────────────────────────────────┘
```
