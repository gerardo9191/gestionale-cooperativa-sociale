"""
Contabilità Widget
==================

Widget per la gestione della contabilità generale.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTabWidget, QTableWidget, QTableWidgetItem, QTreeWidget,
    QMessageBox
)
from PySide6.QtGui import QFont

from ..config import Config
from ..controllers.contabilita_controller import ContabilitaController


class ContabilitaWidget(QWidget):
    """Widget per la gestione della contabilità generale."""
    
    def __init__(self, contabilita_controller: ContabilitaController, config: Config):
        super().__init__()
        self.contabilita_controller = contabilita_controller
        self.config = config
        
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """Configura l'interfaccia utente."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("💼 Contabilità Generale")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Pulsanti
        nuovo_button = QPushButton("➕ Nuovo Movimento")
        nuovo_button.clicked.connect(self.new_movement)
        header_layout.addWidget(nuovo_button)
        
        piano_button = QPushButton("🗂️ Piano dei Conti")
        piano_button.clicked.connect(self.show_chart_of_accounts)
        header_layout.addWidget(piano_button)
        
        layout.addLayout(header_layout)
        
        # Tab widget
        tab_widget = QTabWidget()
        
        # Tab Piano dei Conti
        conti_tree = QTreeWidget()
        conti_tree.setHeaderLabels(['Codice', 'Descrizione', 'Tipo', 'Saldo'])
        tab_widget.addTab(conti_tree, "Piano dei Conti")
        
        # Tab Movimenti
        movimenti_table = QTableWidget()
        movimenti_table.setColumnCount(6)
        movimenti_table.setHorizontalHeaderLabels([
            'Numero', 'Data', 'Causale', 'Conto Dare', 'Conto Avere', 'Importo'
        ])
        tab_widget.addTab(movimenti_table, "Movimenti Contabili")
        
        # Tab Bilancio
        bilancio_table = QTableWidget()
        bilancio_table.setColumnCount(3)
        bilancio_table.setHorizontalHeaderLabels(['Conto', 'Descrizione', 'Saldo'])
        tab_widget.addTab(bilancio_table, "Bilancio")
        
        layout.addWidget(tab_widget)
        
        # Placeholder label
        placeholder_label = QLabel("🧮 Implementazione completa della contabilità in sviluppo")
        placeholder_label.setStyleSheet("color: #757575; font-style: italic; padding: 20px;")
        layout.addWidget(placeholder_label)
    
    def new_movement(self):
        """Crea un nuovo movimento contabile."""
        QMessageBox.information(self, "Info", "Funzionalità in sviluppo")
    
    def show_chart_of_accounts(self):
        """Mostra il piano dei conti."""
        QMessageBox.information(self, "Info", "Piano dei conti in sviluppo")
    
    def refresh_data(self):
        """Aggiorna i dati."""
        pass