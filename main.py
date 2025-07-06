#!/usr/bin/env python3
"""
Contabilità Manager - Applicazione Desktop
==========================================

Applicazione completa per la gestione della contabilità aziendale.

Caratteristiche principali:
- Gestione anagrafiche (fornitori, clienti, dipendenti)
- Emissione fatture e documenti contabili
- Contabilità generale e prima nota
- Report finanziari e dashboard interattiva
- Interfaccia moderna con supporto temi light/dark

Per avviare l'applicazione:
    python main.py

Requisiti:
- Python 3.10+
- PySide6
- SQLAlchemy
- Matplotlib
- Pandas
- Altre dipendenze in requirements.txt
"""

import sys
import os
import logging
from pathlib import Path

# Aggiungi la directory dell'app al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QFont

from app.config import Config
from app.database.connection import DatabaseManager
from app.views.main_window import MainWindow, ThemeManager


def setup_logging():
    """Configura il sistema di logging."""
    # Crea directory per i log
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configura il logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "contabilita.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Logger principale
    logger = logging.getLogger("ContabilitaManager")
    logger.info("Sistema di logging inizializzato")
    return logger


def check_dependencies():
    """Verifica che tutte le dipendenze siano installate."""
    required_modules = [
        'PySide6', 'sqlalchemy', 'matplotlib', 'pandas', 'babel'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module.lower())
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        error_msg = f"""
        Moduli mancanti: {', '.join(missing_modules)}
        
        Per installarli, esegui:
        pip install {' '.join(missing_modules)}
        
        Oppure:
        pip install -r requirements.txt
        """
        
        app = QApplication(sys.argv)
        QMessageBox.critical(None, "Dipendenze Mancanti", error_msg)
        sys.exit(1)


def create_splash_screen(app: QApplication) -> QSplashScreen:
    """Crea e mostra la splash screen."""
    # Crea un pixmap semplice per la splash screen
    pixmap = QPixmap(400, 300)
    pixmap.fill(Qt.white)
    
    splash = QSplashScreen(pixmap)
    splash.setStyleSheet("""
        QSplashScreen {
            background-color: #2196f3;
            color: white;
            font-size: 16px;
            font-weight: bold;
        }
    """)
    
    # Mostra messaggio di caricamento
    splash.showMessage(
        "Contabilità Manager v1.0.0\n\nCaricamento in corso...",
        Qt.AlignCenter | Qt.AlignBottom,
        Qt.white
    )
    
    splash.show()
    app.processEvents()
    
    return splash


def initialize_database(config: Config, logger: logging.Logger) -> DatabaseManager:
    """Inizializza il database."""
    logger.info("Inizializzazione database...")
    
    try:
        # Crea il gestore del database
        db_manager = DatabaseManager()
        db_manager.initialize(config.get_database_url())
        
        # Testa la connessione
        if db_manager.test_connection():
            logger.info("Database connesso con successo")
            return db_manager
        else:
            raise Exception("Impossibile connettersi al database")
            
    except Exception as e:
        logger.error(f"Errore nell'inizializzazione del database: {e}")
        
        # Mostra errore all'utente
        app = QApplication.instance()
        if app:
            QMessageBox.critical(
                None, 
                "Errore Database",
                f"Impossibile inizializzare il database:\n{e}\n\n"
                "Verifica che il percorso del database sia accessibile."
            )
        
        sys.exit(1)


def main():
    """Funzione principale dell'applicazione."""
    # Verifica dipendenze
    check_dependencies()
    
    # Configura logging
    logger = setup_logging()
    logger.info("=== Avvio Contabilità Manager ===")
    
    try:
        # Crea applicazione Qt
        app = QApplication(sys.argv)
        app.setApplicationName("Contabilità Manager")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("Assistente AI")
        
        # Configura font dell'applicazione
        font = QFont("Segoe UI", 9)
        app.setFont(font)
        
        # Mostra splash screen
        splash = create_splash_screen(app)
        
        # Simula caricamento
        QTimer.singleShot(1000, lambda: splash.showMessage(
            "Contabilità Manager v1.0.0\n\nConfigurazione...",
            Qt.AlignCenter | Qt.AlignBottom, Qt.white
        ))
        app.processEvents()
        
        # Carica configurazione
        logger.info("Caricamento configurazione...")
        config = Config()
        
        # Inizializza database
        QTimer.singleShot(2000, lambda: splash.showMessage(
            "Contabilità Manager v1.0.0\n\nInnizializzazione database...",
            Qt.AlignCenter | Qt.AlignBottom, Qt.white
        ))
        app.processEvents()
        
        db_manager = initialize_database(config, logger)
        
        # Applica tema
        QTimer.singleShot(3000, lambda: splash.showMessage(
            "Contabilità Manager v1.0.0\n\nCaricamento interfaccia...",
            Qt.AlignCenter | Qt.AlignBottom, Qt.white
        ))
        app.processEvents()
        
        ThemeManager.apply_theme(app, config.THEME)
        
        # Crea finestra principale
        logger.info("Creazione finestra principale...")
        main_window = MainWindow(config, db_manager)
        
        # Nascondi splash e mostra finestra principale
        QTimer.singleShot(4000, lambda: (
            splash.finish(main_window),
            main_window.show()
        ))
        
        logger.info("Applicazione avviata con successo")
        
        # Avvia event loop
        exit_code = app.exec()
        
        # Cleanup
        logger.info("Chiusura applicazione...")
        db_manager.close()
        logger.info("=== Fine Contabilità Manager ===")
        
        return exit_code
        
    except Exception as e:
        logger.error(f"Errore critico nell'avvio dell'applicazione: {e}", exc_info=True)
        
        # Mostra errore all'utente
        if 'app' in locals():
            QMessageBox.critical(
                None,
                "Errore Critico",
                f"Si è verificato un errore critico:\n{e}\n\n"
                "L'applicazione verrà chiusa."
            )
        
        return 1


if __name__ == "__main__":
    # Verifica versione Python
    if sys.version_info < (3, 10):
        print("ERRORE: Python 3.10 o superiore è richiesto")
        print(f"Versione corrente: {sys.version}")
        sys.exit(1)
    
    # Avvia applicazione
    exit_code = main()
    sys.exit(exit_code)