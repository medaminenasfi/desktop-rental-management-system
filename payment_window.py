"""
Payment Tracking Window
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QMessageBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QComboBox, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor


class PaymentWindow(QDialog):
    """Window for viewing and managing payments"""
    
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.parent_window = parent
        self.current_rental_id = None
        self.init_ui()
        self.load_rentals()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Payment Management")
        self.setGeometry(100, 100, 1000, 700)
        self.setModal(True)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title_label = QLabel("Payment Management")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Rental selection
        rental_group = QGroupBox("Select Rental")
        rental_layout = QFormLayout()
        
        self.rental_combo = QComboBox()
        self.rental_combo.currentIndexChanged.connect(self.rental_selected)
        rental_layout.addRow("Rental:", self.rental_combo)
        
        self.rental_info_label = QLabel("Select a rental to view payments")
        self.rental_info_label.setWordWrap(True)
        rental_layout.addRow("Info:", self.rental_info_label)
        
        rental_group.setLayout(rental_layout)
        layout.addWidget(rental_group)
        
        # Payment summary
        summary_group = QGroupBox("Payment Summary")
        summary_layout = QHBoxLayout()
        
        self.paid_label = QLabel("Paid: $0.00")
        self.paid_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.paid_label.setStyleSheet("color: #2ecc71;")
        
        self.unpaid_label = QLabel("Unpaid: $0.00")
        self.unpaid_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.unpaid_label.setStyleSheet("color: #e74c3c;")
        
        self.total_label = QLabel("Total: $0.00")
        self.total_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.total_label.setStyleSheet("color: #3498db;")
        
        summary_layout.addWidget(self.paid_label)
        summary_layout.addWidget(self.unpaid_label)
        summary_layout.addWidget(self.total_label)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        self.btn_mark_paid = QPushButton("✅ Mark as Paid")
        self.btn_mark_paid.clicked.connect(self.mark_selected_paid)
        
        self.btn_mark_unpaid = QPushButton("❌ Mark as Unpaid")
        self.btn_mark_unpaid.clicked.connect(self.mark_selected_unpaid)
        
        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.clicked.connect(self.refresh_payments)
        
        btn_layout.addWidget(self.btn_mark_paid)
        btn_layout.addWidget(self.btn_mark_unpaid)
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # Payments table
        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(6)
        self.payments_table.setHorizontalHeaderLabels([
            "ID", "Payment Month", "Amount", "Due Date", "Status", "Notes"
        ])
        self.payments_table.horizontalHeader().setStretchLastSection(True)
        self.payments_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.payments_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.payments_table.setSelectionMode(QTableWidget.MultiSelection)
        
        layout.addWidget(self.payments_table)
        
        # Close button
        btn_close_layout = QHBoxLayout()
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.close)
        btn_close_layout.addStretch()
        btn_close_layout.addWidget(self.btn_close)
        
        layout.addLayout(btn_close_layout)
        
        # Apply styles
        self.apply_styles()
    
    def load_rentals(self):
        """Load all rentals into combo box"""
        rentals = self.db.get_all_rentals()
        self.rental_combo.clear()
        self.rental_combo.addItem("-- Select Rental --", None)
        
        for rental in rentals:
            display_text = (f"Rental #{rental['id']} - {rental['product_name']} - "
                          f"{rental['renter_name']} ({rental['status']})")
            self.rental_combo.addItem(display_text, rental['id'])
    
    def rental_selected(self):
        """Handle rental selection"""
        rental_id = self.rental_combo.currentData()
        
        if rental_id:
            self.current_rental_id = rental_id
            rental = self.db.get_rental_by_id(rental_id)
            
            if rental:
                info_text = (f"Product: {rental['product_name']}\n"
                           f"Renter: {rental['renter_name']}\n"
                           f"Billing: {rental['billing_type']}\n"
                           f"Price: {rental['rental_price']:.3f} TND\n"
                           f"Period: {rental['start_date']} to {rental['end_date'] or 'Ongoing'}")
                self.rental_info_label.setText(info_text)
                
                self.load_payments()
        else:
            self.current_rental_id = None
            self.rental_info_label.setText("Select a rental to view payments")
            self.payments_table.setRowCount(0)
            self.update_summary(0, 0, 0)
    
    def load_payments(self):
        """Load payments for selected rental"""
        if not self.current_rental_id:
            return
        
        payments = self.db.get_payments_by_rental(self.current_rental_id)
        self.payments_table.setRowCount(len(payments))
        
        total_paid = 0
        total_unpaid = 0
        
        for row, payment in enumerate(payments):
            # ID
            self.payments_table.setItem(row, 0, QTableWidgetItem(str(payment['id'])))
            
            # Payment month
            self.payments_table.setItem(row, 1, QTableWidgetItem(payment['payment_month']))
            
            # Amount
            amount_item = QTableWidgetItem(f"{payment['amount']:.3f} TND")
            self.payments_table.setItem(row, 2, amount_item)
            
            # Due date
            self.payments_table.setItem(row, 3, QTableWidgetItem(payment['payment_date']))
            
            # Status
            status_item = QTableWidgetItem(payment['status'].upper())
            if payment['status'] == 'paid':
                status_item.setForeground(QColor("#2ecc71"))
                status_item.setFont(QFont("Arial", 10, QFont.Bold))
                total_paid += payment['amount']
            else:
                status_item.setForeground(QColor("#e74c3c"))
                status_item.setFont(QFont("Arial", 10, QFont.Bold))
                total_unpaid += payment['amount']
            
            self.payments_table.setItem(row, 4, status_item)
            
            # Notes
            notes = payment.get('notes', '') or ''
            self.payments_table.setItem(row, 5, QTableWidgetItem(notes))
        
        self.update_summary(total_paid, total_unpaid, total_paid + total_unpaid)
    
    def update_summary(self, paid, unpaid, total):
        """Update payment summary labels"""
        self.paid_label.setText(f"Paid: {paid:.3f} TND")
        self.unpaid_label.setText(f"Unpaid: {unpaid:.3f} TND")
        self.total_label.setText(f"Total: {total:.3f} TND")
    
    def mark_selected_paid(self):
        """Mark selected payments as paid"""
        selected_rows = self.payments_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select payments to mark as paid")
            return
        
        payment_ids = []
        for row in selected_rows:
            payment_id = int(self.payments_table.item(row.row(), 0).text())
            payment_ids.append(payment_id)
        
        reply = QMessageBox.question(self, "Confirm", 
                                     f"Mark {len(payment_ids)} payment(s) as paid?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                for payment_id in payment_ids:
                    self.db.mark_payment_paid(payment_id, "Marked paid manually")
                
                self.load_payments()
                
                if self.parent_window:
                    self.parent_window.load_dashboard_data()
                    self.parent_window.load_unpaid_payments()
                
                QMessageBox.information(self, "Success", 
                                       f"{len(payment_ids)} payment(s) marked as paid")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update payments: {str(e)}")
    
    def mark_selected_unpaid(self):
        """Mark selected payments as unpaid"""
        selected_rows = self.payments_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select payments to mark as unpaid")
            return
        
        payment_ids = []
        for row in selected_rows:
            payment_id = int(self.payments_table.item(row.row(), 0).text())
            payment_ids.append(payment_id)
        
        reply = QMessageBox.question(self, "Confirm", 
                                     f"Mark {len(payment_ids)} payment(s) as unpaid?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                for payment_id in payment_ids:
                    self.db.mark_payment_unpaid(payment_id)
                
                self.load_payments()
                
                if self.parent_window:
                    self.parent_window.load_dashboard_data()
                    self.parent_window.load_unpaid_payments()
                
                QMessageBox.information(self, "Success", 
                                       f"{len(payment_ids)} payment(s) marked as unpaid")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update payments: {str(e)}")
    
    def refresh_payments(self):
        """Refresh payment data"""
        if self.current_rental_id:
            self.load_payments()
        else:
            QMessageBox.information(self, "Info", "Please select a rental first")
    
    def apply_styles(self):
        """Apply custom styles"""
        self.setStyleSheet("""
            QDialog {
                background-color: #ecf0f1;
            }
            QLabel {
                font-size: 13px;
            }
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 13px;
                background-color: white;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
