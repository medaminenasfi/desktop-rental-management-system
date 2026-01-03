"""
Product Management Window
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QMessageBox,
                             QFormLayout, QDoubleSpinBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class ProductWindow(QDialog):
    """Window for adding/editing products"""
    
    def __init__(self, db, parent=None, product=None):
        super().__init__(parent)
        self.db = db
        self.product = product
        self.parent_window = parent
        self.init_ui()
        
        if product:
            self.load_product_data()
    
    def init_ui(self):
        """Initialize the user interface"""
        title = "Modifier Produit" if self.product else "Ajouter Nouveau Produit"
        self.setWindowTitle(title)
        self.setGeometry(200, 200, 500, 400)
        self.setModal(True)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Form
        form_layout = QFormLayout()
        
        # Product name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Entrer nom du produit")
        form_layout.addRow("Nom Produit:", self.name_input)
        
        # Product type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["lit", "équipement"])
        form_layout.addRow("Type Produit:", self.type_combo)
        
        # Rental price
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 1000000)
        self.price_input.setDecimals(3)
        self.price_input.setSuffix(" TND")
        self.price_input.setValue(0)
        form_layout.addRow("Prix Location:", self.price_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("💾 Enregistrer")
        self.btn_save.clicked.connect(self.save_product)
        
        self.btn_cancel = QPushButton("❌ Annuler")
        self.btn_cancel.clicked.connect(self.close)
        
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(btn_layout)
        
        # Apply styles
        self.apply_styles()
    
    def load_product_data(self):
        """Load existing product data into form"""
        self.name_input.setText(self.product['name'])
        # Convert English type to French
        type_fr = 'lit' if self.product['type'] == 'bed' else 'équipement'
        self.type_combo.setCurrentText(type_fr)
        self.price_input.setValue(self.product['rental_price'])
    
    def save_product(self):
        """Save product to database"""
        name = self.name_input.text().strip()
        product_type_fr = self.type_combo.currentText()
        # Convert French type to English for database
        product_type = 'bed' if product_type_fr == 'lit' else 'equipment'
        price = self.price_input.value()
        
        # Validation
        if not name:
            QMessageBox.warning(self, "Attention", "Veuillez entrer le nom du produit")
            return
        
        if price <= 0:
            QMessageBox.warning(self, "Attention", "Le prix doit être supérieur à 0")
            return
        
        try:
            if self.product:
                # Update existing product
                self.db.update_product(self.product['id'], name, product_type, price)
                QMessageBox.information(self, "Succès", "Produit mis à jour avec succès")
            else:
                # Add new product
                self.db.add_product(name, product_type, price)
                QMessageBox.information(self, "Succès", "Produit ajouté avec succès")
            
            # Refresh parent window
            if self.parent_window:
                self.parent_window.load_products()
                self.parent_window.load_dashboard_data()
            
            self.close()
        
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de sauvegarde du produit: {str(e)}")
    
    def apply_styles(self):
        """Apply custom styles"""
        self.setStyleSheet("""
            QDialog {
                background-color: #ecf0f1;
            }
            QLabel {
                font-size: 14px;
            }
            QLineEdit, QComboBox, QDoubleSpinBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {
                border-color: #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
