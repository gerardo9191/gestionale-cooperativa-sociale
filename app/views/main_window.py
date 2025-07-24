"""
Finestra Principale
===================

Finestra principale dell'applicazione con menu, toolbar e area centrale.
"""

import sys
from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QWidget, 
    QTabWidget, QMenuBar, QToolBar, QStatusBar, QLabel, QPushButton,
    QAction, QSplitter, QFrame, QMessageBox, QDialog, QGridLayout,
    QLineEdit, QComboBox, QSpinBox, QCheckBox
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread, pyqtSignal
from PySide6.QtGui import QIcon, QPixmap, QFont, QPalette, QColor

from ..config import Config
from ..database.connection import DatabaseManager
from ..controllers import (
    AnagraficheController, DocumentiController, 
    ContabilitaController, ReportController
)

# Import dei widget principali
from .dashboard_widget import DashboardWidget
from .anagrafiche_widget import AnagraficheWidget
from .documenti_widget import DocumentiWidget
from .contabilita_widget import ContabilitaWidget
from .report_widget import ReportWidget


class ThemeManager:
    """Gestore dei temi dell'applicazione."""
    
    LIGHT_THEME = {
        'background': '#f5f5f5',
        'surface': '#ffffff',
        'primary': '#2196f3',
        'secondary': '#03dac6',
        'text': '#212121',
        'text_secondary': '#757575'
    }
    
    DARK_THEME = {
        'background': '#121212',
        'surface': '#1e1e1e',
        'primary': '#bb86fc',
        'secondary': '#03dac6',
        'text': '#ffffff',
        'text_secondary': '#b3b3b3'
    }
    
    @staticmethod
    def apply_theme(app: QApplication, theme: str = 'light'):
        """Applica un tema all'applicazione."""
        colors = ThemeManager.LIGHT_THEME if theme == 'light' else ThemeManager.DARK_THEME
        
        stylesheet = f"""
        QMainWindow {{
            background-color: {colors['background']};
            color: {colors['text']};
        }}
        
        QWidget {{
            background-color: {colors['surface']};
            color: {colors['text']};
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 9pt;
        }}
        
        QPushButton {{
            background-color: {colors['primary']};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {colors['secondary']};
        }}
        
        QPushButton:pressed {{
            background-color: {colors['primary']};
        }}
        
        QTabWidget::pane {{
            border: 1px solid {colors['text_secondary']};
            background-color: {colors['surface']};
        }}
        
        QTabBar::tab {{
            background-color: {colors['background']};
            color: {colors['text']};
            padding: 8px 16px;
            border: 1px solid {colors['text_secondary']};
            border-bottom: none;
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors['primary']};
            color: white;
        }}
        
        QMenuBar {{
            background-color: {colors['surface']};
            color: {colors['text']};
            border-bottom: 1px solid {colors['text_secondary']};
        }}
        
        QMenuBar::item:selected {{
            background-color: {colors['primary']};
            color: white;
        }}
        
        QToolBar {{
            background-color: {colors['surface']};
            border: none;
            spacing: 4px;
        }}
        
        QStatusBar {{
            background-color: {colors['surface']};
            color: {colors['text_secondary']};
            border-top: 1px solid {colors['text_secondary']};
        }}
        
        QLineEdit, QComboBox, QSpinBox {{
            padding: 6px;
            border: 1px solid {colors['text_secondary']};
            border-radius: 4px;
            background-color: {colors['surface']};
            color: {colors['text']};
        }}
        
        QTableWidget {{
            gridline-color: {colors['text_secondary']};
            background-color: {colors['surface']};
            alternate-background-color: {colors['background']};
        }}
        
        QHeaderView::section {{
            background-color: {colors['primary']};
            color: white;
            padding: 6px;
            border: none;
            font-weight: bold;
        }}
        """
        
        app.setStyleSheet(stylesheet)


class SettingsDialog(QDialog):
    """Dialog per le impostazioni dell'applicazione."""
    
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Impostazioni")
        self.setModal(True)
        self.setFixedSize(400, 300)
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Configura l'interfaccia utente."""
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QGridLayout()
        
        # Tema
        form_layout.addWidget(QLabel("Tema:"), 0, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark"])
        form_layout.addWidget(self.theme_combo, 0, 1)
        
        # Lingua
        form_layout.addWidget(QLabel("Lingua:"), 1, 0)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["it", "en"])
        form_layout.addWidget(self.language_combo, 1, 1)
        
        # Dimensioni finestra
        form_layout.addWidget(QLabel("Larghezza finestra:"), 2, 0)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(800, 2000)
        form_layout.addWidget(self.width_spin, 2, 1)
        
        form_layout.addWidget(QLabel("Altezza finestra:"), 3, 0)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(600, 1500)
        form_layout.addWidget(self.height_spin, 3, 1)
        
        # Simbolo valuta
        form_layout.addWidget(QLabel("Simbolo valuta:"), 4, 0)
        self.currency_edit = QLineEdit()
        form_layout.addWidget(self.currency_edit, 4, 1)
        
        # Decimali
        form_layout.addWidget(QLabel("Cifre decimali:"), 5, 0)
        self.decimals_spin = QSpinBox()
        self.decimals_spin.setRange(0, 4)
        form_layout.addWidget(self.decimals_spin, 5, 1)
        
        layout.addLayout(form_layout)
        
        # Pulsanti
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Salva")
        save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Annulla")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def load_settings(self):
        """Carica le impostazioni correnti."""
        self.theme_combo.setCurrentText(self.config.THEME)
        self.language_combo.setCurrentText(self.config.LANGUAGE)
        self.width_spin.setValue(self.config.WINDOW_WIDTH)
        self.height_spin.setValue(self.config.WINDOW_HEIGHT)
        self.currency_edit.setText(self.config.CURRENCY_SYMBOL)
        self.decimals_spin.setValue(self.config.DECIMAL_PLACES)
    
    def save_settings(self):
        """Salva le impostazioni."""
        self.config.update_theme(self.theme_combo.currentText())
        self.config.update_language(self.language_combo.currentText())
        self.config.WINDOW_WIDTH = self.width_spin.value()
        self.config.WINDOW_HEIGHT = self.height_spin.value()
        self.config.CURRENCY_SYMBOL = self.currency_edit.text()
        self.config.DECIMAL_PLACES = self.decimals_spin.value()
        
        self.accept()


class MainWindow(QMainWindow):
    """Finestra principale dell'applicazione."""
    
    def __init__(self, config: Config, db_manager: DatabaseManager):
        super().__init__()
        
        self.config = config
        self.db_manager = db_manager
        
        # Inizializza i controller
        self.anagrafiche_controller = AnagraficheController(db_manager)
        self.documenti_controller = DocumentiController(db_manager)
        self.contabilita_controller = ContabilitaController(db_manager)
        self.report_controller = ReportController(db_manager)
        
        # Configura l'interfaccia
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        
        # Applica il tema
        ThemeManager.apply_theme(QApplication.instance(), self.config.THEME)
        
        # Timer per aggiornamenti automatici
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_dashboard)
        self.update_timer.start(60000)  # Aggiorna ogni minuto
    
    def setup_ui(self):
        """Configura l'interfaccia utente principale."""
        self.setWindowTitle(f"{self.config.APP_NAME} v{self.config.VERSION}")
        self.setGeometry(100, 100, self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT)
        
        # Widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principale
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget per le diverse sezioni
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Crea i widget per ogni sezione
        self.setup_tabs()
    
    def setup_tabs(self):
        """Configura le schede dell'applicazione."""
        # Dashboard
        self.dashboard_widget = DashboardWidget(self.report_controller, self.config)
        self.tab_widget.addTab(self.dashboard_widget, "📊 Dashboard")
        
        # Anagrafiche
        self.anagrafiche_widget = AnagraficheWidget(self.anagrafiche_controller, self.config)
        self.tab_widget.addTab(self.anagrafiche_widget, "👥 Anagrafiche")
        
        # Documenti
        self.documenti_widget = DocumentiWidget(self.documenti_controller, self.anagrafiche_controller, self.config)
        self.tab_widget.addTab(self.documenti_widget, "📄 Documenti")
        
        # Contabilità
        self.contabilita_widget = ContabilitaWidget(self.contabilita_controller, self.config)
        self.tab_widget.addTab(self.contabilita_widget, "💼 Contabilità")
        
        # Report
        self.report_widget = ReportWidget(self.report_controller, self.config)
        self.tab_widget.addTab(self.report_widget, "📈 Report")
    
    def setup_menu(self):
        """Configura il menu dell'applicazione."""
        menubar = self.menuBar()
        
        # Menu File
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("Nuovo", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_document)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("Esporta...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)
        
        import_action = QAction("Importa...", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self.import_data)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Esci", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Modifica
        edit_menu = menubar.addMenu("Modifica")
        
        settings_action = QAction("Impostazioni...", self)
        settings_action.triggered.connect(self.show_settings)
        edit_menu.addAction(settings_action)
        
        # Menu Visualizza
        view_menu = menubar.addMenu("Visualizza")
        
        refresh_action = QAction("Aggiorna", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_all)
        view_menu.addAction(refresh_action)
        
        theme_menu = view_menu.addMenu("Tema")
        
        light_action = QAction("Chiaro", self)
        light_action.triggered.connect(lambda: self.change_theme('light'))
        theme_menu.addAction(light_action)
        
        dark_action = QAction("Scuro", self)
        dark_action.triggered.connect(lambda: self.change_theme('dark'))
        theme_menu.addAction(dark_action)
        
        # Menu Aiuto
        help_menu = menubar.addMenu("Aiuto")
        
        about_action = QAction("Informazioni...", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Configura la toolbar dell'applicazione."""
        toolbar = self.addToolBar("Principale")
        toolbar.setMovable(False)
        
        # Pulsanti principali
        new_button = QPushButton("Nuovo")
        new_button.clicked.connect(self.new_document)
        toolbar.addWidget(new_button)
        
        refresh_button = QPushButton("Aggiorna")
        refresh_button.clicked.connect(self.refresh_all)
        toolbar.addWidget(refresh_button)
        
        toolbar.addSeparator()
        
        export_button = QPushButton("Esporta")
        export_button.clicked.connect(self.export_data)
        toolbar.addWidget(export_button)
        
        settings_button = QPushButton("Impostazioni")
        settings_button.clicked.connect(self.show_settings)
        toolbar.addWidget(settings_button)
    
    def setup_statusbar(self):
        """Configura la barra di stato."""
        self.statusbar = self.statusBar()
        
        # Label per informazioni
        self.status_label = QLabel("Pronto")
        self.statusbar.addWidget(self.status_label)
        
        # Label per connessione database
        self.db_status_label = QLabel()
        self.update_db_status()
        self.statusbar.addPermanentWidget(self.db_status_label)
        
        # Label per data/ora
        self.datetime_label = QLabel()
        self.update_datetime()
        self.statusbar.addPermanentWidget(self.datetime_label)
        
        # Timer per aggiornare data/ora
        datetime_timer = QTimer()
        datetime_timer.timeout.connect(self.update_datetime)
        datetime_timer.start(1000)
    
    def update_db_status(self):
        """Aggiorna lo stato della connessione al database."""
        if self.db_manager.test_connection():
            self.db_status_label.setText("🟢 DB Connesso")
        else:
            self.db_status_label.setText("🔴 DB Disconnesso")
    
    def update_datetime(self):
        """Aggiorna la data/ora nella statusbar."""
        from datetime import datetime
        now = datetime.now()
        self.datetime_label.setText(now.strftime("%d/%m/%Y %H:%M:%S"))
    
    def update_dashboard(self):
        """Aggiorna i dati della dashboard."""
        if hasattr(self, 'dashboard_widget'):
            self.dashboard_widget.refresh_data()
    
    def change_theme(self, theme: str):
        """Cambia il tema dell'applicazione."""
        self.config.update_theme(theme)
        ThemeManager.apply_theme(QApplication.instance(), theme)
        self.status_label.setText(f"Tema cambiato in: {theme}")
    
    def show_settings(self):
        """Mostra il dialog delle impostazioni."""
        dialog = SettingsDialog(self.config, self)
        if dialog.exec() == QDialog.Accepted:
            # Applica le nuove impostazioni
            ThemeManager.apply_theme(QApplication.instance(), self.config.THEME)
            self.resize(self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT)
            self.status_label.setText("Impostazioni salvate")
    
    def show_about(self):
        """Mostra il dialog delle informazioni."""
        QMessageBox.about(
            self, 
            "Informazioni",
            f"""
            <h3>{self.config.APP_NAME}</h3>
            <p>Versione: {self.config.VERSION}</p>
            <p>Autore: {self.config.AUTHOR}</p>
            <p>Un'applicazione completa per la gestione della contabilità aziendale.</p>
            <p>Caratteristiche principali:</p>
            <ul>
            <li>Gestione anagrafiche (clienti, fornitori, dipendenti)</li>
            <li>Emissione fatture e documenti contabili</li>
            <li>Contabilità generale e prima nota</li>
            <li>Report finanziari e dashboard interattiva</li>
            <li>Interfaccia moderna con supporto temi</li>
            </ul>
            """
        )
    
    def new_document(self):
        """Crea un nuovo documento."""
        current_tab = self.tab_widget.currentIndex()
        if current_tab == 1:  # Anagrafiche
            self.anagrafiche_widget.new_record()
        elif current_tab == 2:  # Documenti
            self.documenti_widget.new_document()
        elif current_tab == 3:  # Contabilità
            self.contabilita_widget.new_movement()
        
        self.status_label.setText("Nuovo documento creato")
    
    def export_data(self):
        """Esporta i dati."""
        current_tab = self.tab_widget.currentIndex()
        if current_tab == 4:  # Report
            self.report_widget.export_current_report()
        
        self.status_label.setText("Dati esportati")
    
    def import_data(self):
        """Importa i dati."""
        self.status_label.setText("Funzione di importazione non ancora implementata")
    
    def refresh_all(self):
        """Aggiorna tutti i widget."""
        # Aggiorna ogni widget
        if hasattr(self, 'dashboard_widget'):
            self.dashboard_widget.refresh_data()
        if hasattr(self, 'anagrafiche_widget'):
            self.anagrafiche_widget.refresh_data()
        if hasattr(self, 'documenti_widget'):
            self.documenti_widget.refresh_data()
        if hasattr(self, 'contabilita_widget'):
            self.contabilita_widget.refresh_data()
        if hasattr(self, 'report_widget'):
            self.report_widget.refresh_data()
        
        # Aggiorna stato database
        self.update_db_status()
        
        self.status_label.setText("Tutti i dati aggiornati")
    
    def closeEvent(self, event):
        """Gestisce la chiusura dell'applicazione."""
        reply = QMessageBox.question(
            self, 
            'Conferma uscita',
            'Sei sicuro di voler chiudere l\'applicazione?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Chiudi la connessione al database
            self.db_manager.close()
            event.accept()
        else:
            event.ignore()