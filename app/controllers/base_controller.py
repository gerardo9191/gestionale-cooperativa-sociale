"""
Base Controller
===============

Classe base per tutti i controller dell'applicazione.
"""

import logging
from typing import Any, List, Optional, Dict, Type, TypeVar, Generic
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_

from ..database.connection import DatabaseManager
from ..database.base import Base

T = TypeVar('T', bound=Base)


class BaseController(Generic[T]):
    """Controller base per le operazioni CRUD."""
    
    def __init__(self, db_manager: DatabaseManager, model_class: Type[T]):
        """
        Inizializza il controller base.
        
        Args:
            db_manager: Gestore del database
            model_class: Classe del modello SQLAlchemy
        """
        self.db_manager = db_manager
        self.model_class = model_class
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def create(self, **kwargs) -> Optional[T]:
        """
        Crea un nuovo record.
        
        Args:
            **kwargs: Dati del record
            
        Returns:
            Il record creato o None se errore
        """
        try:
            with self.db_manager.get_session_context() as session:
                record = self.model_class(**kwargs)
                session.add(record)
                session.commit()
                session.refresh(record)
                self.logger.info(f"Record creato: {record}")
                return record
                
        except SQLAlchemyError as e:
            self.logger.error(f"Errore nella creazione del record: {e}")
            return None
    
    def get_by_id(self, record_id: int) -> Optional[T]:
        """
        Recupera un record per ID.
        
        Args:
            record_id: ID del record
            
        Returns:
            Il record trovato o None
        """
        try:
            with self.db_manager.get_session_context() as session:
                return session.query(self.model_class).filter(
                    self.model_class.id == record_id
                ).first()
                
        except SQLAlchemyError as e:
            self.logger.error(f"Errore nel recupero del record {record_id}: {e}")
            return None
    
    def get_all(self, active_only: bool = True) -> List[T]:
        """
        Recupera tutti i record.
        
        Args:
            active_only: Se True, recupera solo i record attivi
            
        Returns:
            Lista dei record
        """
        try:
            with self.db_manager.get_session_context() as session:
                query = session.query(self.model_class)
                
                # Filtra per record attivi se il modello ha il campo 'attivo'
                if active_only and hasattr(self.model_class, 'attivo'):
                    query = query.filter(self.model_class.attivo == True)
                
                return query.all()
                
        except SQLAlchemyError as e:
            self.logger.error(f"Errore nel recupero di tutti i record: {e}")
            return []
    
    def update(self, record_id: int, **kwargs) -> Optional[T]:
        """
        Aggiorna un record.
        
        Args:
            record_id: ID del record
            **kwargs: Dati da aggiornare
            
        Returns:
            Il record aggiornato o None se errore
        """
        try:
            with self.db_manager.get_session_context() as session:
                record = session.query(self.model_class).filter(
                    self.model_class.id == record_id
                ).first()
                
                if not record:
                    self.logger.warning(f"Record {record_id} non trovato per l'aggiornamento")
                    return None
                
                # Aggiorna i campi
                for key, value in kwargs.items():
                    if hasattr(record, key):
                        setattr(record, key, value)
                
                session.commit()
                session.refresh(record)
                self.logger.info(f"Record aggiornato: {record}")
                return record
                
        except SQLAlchemyError as e:
            self.logger.error(f"Errore nell'aggiornamento del record {record_id}: {e}")
            return None
    
    def delete(self, record_id: int, soft_delete: bool = True) -> bool:
        """
        Elimina un record.
        
        Args:
            record_id: ID del record
            soft_delete: Se True, imposta attivo=False invece di eliminare
            
        Returns:
            True se eliminato con successo, False altrimenti
        """
        try:
            with self.db_manager.get_session_context() as session:
                record = session.query(self.model_class).filter(
                    self.model_class.id == record_id
                ).first()
                
                if not record:
                    self.logger.warning(f"Record {record_id} non trovato per l'eliminazione")
                    return False
                
                if soft_delete and hasattr(record, 'attivo'):
                    # Soft delete
                    record.attivo = False
                    session.commit()
                    self.logger.info(f"Record disattivato: {record}")
                else:
                    # Hard delete
                    session.delete(record)
                    session.commit()
                    self.logger.info(f"Record eliminato: {record_id}")
                
                return True
                
        except SQLAlchemyError as e:
            self.logger.error(f"Errore nell'eliminazione del record {record_id}: {e}")
            return False
    
    def search(self, search_term: str, fields: List[str] = None) -> List[T]:
        """
        Cerca record per termine.
        
        Args:
            search_term: Termine da cercare
            fields: Campi in cui cercare (default: tutti i campi stringa)
            
        Returns:
            Lista dei record trovati
        """
        try:
            with self.db_manager.get_session_context() as session:
                query = session.query(self.model_class)
                
                if not fields:
                    # Cerca in tutti i campi stringa
                    fields = [column.name for column in self.model_class.__table__.columns 
                             if str(column.type).startswith('VARCHAR')]
                
                # Costruisci la query di ricerca
                conditions = []
                for field in fields:
                    if hasattr(self.model_class, field):
                        conditions.append(
                            getattr(self.model_class, field).ilike(f'%{search_term}%')
                        )
                
                if conditions:
                    query = query.filter(or_(*conditions))
                
                return query.all()
                
        except SQLAlchemyError as e:
            self.logger.error(f"Errore nella ricerca '{search_term}': {e}")
            return []
    
    def count(self, active_only: bool = True) -> int:
        """
        Conta i record.
        
        Args:
            active_only: Se True, conta solo i record attivi
            
        Returns:
            Numero di record
        """
        try:
            with self.db_manager.get_session_context() as session:
                query = session.query(self.model_class)
                
                if active_only and hasattr(self.model_class, 'attivo'):
                    query = query.filter(self.model_class.attivo == True)
                
                return query.count()
                
        except SQLAlchemyError as e:
            self.logger.error(f"Errore nel conteggio dei record: {e}")
            return 0
    
    def exists(self, **kwargs) -> bool:
        """
        Verifica se esiste un record con i criteri specificati.
        
        Args:
            **kwargs: Criteri di ricerca
            
        Returns:
            True se esiste, False altrimenti
        """
        try:
            with self.db_manager.get_session_context() as session:
                query = session.query(self.model_class)
                
                for key, value in kwargs.items():
                    if hasattr(self.model_class, key):
                        query = query.filter(getattr(self.model_class, key) == value)
                
                return query.first() is not None
                
        except SQLAlchemyError as e:
            self.logger.error(f"Errore nella verifica esistenza: {e}")
            return False
    
    def validate_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Valida i dati di input.
        
        Args:
            data: Dati da validare
            
        Returns:
            Dizionario con eventuali errori di validazione
        """
        errors = {}
        
        # Validazione base - da implementare nelle sottoclassi
        for key, value in data.items():
            if hasattr(self.model_class, key):
                column = getattr(self.model_class.__table__.columns, key, None)
                if column and not column.nullable and not value:
                    errors[key] = f"Il campo {key} è obbligatorio"
        
        return errors