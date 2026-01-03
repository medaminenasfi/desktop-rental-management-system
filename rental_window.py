"""
Rental Management Window
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QMessageBox,
                             QFormLayout, QDoubleSpinBox, QDateEdit, QTextEdit,
                             QGroupBox, QCheckBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from datetime import datetime


class RentalWindow(QDialog):
    """Window for creating new rentals"""
    
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.parent_window = parent
        self.selected_renter_id = None
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Créer Nouvelle Location")
        self.setGeometry(150, 150, 700, 700)
        self.setModal(True)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title_label = QLabel("Créer Nouvelle Location")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Product selection
        product_group = QGroupBox("Sélectionner Produit")
        product_layout = QFormLayout()
        
        self.product_combo = QComboBox()
        self.product_combo.currentIndexChanged.connect(self.product_selected)
        product_layout.addRow("Produit:", self.product_combo)
        
        self.product_price_label = QLabel("0.000 TND")
        self.product_price_label.setFont(QFont("Arial", 12, QFont.Bold))
        product_layout.addRow("Prix Produit:", self.product_price_label)
        
        product_group.setLayout(product_layout)
        layout.addWidget(product_group)
        
        # Renter information
        renter_group = QGroupBox("Informations Locataire")
        renter_layout = QVBoxLayout()
        
        # Existing renter or new
        renter_type_layout = QHBoxLayout()
        
        self.existing_renter_radio = QCheckBox("Sélectionner Locataire Existant")
        self.existing_renter_radio.setChecked(True)
        self.existing_renter_radio.toggled.connect(self.toggle_renter_mode)
        
        renter_type_layout.addWidget(self.existing_renter_radio)
        renter_layout.addLayout(renter_type_layout)
        
        # Existing renter dropdown
        self.renter_combo = QComboBox()
        renter_layout.addWidget(self.renter_combo)
        
        # New renter form
        self.new_renter_form = QFormLayout()
        
        self.renter_name = QLineEdit()
        self.renter_name.setPlaceholderText("Nom complet")
        self.new_renter_form.addRow("Nom Complet:", self.renter_name)
        
        self.renter_phone = QLineEdit()
        self.renter_phone.setPlaceholderText("Numéro de téléphone")
        self.new_renter_form.addRow("Téléphone:", self.renter_phone)
        
        self.renter_email = QLineEdit()
        self.renter_email.setPlaceholderText("Adresse email")
        self.new_renter_form.addRow("Email:", self.renter_email)
        
        self.renter_address = QTextEdit()
        self.renter_address.setPlaceholderText("Adresse complète")
        self.renter_address.setMaximumHeight(80)
        self.new_renter_form.addRow("Adresse:", self.renter_address)
        
        self.renter_id_number = QLineEdit()
        self.renter_id_number.setPlaceholderText("Numéro CIN/Passeport")
        self.new_renter_form.addRow("Numéro CIN:", self.renter_id_number)
        
        renter_layout.addLayout(self.new_renter_form)
        
        # Hide new renter form initially
        self.set_new_renter_form_visible(False)
        
        renter_group.setLayout(renter_layout)
        layout.addWidget(renter_group)
        
        # Rental details
        rental_group = QGroupBox("Détails Location")
        rental_layout = QFormLayout()
        
        # Billing type
        self.billing_combo = QComboBox()
        self.billing_combo.addItems(["mensuel", "annuel"])
        self.billing_combo.currentIndexChanged.connect(self.calculate_cost)
        rental_layout.addRow("Type Facturation:", self.billing_combo)
        
        # Custom price
        self.custom_price = QDoubleSpinBox()
        self.custom_price.setRange(0, 1000000)
        self.custom_price.setDecimals(3)
        self.custom_price.setSuffix(" TND")
        self.custom_price.valueChanged.connect(self.calculate_cost)
        rental_layout.addRow("Prix Location:", self.custom_price)
        
        # Start date
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        rental_layout.addRow("Date Début:", self.start_date)
        
        # End date
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addYears(1))
        rental_layout.addRow("Date Fin (Optionnel):", self.end_date)
        
        # Payment status
        self.payment_status_combo = QComboBox()
        self.payment_status_combo.addItems(["impayé", "payé"])
        rental_layout.addRow("Statut Paiement:", self.payment_status_combo)
        
        rental_group.setLayout(rental_layout)
        layout.addWidget(rental_group)
        
        # Cost calculation
        cost_group = QGroupBox("Résumé Coûts")
        cost_layout = QFormLayout()
        
        self.monthly_cost_label = QLabel("0.000 TND")
        self.monthly_cost_label.setFont(QFont("Arial", 12, QFont.Bold))
        cost_layout.addRow("Coût Mensuel:", self.monthly_cost_label)
        
        self.yearly_cost_label = QLabel("0.000 TND")
        self.yearly_cost_label.setFont(QFont("Arial", 12, QFont.Bold))
        cost_layout.addRow("Coût Annuel:", self.yearly_cost_label)
        
        cost_group.setLayout(cost_layout)
        layout.addWidget(cost_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("💾 Créer Location")
        self.btn_save.clicked.connect(self.save_rental)
        
        self.btn_cancel = QPushButton("❌ Annuler")
        self.btn_cancel.clicked.connect(self.close)
        
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(btn_layout)
        
        # Apply styles
        self.apply_styles()
    
    def load_data(self):
        """Load products and renters"""
        # Load products
        products = self.db.get_all_products()
        self.product_combo.clear()
        self.product_combo.addItem("-- Sélectionner Produit --", None)
        for product in products:
            self.product_combo.addItem(
                f"{product['name']} ({product['type']}) - {product['rental_price']:.3f} TND",
                product
            )
        
        # Load renters
        renters = self.db.get_all_renters()
        self.renter_combo.clear()
        self.renter_combo.addItem("-- Sélectionner Locataire --", None)
        for renter in renters:
            self.renter_combo.addItem(
                f"{renter['full_name']} - {renter['phone'] or 'Pas de téléphone'}",
                renter['id']
            )
    
    def product_selected(self):
        """Handle product selection"""
        product = self.product_combo.currentData()
        if product:
            self.product_price_label.setText(f"{product['rental_price']:.3f} TND")
            self.custom_price.setValue(product['rental_price'])
            self.calculate_cost()
        else:
            self.product_price_label.setText("0.000 TND")
            self.custom_price.setValue(0)
    
    def toggle_renter_mode(self, checked):
        """Toggle between existing and new renter"""
        if checked:
            self.renter_combo.setEnabled(True)
            self.set_new_renter_form_visible(False)
        else:
            self.renter_combo.setEnabled(False)
            self.set_new_renter_form_visible(True)
    
    def set_new_renter_form_visible(self, visible):
        """Show or hide new renter form fields"""
        for i in range(self.new_renter_form.count()):
            item = self.new_renter_form.itemAt(i)
            if item.widget():
                item.widget().setVisible(visible)
    
    def calculate_cost(self):
        """Calculate and display costs"""
        price = self.custom_price.value()
        billing_type = self.billing_combo.currentText()
        
        if billing_type == "mensuel":
            monthly = price
            yearly = price * 12
        else:  # annuel
            monthly = price / 12
            yearly = price
        
        self.monthly_cost_label.setText(f"{monthly:.3f} TND")
        self.yearly_cost_label.setText(f"{yearly:.3f} TND")
    
    def save_rental(self):
        """Save rental to database"""
        # Validate product
        product = self.product_combo.currentData()
        if not product:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un produit")
            return
        
        # Get or create renter
        if self.existing_renter_radio.isChecked():
            renter_id = self.renter_combo.currentData()
            if not renter_id:
                QMessageBox.warning(self, "Attention", "Veuillez sélectionner un locataire")
                return
        else:
            # Create new renter
            name = self.renter_name.text().strip()
            if not name:
                QMessageBox.warning(self, "Attention", "Veuillez entrer le nom du locataire")
                return
            
            phone = self.renter_phone.text().strip()
            email = self.renter_email.text().strip()
            address = self.renter_address.toPlainText().strip()
            id_number = self.renter_id_number.text().strip()
            
            try:
                renter_id = self.db.add_renter(name, phone, email, address, id_number)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Échec de création du locataire: {str(e)}")
                return
        
        # Get rental details
        billing_type_fr = self.billing_combo.currentText()
        # Convert French to English for database
        billing_type = 'monthly' if billing_type_fr == 'mensuel' else 'yearly'
        rental_price = self.custom_price.value()
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        payment_status_fr = self.payment_status_combo.currentText()
        # Convert French to English for database
        payment_status = 'paid' if payment_status_fr == 'payé' else 'unpaid'
        
        if rental_price <= 0:
            QMessageBox.warning(self, "Attention", "Le prix de location doit être supérieur à 0")
            return
        
        try:
            # Create rental
            rental_id = self.db.add_rental(
                product['id'], 
                renter_id, 
                billing_type, 
                rental_price, 
                start_date, 
                end_date
            )
            
            # Set payment status
            self.db.update_rental_payment_status(rental_id, payment_status)
            
            QMessageBox.information(self, "Succès", 
                                   f"Location créée avec succès!\nID Location: {rental_id}")
            
            # Refresh parent window
            if self.parent_window:
                self.parent_window.load_rentals()
                self.parent_window.load_dashboard_data()
            
            self.close()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create rental: {str(e)}")
    
    def apply_styles(self):
        """Apply custom styles"""
        self.setStyleSheet("""
            QDialog {
                background-color: #ecf0f1;
            }
            QLabel {
                font-size: 13px;
            }
            QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit, QTextEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 13px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {
                border-color: #3498db;
            }
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #27ae60;
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
