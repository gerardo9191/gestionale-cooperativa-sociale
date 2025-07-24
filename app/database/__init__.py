"""
Database Package
================

Gestisce la connessione al database e le operazioni CRUD.
"""

from .connection import DatabaseManager
from .base import Base

__all__ = ["DatabaseManager", "Base"]