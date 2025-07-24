"""
Applicazione di Contabilità
==========================

Un'applicazione desktop completa per la gestione della contabilità aziendale.

Moduli principali:
- models: Modelli del database (SQLAlchemy)
- views: Interfaccia grafica (PySide6)
- controllers: Logica di business
- database: Gestione database
- utils: Utilità e helper
"""

__version__ = "1.0.0"
__author__ = "Assistente AI"
__email__ = "assistente@contabilita.com"

# Importazioni principali
from .config import Config
from .database.connection import DatabaseManager

# Configurazione base
config = Config()
db_manager = DatabaseManager()