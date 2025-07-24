"""
Database Connection Manager
===========================

Gestisce la connessione al database e le operazioni di base.
"""

import logging
from typing import Optional, Generator
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .base import Base


class DatabaseManager:
    """Gestore delle connessioni al database."""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Inizializza il gestore del database.
        
        Args:
            database_url: URL di connessione al database
        """
        self.database_url = database_url
        self.engine: Optional[Engine] = None
        self.session_factory: Optional[sessionmaker] = None
        self.logger = logging.getLogger(__name__)
    
    def initialize(self, database_url: str) -> None:
        """
        Inizializza il database con l'URL specificato.
        
        Args:
            database_url: URL di connessione al database
        """
        try:
            self.database_url = database_url
            self.engine = create_engine(
                database_url,
                echo=False,  # Imposta True per debug SQL
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            # Crea il factory delle sessioni
            self.session_factory = sessionmaker(
                bind=self.engine,
                autoflush=False,
                autocommit=False
            )
            
            # Crea tutte le tabelle
            self.create_tables()
            
            self.logger.info(f"Database inizializzato: {database_url}")
            
        except SQLAlchemyError as e:
            self.logger.error(f"Errore nell'inizializzazione del database: {e}")
            raise
    
    def create_tables(self) -> None:
        """Crea tutte le tabelle nel database."""
        if self.engine is None:
            raise RuntimeError("Database non inizializzato")
        
        try:
            Base.metadata.create_all(self.engine)
            self.logger.info("Tabelle create con successo")
            
        except SQLAlchemyError as e:
            self.logger.error(f"Errore nella creazione delle tabelle: {e}")
            raise
    
    def get_session(self) -> Session:
        """
        Restituisce una nuova sessione del database.
        
        Returns:
            Session: Sessione SQLAlchemy
        """
        if self.session_factory is None:
            raise RuntimeError("Database non inizializzato")
        
        return self.session_factory()
    
    def get_session_context(self) -> Generator[Session, None, None]:
        """
        Context manager per le sessioni del database.
        
        Yields:
            Session: Sessione SQLAlchemy
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Errore nella sessione del database: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """
        Testa la connessione al database.
        
        Returns:
            bool: True se la connessione è OK, False altrimenti
        """
        try:
            if self.engine is None:
                return False
            
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
                return True
                
        except SQLAlchemyError as e:
            self.logger.error(f"Errore nel test della connessione: {e}")
            return False
    
    def close(self) -> None:
        """Chiude la connessione al database."""
        if self.engine:
            self.engine.dispose()
            self.logger.info("Connessione al database chiusa")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()