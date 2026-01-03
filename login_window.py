"""
Login Window for Admin Authentication
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class LoginWindow(QDialog):
    """Simple admin login window"""
    
    def __init__(self):
        super().__init__()
        self.authenticated = False
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Connexion Admin - Système de Gestion de Location")
        self.setGeometry(300, 300, 400, 300)
        self.setModal(True)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title = QLabel("🔐 Connexion Admin")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Entrez vos identifiants pour accéder au système")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d; padding: 10px;")
        layout.addWidget(subtitle)
        
        # Form
        form_layout = QFormLayout()
        
        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Entrer nom d'utilisateur")
        self.username_input.returnPressed.connect(self.login)
        form_layout.addRow("Nom d'utilisateur:", self.username_input)
        
        # Password with show/hide toggle
        password_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Entrer mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self.login)
        
        self.btn_show_password = QPushButton("👁️")
        self.btn_show_password.setMaximumWidth(40)
        self.btn_show_password.setCheckable(True)
        self.btn_show_password.clicked.connect(self.toggle_password_visibility)
        self.btn_show_password.setStyleSheet("""QPushButton {
            background-color: #95a5a6;
            padding: 10px;
        }
        QPushButton:checked {
            background-color: #3498db;
        }""")
        
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.btn_show_password)
        form_layout.addRow("Mot de passe:", password_layout)
        
        layout.addLayout(form_layout)
        
        # Default credentials info
        info_label = QLabel("Par défaut:  ")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #3498db; font-size: 11px; padding: 10px;")
        layout.addWidget(info_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_login = QPushButton("🔓 Connexion")
        self.btn_login.clicked.connect(self.login)
        self.btn_login.setDefault(True)
        
        self.btn_cancel = QPushButton("❌ Annuler")
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_login)
        btn_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(btn_layout)
        
        # Apply styles
        self.apply_styles()
        
        # Set focus
        self.username_input.setFocus()
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.btn_show_password.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
    
    def login(self):
        """Validate login credentials"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        # Simple authentication (in real app, use hashed passwords)
        if username == "admin" and password == "admin123":
            self.authenticated = True
            QMessageBox.information(self, "Succès", f"Bienvenue, {username}!")
            self.accept()
        else:
            QMessageBox.warning(self, "Échec de Connexion", 
                              "Nom d'utilisateur ou mot de passe invalide.\n\nIdentifiants par défaut:\nNom d'utilisateur: admin\nMot de passe: admin123")
            self.password_input.clear()
            self.password_input.setFocus()
    
    def apply_styles(self):
        """Apply custom styles"""
        self.setStyleSheet("""
            QDialog {
                background-color: #ecf0f1;
            }
            QLabel {
                font-size: 13px;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
                background-color: white;
                min-width: 250px;
            }
            QLineEdit:focus {
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
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton#btn_cancel {
                background-color: #e74c3c;
            }
            QPushButton#btn_cancel:hover {
                background-color: #c0392b;
            }
        """)
