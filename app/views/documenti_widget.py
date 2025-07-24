"""
Documenti Widget
================

Widget per la gestione dei documenti contabili (fatture, note credito, prima nota).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTabWidget, QTableWidget, QTableWidgetItem, QLineEdit,
    QMessageBox
)
from PySide6.QtGui import QFont

from ..config import Config
from ..controllers.documenti_controller import DocumentiController
from ..controllers.anagrafiche_controller import AnagraficheController


class DocumentiWidget(QWidget):
    """Widget per la gestione dei documenti contabili."""
    
    def __init__(self, documenti_controller: DocumentiController, 
                 anagrafiche_controller: AnagraficheController, config: Config):
        super().__init__()
        self.documenti_controller = documenti_controller
        self.anagrafiche_controller = anagrafiche_controller
        self.config = config
        
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """Configura l'interfaccia utente."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("📄 Gestione Documenti")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Pulsanti
        nuovo_button = QPushButton("➕ Nuovo Documento")
        nuovo_button.clicked.connect(self.new_document)
        header_layout.addWidget(nuovo_button)
        
        layout.addLayout(header_layout)
        
        # Tab widget
        tab_widget = QTabWidget()
        
        # Tab Fatture
        fatture_table = QTableWidget()
        fatture_table.setColumnCount(6)
        fatture_table.setHorizontalHeaderLabels([
            'Numero', 'Data', 'Cliente/Fornitore', 'Tipo', 'Totale', 'Stato'
        ])
        tab_widget.addTab(fatture_table, "Fatture")
        
        # Tab Note Credito
        note_table = QTableWidget()
        note_table.setColumnCount(5)
        note_table.setHorizontalHeaderLabels([
            'Numero', 'Data', 'Cliente/Fornitore', 'Motivo', 'Totale'
        ])
        tab_widget.addTab(note_table, "Note Credito")
        
        # Tab Prima Nota
        prima_nota_table = QTableWidget()
        prima_nota_table.setColumnCount(5)
        prima_nota_table.setHorizontalHeaderLabels([
            'Numero', 'Data', 'Causale', 'Dare', 'Avere'
        ])
        tab_widget.addTab(prima_nota_table, "Prima Nota")
        
        layout.addWidget(tab_widget)
        
        # Placeholder label
        placeholder_label = QLabel("📝 Implementazione completa dei documenti in sviluppo")
        placeholder_label.setStyleSheet("color: #757575; font-style: italic; padding: 20px;")
        layout.addWidget(placeholder_label)
    
    def new_document(self):
        """Crea un nuovo documento."""
        QMessageBox.information(self, "Info", "Funzionalità in sviluppo")
    
    def refresh_data(self):
        """Aggiorna i dati."""
        pass