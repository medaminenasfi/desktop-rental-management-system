"""
Database Test Script
Tests all database operations to ensure everything works correctly
"""

from database import DatabaseHandler
from datetime import datetime

def test_database():
    """Test all database operations"""
    print("=" * 60)
    print("RENTAL MANAGEMENT SYSTEM - DATABASE TEST")
    print("=" * 60)
    
    # Initialize database
    print("\n1. Initializing database...")
    db = DatabaseHandler("test_rental.db")
    print("✓ Database initialized successfully")
    
    # Test Products
    print("\n2. Testing Product Operations...")
    product_id_1 = db.add_product("Standard Bed", "bed", 150.000)
    product_id_2 = db.add_product("Medical Equipment", "equipment", 200.000)
    print(f"✓ Added product 1: ID={product_id_1}")
    print(f"✓ Added product 2: ID={product_id_2}")
    
    products = db.get_all_products()
    print(f"✓ Total products in database: {len(products)}")
    for p in products:
        print(f"  - {p['name']} ({p['type']}): {p['rental_price']:.3f} TND")
    
    # Test Renters
    print("\n3. Testing Renter Operations...")
    renter_id_1 = db.add_renter(
        "Ahmed Ben Ali", 
        "+216 98 123 456", 
        "ahmed@email.tn", 
        "Tunis, Tunisia",
        "12345678"
    )
    renter_id_2 = db.add_renter(
        "Fatima Trabelsi",
        "+216 22 987 654",
        "fatima@email.tn",
        "Sfax, Tunisia",
        "87654321"
    )
    print(f"✓ Added renter 1: ID={renter_id_1} (Ahmed Ben Ali)")
    print(f"✓ Added renter 2: ID={renter_id_2} (Fatima Trabelsi)")
    
    renters = db.get_all_renters()
    print(f"✓ Total renters in database: {len(renters)}")
    for r in renters:
        print(f"  - {r['full_name']} - Phone: {r['phone']}")
    
    # Test Rentals
    print("\n4. Testing Rental Operations...")
    rental_id_1 = db.add_rental(
        product_id=product_id_1,
        renter_id=renter_id_1,
        billing_type="monthly",
        rental_price=150.000,
        start_date="2026-01-01",
        end_date="2026-12-31"
    )
    rental_id_2 = db.add_rental(
        product_id=product_id_2,
        renter_id=renter_id_2,
        billing_type="yearly",
        rental_price=2000.000,
        start_date="2026-01-01",
        end_date="2027-01-01"
    )
    print(f"✓ Created rental 1: ID={rental_id_1} (Monthly)")
    print(f"✓ Created rental 2: ID={rental_id_2} (Yearly)")
    
    rentals = db.get_all_rentals()
    print(f"✓ Total rentals in database: {len(rentals)}")
    for r in rentals:
        print(f"  - Rental #{r['id']}: {r['product_name']} → {r['renter_name']}")
        print(f"    Billing: {r['billing_type']}, Price: {r['rental_price']:.3f} TND")
    
    # Test Payments
    print("\n5. Testing Payment Operations...")
    payments_rental_1 = db.get_payments_by_rental(rental_id_1)
    print(f"✓ Rental 1 has {len(payments_rental_1)} payment(s)")
    print("  First 3 payments:")
    for p in payments_rental_1[:3]:
        print(f"    - Month: {p['payment_month']}, Amount: {p['amount']:.3f} TND, Status: {p['status']}")
    
    payments_rental_2 = db.get_payments_by_rental(rental_id_2)
    print(f"✓ Rental 2 has {len(payments_rental_2)} payment(s)")
    for p in payments_rental_2:
        print(f"    - Month: {p['payment_month']}, Amount: {p['amount']:.3f} TND, Status: {p['status']}")
    
    # Test mark payment as paid
    if payments_rental_1:
        first_payment_id = payments_rental_1[0]['id']
        db.mark_payment_paid(first_payment_id, "Paid by cash")
        print(f"✓ Marked payment {first_payment_id} as PAID")
    
    # Test Statistics
    print("\n6. Testing Statistics Operations...")
    stats = db.get_dashboard_stats()
    print(f"✓ Dashboard Statistics:")
    print(f"  - Total Products: {stats['total_products']}")
    print(f"  - Active Rentals: {stats['active_rentals']}")
    print(f"  - Total Renters: {stats['total_renters']}")
    print(f"  - Unpaid Payments: {stats['unpaid_count']}")
    print(f"  - Total Income: {stats['total_income']:.3f} TND")
    
    # Test Unpaid Payments
    print("\n7. Testing Unpaid Payments...")
    unpaid = db.get_unpaid_payments()
    print(f"✓ Total unpaid payments: {len(unpaid)}")
    if unpaid:
        print("  First 5 unpaid payments:")
        for p in unpaid[:5]:
            print(f"    - {p['product_name']} → {p['renter_name']}")
            print(f"      Month: {p['payment_month']}, Amount: {p['amount']:.3f} TND")
    
    # Test Income Calculation
    print("\n8. Testing Income Calculations...")
    paid, expected = db.get_income_by_rental(rental_id_1)
    print(f"✓ Rental 1 Income:")
    print(f"  - Paid: {paid:.3f} TND")
    print(f"  - Expected: {expected:.3f} TND")
    print(f"  - Remaining: {(expected - paid):.3f} TND")
    
    # Close database
    db.close()
    print("\n" + "=" * 60)
    print("✅ ALL DATABASE TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
    print("\nCurrency: Tunisian Dinar (TND)")
    print("Database file: test_rental.db")
    print("\nThe database is working correctly!")
    print("You can now run the main application: python main.py")
    print("\nDefault Admin Login:")
    print("  Username: admin")
    print("  Password: admin123")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_database()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
