"""
Configurazione dell'applicazione
===============================

Gestisce tutte le impostazioni e configurazioni dell'applicazione.
"""

import os
from pathlib import Path
from typing import Dict, Any


class Config:
    """Classe per la gestione delle configurazioni dell'applicazione."""
    
    def __init__(self):
        """Inizializza la configurazione con i valori predefiniti."""
        self.APP_NAME = "Contabilità Manager"
        self.VERSION = "1.0.0"
        self.AUTHOR = "Assistente AI"
        
        # Percorsi
        self.BASE_DIR = Path(__file__).parent.parent
        self.DATA_DIR = self.BASE_DIR / "data"
        self.RESOURCES_DIR = self.BASE_DIR / "resources"
        self.TRANSLATIONS_DIR = self.RESOURCES_DIR / "translations"
        self.THEMES_DIR = self.RESOURCES_DIR / "themes"
        
        # Database
        self.DATABASE_URL = f"sqlite:///{self.DATA_DIR}/contabilita.db"
        
        # Interfaccia
        self.WINDOW_WIDTH = 1200
        self.WINDOW_HEIGHT = 800
        self.THEME = "light"  # light, dark
        self.LANGUAGE = "it"  # it, en
        
        # Formato numerico
        self.CURRENCY_SYMBOL = "€"
        self.DECIMAL_PLACES = 2
        
        # Creo le directory se non esistono
        self._create_directories()
    
    def _create_directories(self) -> None:
        """Crea le directory necessarie se non esistono."""
        directories = [
            self.DATA_DIR,
            self.RESOURCES_DIR,
            self.TRANSLATIONS_DIR,
            self.THEMES_DIR
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_database_url(self) -> str:
        """Restituisce l'URL del database."""
        return self.DATABASE_URL
    
    def get_theme_settings(self) -> Dict[str, Any]:
        """Restituisce le impostazioni del tema corrente."""
        return {
            "theme": self.THEME,
            "window_width": self.WINDOW_WIDTH,
            "window_height": self.WINDOW_HEIGHT
        }
    
    def get_locale_settings(self) -> Dict[str, Any]:
        """Restituisce le impostazioni locali."""
        return {
            "language": self.LANGUAGE,
            "currency_symbol": self.CURRENCY_SYMBOL,
            "decimal_places": self.DECIMAL_PLACES
        }
    
    def update_theme(self, theme: str) -> None:
        """Aggiorna il tema dell'applicazione."""
        if theme in ["light", "dark"]:
            self.THEME = theme
    
    def update_language(self, language: str) -> None:
        """Aggiorna la lingua dell'applicazione."""
        if language in ["it", "en"]:
            self.LANGUAGE = language