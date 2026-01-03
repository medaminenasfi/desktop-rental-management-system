"""
Main Application Window for Rental Management System
"""

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QTabWidget, QFrame,
                             QHeaderView, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon
from database import DatabaseHandler
from product_window import ProductWindow
from rental_window import RentalWindow
from login_window import LoginWindow


class MainWindow(QMainWindow):
    """Main application window with dashboard and navigation"""
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseHandler()
        self.init_ui()
        self.load_dashboard_data()
        
        # Auto-refresh dashboard every 30 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_dashboard_data)
        self.timer.start(30000)  # 30 seconds
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Système de Gestion de Location")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title and logout
        title_layout = QHBoxLayout()
        
        title = QLabel("Système de Gestion de Location")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; padding: 20px;")
        
        btn_logout = QPushButton("🚪 Déconnexion")
        btn_logout.clicked.connect(self.logout)
        btn_logout.setMinimumWidth(140)
        btn_logout.setMinimumHeight(40)
        btn_logout.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e74c3c, stop:1 #c0392b);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #a93226;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #c0392b, stop:1 #a93226);
                border: 2px solid #922b21;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #922b21, stop:1 #78281f);
            }""")
        
        title_layout.addStretch()
        title_layout.addWidget(title, 1)
        title_layout.addWidget(btn_logout)
        
        main_layout.addLayout(title_layout)
        
        # Create tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Add tabs
        self.create_dashboard_tab()
        self.create_products_tab()
        self.create_rentals_tab()
        self.create_tenants_tab()
        
        # Style
        self.apply_styles()
    
    def create_dashboard_tab(self):
        """Create dashboard tab with statistics"""
        dashboard_widget = QWidget()
        layout = QVBoxLayout()
        dashboard_widget.setLayout(layout)
        
        # Statistics cards
        stats_layout = QHBoxLayout()
        
        self.stat_products = self.create_stat_card("Total Produits", "0", "#3498db", lambda: self.tabs.setCurrentIndex(1))
        self.stat_rentals = self.create_stat_card("Locations Actives", "0", "#2ecc71", lambda: self.tabs.setCurrentIndex(2))
        self.stat_renters = self.create_stat_card("Total Locataires", "0", "#9b59b6", lambda: self.tabs.setCurrentIndex(2))
        self.stat_paid = self.create_stat_card("Locations Payées", "0", "#27ae60", lambda: self.tabs.setCurrentIndex(2))
        self.stat_unpaid = self.create_stat_card("Locations Impayées", "0", "#e74c3c", lambda: self.tabs.setCurrentIndex(2))
        
        stats_layout.addWidget(self.stat_products)
        stats_layout.addWidget(self.stat_rentals)
        stats_layout.addWidget(self.stat_renters)
        stats_layout.addWidget(self.stat_paid)
        stats_layout.addWidget(self.stat_unpaid)
        
        layout.addLayout(stats_layout)
        
        # Quick actions
        quick_actions = QGroupBox("Actions Rapides")
        quick_layout = QHBoxLayout()
        
        btn_new_product = QPushButton("➕ Nouveau Produit")
        btn_new_product.clicked.connect(self.open_product_window)
        btn_new_product.setMinimumHeight(50)
        
        btn_new_rental = QPushButton("📋 Nouvelle Location")
        btn_new_rental.clicked.connect(self.open_rental_window)
        btn_new_rental.setMinimumHeight(50)
        
        quick_layout.addWidget(btn_new_product)
        quick_layout.addWidget(btn_new_rental)
        
        quick_actions.setLayout(quick_layout)
        layout.addWidget(quick_actions)
        
        # Recent rentals
        recent_group = QGroupBox("Locations Actives Récentes")
        recent_layout = QVBoxLayout()
        
        self.recent_rentals_table = QTableWidget()
        self.recent_rentals_table.setColumnCount(6)
        self.recent_rentals_table.setHorizontalHeaderLabels([
            "Produit", "Locataire", "Téléphone", "Facturation", "Prix", "Date Début"
        ])
        self.recent_rentals_table.horizontalHeader().setStretchLastSection(True)
        self.recent_rentals_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.recent_rentals_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        recent_layout.addWidget(self.recent_rentals_table)
        recent_group.setLayout(recent_layout)
        layout.addWidget(recent_group)
        
        # Payment Reminders - Monthly unpaid rentals
        reminders_group = QGroupBox("🚨 Rappels de Paiement Mensuels")
        reminders_layout = QVBoxLayout()
        
        # Summary label
        self.reminders_summary = QLabel("Total à collecter: 0.000 TND")
        self.reminders_summary.setFont(QFont("Arial", 14, QFont.Bold))
        self.reminders_summary.setStyleSheet("color: #d32f2f; padding: 10px; background-color: #ffebee; border-radius: 5px;")
        self.reminders_summary.setAlignment(Qt.AlignCenter)
        reminders_layout.addWidget(self.reminders_summary)
        
        self.reminders_table = QTableWidget()
        self.reminders_table.setColumnCount(5)
        self.reminders_table.setHorizontalHeaderLabels([
            "Locataire", "Téléphone", "Produit", "Facturation", "Montant Mensuel"
        ])
        self.reminders_table.horizontalHeader().setStretchLastSection(True)
        self.reminders_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.reminders_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.reminders_table.setStyleSheet("""
            QTableWidget {
                background-color: #fff3cd;
                border: 2px solid #ffc107;
            }
            QHeaderView::section {
                background-color: #ffc107;
                color: #000;
            }
        """)
        
        reminders_layout.addWidget(self.reminders_table)
        reminders_group.setLayout(reminders_layout)
        layout.addWidget(reminders_group)
        
        self.tabs.addTab(dashboard_widget, "📊 Tableau de Bord")
    
    def create_stat_card(self, title, value, color, click_action=None):
        """Create a statistics card widget"""
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 10px;
                padding: 15px;
            }}
            QFrame:hover {{
                background-color: {color};
                border: 3px solid white;
            }}
            QLabel {{
                color: white;
            }}
        """)
        
        # Make cursor change to pointer when hovering
        if click_action:
            frame.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout()
        frame.setLayout(layout)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 28, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12))
        title_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(value_label)
        layout.addWidget(title_label)
        
        # Store reference for updating
        frame.value_label = value_label
        
        # Add click event
        if click_action:
            frame.mousePressEvent = lambda event: click_action()
        
        return frame
    
    def create_products_tab(self):
        """Create products management tab"""
        products_widget = QWidget()
        layout = QVBoxLayout()
        products_widget.setLayout(layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        btn_add = QPushButton("➕ Ajouter Produit")
        btn_add.clicked.connect(self.open_product_window)
        
        btn_edit = QPushButton("✏️ Modifier Produit")
        btn_edit.clicked.connect(self.edit_product)
        
        btn_delete = QPushButton("🗑️ Supprimer Produit")
        btn_delete.clicked.connect(self.delete_product)
        
        btn_refresh = QPushButton("🔄 Actualiser")
        btn_refresh.clicked.connect(self.load_products)
        
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_delete)
        btn_layout.addWidget(btn_refresh)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(4)
        self.products_table.setHorizontalHeaderLabels(["ID", "Nom", "Type", "Prix Location"])
        self.products_table.horizontalHeader().setStretchLastSection(True)
        self.products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.products_table)
        
        self.tabs.addTab(products_widget, "📦 Produits")
    
    def create_rentals_tab(self):
        """Create rentals management tab"""
        rentals_widget = QWidget()
        layout = QVBoxLayout()
        rentals_widget.setLayout(layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        btn_new = QPushButton("➕ Nouvelle Location")
        btn_new.clicked.connect(self.open_rental_window)
        
        btn_return = QPushButton("✅ Marquer Retourné")
        btn_return.clicked.connect(self.mark_rental_returned)
        
        btn_toggle_paid = QPushButton("💰 Basculer Statut Payé")
        btn_toggle_paid.clicked.connect(self.toggle_rental_paid_status)
        
        btn_delete = QPushButton("🗑️ Supprimer Location")
        btn_delete.clicked.connect(self.delete_rental)
        
        btn_refresh = QPushButton("🔄 Actualiser")
        btn_refresh.clicked.connect(self.load_rentals)
        
        btn_layout.addWidget(btn_new)
        btn_layout.addWidget(btn_return)
        btn_layout.addWidget(btn_toggle_paid)
        btn_layout.addWidget(btn_delete)
        btn_layout.addWidget(btn_refresh)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # Rentals table
        self.rentals_table = QTableWidget()
        self.rentals_table.setColumnCount(11)
        self.rentals_table.setHorizontalHeaderLabels([
            "ID", "Produit", "Locataire", "Téléphone", "Facturation", "Prix", "Date Début", "Statut", "Payé", "Total à Payer", "Montant Reçu"
        ])
        self.rentals_table.horizontalHeader().setStretchLastSection(True)
        self.rentals_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.rentals_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.rentals_table)
        
        self.tabs.addTab(rentals_widget, "📋 Locations")
    
    def create_tenants_tab(self):
        """Create tenants totals tab"""
        tenants_widget = QWidget()
        layout = QVBoxLayout()
        tenants_widget.setLayout(layout)
        
        # Title and summary
        title_layout = QHBoxLayout()
        
        title = QLabel("👥 Totaux par Locataire")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 10px;")
        
        btn_refresh = QPushButton("🔄 Actualiser")
        btn_refresh.clicked.connect(self.load_tenants_totals)
        btn_refresh.setMinimumHeight(40)
        
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(btn_refresh)
        
        layout.addLayout(title_layout)
        
        # Summary cards
        summary_layout = QHBoxLayout()
        
        self.tenants_total_received = self.create_stat_card("Total Reçu", "0.000 TND", "#27ae60")
        self.tenants_total_owed = self.create_stat_card("Total Dû", "0.000 TND", "#e74c3c")
        self.tenants_total_amount = self.create_stat_card("Total Global", "0.000 TND", "#3498db")
        
        summary_layout.addWidget(self.tenants_total_received)
        summary_layout.addWidget(self.tenants_total_owed)
        summary_layout.addWidget(self.tenants_total_amount)
        
        layout.addLayout(summary_layout)
        
        # Tenants table
        self.tenants_table = QTableWidget()
        self.tenants_table.setColumnCount(7)
        self.tenants_table.setHorizontalHeaderLabels([
            "Locataire", "Téléphone", "Total Locations", "Locations Payées", "Locations Impayées", 
            "Montant Reçu", "Montant Dû"
        ])
        self.tenants_table.horizontalHeader().setStretchLastSection(True)
        self.tenants_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tenants_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Style the table
        self.tenants_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)
        
        layout.addWidget(self.tenants_table)
        
        self.tabs.addTab(tenants_widget, "👥 Locataires")
    
    def load_dashboard_data(self):
        """Load dashboard statistics and tables"""
        stats = self.db.get_dashboard_stats()
        
        self.stat_products.value_label.setText(str(stats['total_products']))
        self.stat_rentals.value_label.setText(str(stats['active_rentals']))
        self.stat_renters.value_label.setText(str(stats['total_renters']))
        self.stat_paid.value_label.setText(str(stats.get('paid_rentals', 0)))
        self.stat_unpaid.value_label.setText(str(stats.get('unpaid_rentals', 0)))
        
        # Load recent rentals
        rentals = self.db.get_active_rentals()[:10]  # Top 10
        self.recent_rentals_table.setRowCount(len(rentals))
        
        for row, rental in enumerate(rentals):
            self.recent_rentals_table.setItem(row, 0, QTableWidgetItem(rental['product_name']))
            self.recent_rentals_table.setItem(row, 1, QTableWidgetItem(rental['renter_name']))
            self.recent_rentals_table.setItem(row, 2, QTableWidgetItem(rental['renter_phone'] or ''))
            self.recent_rentals_table.setItem(row, 3, QTableWidgetItem(rental['billing_type']))
            self.recent_rentals_table.setItem(row, 4, QTableWidgetItem(f"{rental['rental_price']:.3f} TND"))
            self.recent_rentals_table.setItem(row, 5, QTableWidgetItem(rental['start_date']))
        
        # Load payment reminders - unpaid rentals
        self.load_payment_reminders()
    
    def load_products(self):
        """Load products into table"""
        products = self.db.get_all_products()
        self.products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            self.products_table.setItem(row, 0, QTableWidgetItem(str(product['id'])))
            self.products_table.setItem(row, 1, QTableWidgetItem(product['name']))
            self.products_table.setItem(row, 2, QTableWidgetItem(product['type']))
            self.products_table.setItem(row, 3, QTableWidgetItem(f"{product['rental_price']:.3f} TND"))
    
    def load_payment_reminders(self):
        """Load payment reminders for unpaid rentals with total owed"""
        unpaid_rentals = self.db.get_unpaid_rentals_with_totals()
        self.reminders_table.setRowCount(len(unpaid_rentals))
        
        total_monthly = 0.0
        total_all_periods = 0.0
        
        for row, rental in enumerate(unpaid_rentals):
            self.reminders_table.setItem(row, 0, QTableWidgetItem(rental['renter_name']))
            self.reminders_table.setItem(row, 1, QTableWidgetItem(rental['renter_phone'] or ''))
            self.reminders_table.setItem(row, 2, QTableWidgetItem(rental['product_name']))
            billing_fr = 'mensuel' if rental['billing_type'] == 'monthly' else 'annuel'
            self.reminders_table.setItem(row, 3, QTableWidgetItem(billing_fr))
            self.reminders_table.setItem(row, 4, QTableWidgetItem(f"{rental['rental_price']:.3f} TND"))
            
            # Add to monthly total
            if rental['billing_type'] == 'monthly':
                total_monthly += rental['rental_price']
            else:  # yearly - show monthly equivalent
                total_monthly += rental['rental_price'] / 12
        
        # Calculate total owed across all periods (unpaid months)
        total_all_periods = self.db.get_total_unpaid_amount()
        
        # Update summary label with both amounts
        summary_text = f"""💰 IMPAYÉS | Ce mois: {total_monthly:.3f} TND | Total tous périodes: {total_all_periods:.3f} TND | 👥 {len(unpaid_rentals)} locataire(s)"""
        self.reminders_summary.setText(summary_text)
    
    def load_rentals(self):
        """Load rentals into table"""
        rentals = self.db.get_all_rentals()
        self.rentals_table.setRowCount(len(rentals))
        
        for row, rental in enumerate(rentals):
            self.rentals_table.setItem(row, 0, QTableWidgetItem(str(rental['id'])))
            self.rentals_table.setItem(row, 1, QTableWidgetItem(rental['product_name']))
            self.rentals_table.setItem(row, 2, QTableWidgetItem(rental['renter_name']))
            self.rentals_table.setItem(row, 3, QTableWidgetItem(rental['renter_phone'] or ''))
            self.rentals_table.setItem(row, 4, QTableWidgetItem(rental['billing_type']))
            self.rentals_table.setItem(row, 5, QTableWidgetItem(f"{rental['rental_price']:.3f} TND"))
            self.rentals_table.setItem(row, 6, QTableWidgetItem(rental['start_date']))
            # Translate status to French
            status_fr = 'actif' if rental['status'] == 'active' else 'retourné'
            self.rentals_table.setItem(row, 7, QTableWidgetItem(status_fr))
            # Translate payment status to French
            paid_status = rental.get('payment_status', 'unpaid')
            paid_status_fr = 'payée' if paid_status == 'paid' else 'impayée'
            self.rentals_table.setItem(row, 8, QTableWidgetItem(paid_status_fr))
            
            # Get financial summary for this rental
            financial_summary = self.db.get_rental_financial_summary(rental['id'])
            total_to_pay = financial_summary['total_to_pay']
            total_received = financial_summary['total_received']
            
            self.rentals_table.setItem(row, 9, QTableWidgetItem(f"{total_to_pay:.3f} TND"))
            self.rentals_table.setItem(row, 10, QTableWidgetItem(f"{total_received:.3f} TND"))
    
    def load_tenants_totals(self):
        """Load tenant totals into table"""
        tenants = self.db.get_tenant_totals()
        self.tenants_table.setRowCount(len(tenants))
        
        total_received = 0.0
        total_owed = 0.0
        
        for row, tenant in enumerate(tenants):
            self.tenants_table.setItem(row, 0, QTableWidgetItem(tenant['renter_name']))
            self.tenants_table.setItem(row, 1, QTableWidgetItem(tenant['renter_phone'] or 'N/A'))
            self.tenants_table.setItem(row, 2, QTableWidgetItem(str(tenant['total_rentals'])))
            self.tenants_table.setItem(row, 3, QTableWidgetItem(str(tenant['paid_rentals'])))
            self.tenants_table.setItem(row, 4, QTableWidgetItem(str(tenant['unpaid_rentals'])))
            self.tenants_table.setItem(row, 5, QTableWidgetItem(f"{tenant['total_received']:.3f} TND"))
            self.tenants_table.setItem(row, 6, QTableWidgetItem(f"{tenant['total_owed']:.3f} TND"))
            
            # Add to totals
            total_received += tenant['total_received']
            total_owed += tenant['total_owed']
        
        # Update summary cards
        self.tenants_total_received.value_label.setText(f"{total_received:.3f} TND")
        self.tenants_total_owed.value_label.setText(f"{total_owed:.3f} TND")
        self.tenants_total_amount.value_label.setText(f"{total_received + total_owed:.3f} TND")
    
    def open_product_window(self):
        """Open product management window"""
        self.product_window = ProductWindow(self.db, self)
        self.product_window.show()
    
    def edit_product(self):
        """Edit selected product"""
        row = self.products_table.currentRow()
        if row >= 0:
            product_id = int(self.products_table.item(row, 0).text())
            product = self.db.get_product_by_id(product_id)
            self.product_window = ProductWindow(self.db, self, product)
            self.product_window.show()
        else:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un produit à modifier")
    
    def delete_product(self):
        """Delete selected product"""
        row = self.products_table.currentRow()
        if row >= 0:
            product_id = int(self.products_table.item(row, 0).text())
            reply = QMessageBox.question(self, "Confirmer Suppression", 
                                        "Êtes-vous sûr de vouloir supprimer ce produit?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    self.db.delete_product(product_id)
                    self.load_products()
                    self.load_dashboard_data()
                    QMessageBox.information(self, "Succès", "Produit supprimé avec succès")
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Échec de suppression du produit: {str(e)}")
        else:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un produit à supprimer")
    
    def open_rental_window(self):
        """Open rental management window"""
        self.rental_window = RentalWindow(self.db, self)
        self.rental_window.show()
    
    def mark_rental_returned(self):
        """Mark selected rental as returned"""
        row = self.rentals_table.currentRow()
        if row >= 0:
            rental_id = int(self.rentals_table.item(row, 0).text())
            reply = QMessageBox.question(self, "Confirmer Retour", 
                                        "Marquer cette location comme retournée?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.db.update_rental_status(rental_id, 'returned')
                self.load_rentals()
                self.load_dashboard_data()
                QMessageBox.information(self, "Succès", "Location marquée comme retournée")
        else:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une location")
    
    def toggle_rental_paid_status(self):
        """Toggle paid status for selected rental"""
        row = self.rentals_table.currentRow()
        if row >= 0:
            rental_id = int(self.rentals_table.item(row, 0).text())
            current_status_fr = self.rentals_table.item(row, 8).text()
            # Convert French to English for database operation (handle both 'payé' and 'payée')
            current_status = 'paid' if current_status_fr in ['payé', 'payée'] else 'unpaid'
            new_status = 'unpaid' if current_status == 'paid' else 'paid'
            status_fr = 'payée' if new_status == 'paid' else 'impayée'
            
            # Add confirmation dialog
            reply = QMessageBox.question(self, "Confirmation Changement Statut", 
                                        f"Êtes-vous sûr de vouloir marquer cette location comme {status_fr}?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    # Update database
                    self.db.update_rental_payment_status(rental_id, new_status)
                    
                    # Refresh all relevant data
                    self.load_rentals()
                    self.load_dashboard_data()
                    self.load_tenants_totals()
                    
                    QMessageBox.information(self, "Succès", f"Location marquée comme {status_fr}")
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Échec de mise à jour du statut: {str(e)}")
        else:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une location")
    
    def delete_rental(self):
        """Delete selected rental"""
        row = self.rentals_table.currentRow()
        if row >= 0:
            rental_id = int(self.rentals_table.item(row, 0).text())
            reply = QMessageBox.question(self, "Confirmer Suppression", 
                                        "Êtes-vous sûr de vouloir supprimer cette location?\nCela supprimera également tous les paiements associés.",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    self.db.delete_rental(rental_id)
                    self.load_rentals()
                    self.load_dashboard_data()
                    QMessageBox.information(self, "Succès", "Location supprimée avec succès")
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Échec de suppression de la location: {str(e)}")
        else:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une location à supprimer")
    
    def logout(self):
        """Logout and return to login window"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("🔐 Confirmation de Déconnexion")
        msg_box.setText("Êtes-vous sûr de vouloir vous déconnecter?")
        msg_box.setInformativeText("Toutes vos données non sauvegardées seront perdues.\nVous devrez vous reconnecter pour accéder à l'application.")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        # Style the message box
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #f8f9fa;
            }
            QMessageBox QLabel {
                color: #2c3e50;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        reply = msg_box.exec_()
        if reply == QMessageBox.Yes:
            self.close()
            login = LoginWindow()
            if login.exec_() == LoginWindow.Accepted and login.authenticated:
                window = MainWindow()
                window.show()
            else:
                sys.exit(0)
    
    def apply_styles(self):
        """Apply custom styles to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QComboBox {
                background-color: white;
                color: black;
                padding: 5px;
            }
            QComboBox:on {
                background-color: #ecf0f1;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #3498db;
                selection-color: white;
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
    
    def showEvent(self, event):
        """Handle window show event"""
        super().showEvent(event)
        self.load_products()
        self.load_rentals()
        self.load_tenants_totals()
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.db.close()
        event.accept()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Show login window first
    login = LoginWindow()
    if login.exec_() == LoginWindow.Accepted and login.authenticated:
        # Login successful, show main window
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    else:
        # Login cancelled or failed
        sys.exit(0)


if __name__ == "__main__":
    main()
