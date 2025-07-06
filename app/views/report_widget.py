"""
Report Widget
=============

Widget per la generazione e visualizzazione dei report finanziari.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTabWidget, QTableWidget, QTableWidgetItem, QComboBox,
    QDateEdit, QGroupBox, QMessageBox, QTextEdit
)
from PySide6.QtGui import QFont
from PySide6.QtCore import QDate

from ..config import Config
from ..controllers.report_controller import ReportController


class ReportWidget(QWidget):
    """Widget per la gestione dei report finanziari."""
    
    def __init__(self, report_controller: ReportController, config: Config):
        super().__init__()
        self.report_controller = report_controller
        self.config = config
        
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """Configura l'interfaccia utente."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("📈 Report Finanziari")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Pulsanti
        genera_button = QPushButton("📊 Genera Report")
        genera_button.clicked.connect(self.generate_report)
        header_layout.addWidget(genera_button)
        
        esporta_button = QPushButton("💾 Esporta")
        esporta_button.clicked.connect(self.export_current_report)
        header_layout.addWidget(esporta_button)
        
        layout.addLayout(header_layout)
        
        # Controlli filtri
        filters_group = QGroupBox("Filtri Report")
        filters_layout = QHBoxLayout(filters_group)
        
        filters_layout.addWidget(QLabel("Tipo Report:"))
        
        self.tipo_report_combo = QComboBox()
        self.tipo_report_combo.addItems([
            "Bilancio", "Conto Economico", "Report Fatture", 
            "Estratto Conto Cliente", "Estratto Conto Fornitore"
        ])
        filters_layout.addWidget(self.tipo_report_combo)
        
        filters_layout.addWidget(QLabel("Dal:"))
        self.data_inizio = QDateEdit()
        self.data_inizio.setDate(QDate.currentDate().addMonths(-1))
        self.data_inizio.setCalendarPopup(True)
        filters_layout.addWidget(self.data_inizio)
        
        filters_layout.addWidget(QLabel("Al:"))
        self.data_fine = QDateEdit()
        self.data_fine.setDate(QDate.currentDate())
        self.data_fine.setCalendarPopup(True)
        filters_layout.addWidget(self.data_fine)
        
        filters_layout.addStretch()
        
        layout.addWidget(filters_group)
        
        # Tab widget per i report
        tab_widget = QTabWidget()
        
        # Tab Bilancio
        bilancio_table = QTableWidget()
        bilancio_table.setColumnCount(3)
        bilancio_table.setHorizontalHeaderLabels(['Conto', 'Descrizione', 'Saldo'])
        tab_widget.addTab(bilancio_table, "Bilancio")
        
        # Tab Conto Economico
        conto_economico_table = QTableWidget()
        conto_economico_table.setColumnCount(3)
        conto_economico_table.setHorizontalHeaderLabels(['Voce', 'Descrizione', 'Importo'])
        tab_widget.addTab(conto_economico_table, "Conto Economico")
        
        # Tab Report Personalizzati
        report_text = QTextEdit()
        report_text.setReadOnly(True)
        report_text.setPlainText("Seleziona un tipo di report e premi 'Genera Report' per visualizzare i dati.")
        tab_widget.addTab(report_text, "Report Dettagliato")
        
        layout.addWidget(tab_widget)
        
        # Placeholder label
        placeholder_label = QLabel("📋 Implementazione completa dei report in sviluppo")
        placeholder_label.setStyleSheet("color: #757575; font-style: italic; padding: 20px;")
        layout.addWidget(placeholder_label)
    
    def generate_report(self):
        """Genera il report selezionato."""
        tipo_report = self.tipo_report_combo.currentText()
        QMessageBox.information(self, "Info", f"Generazione {tipo_report} in sviluppo")
    
    def export_current_report(self):
        """Esporta il report corrente."""
        QMessageBox.information(self, "Info", "Funzionalità di export in sviluppo")
    
    def refresh_data(self):
        """Aggiorna i dati."""
        pass