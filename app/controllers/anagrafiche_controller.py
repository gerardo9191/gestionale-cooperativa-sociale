"""
Controller per le Anagrafiche
=============================

Gestisce le operazioni CRUD per fornitori, clienti e dipendenti.
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime

from .base_controller import BaseController
from ..models.anagrafiche import Fornitore, Cliente, Dipendente
from ..database.connection import DatabaseManager


class AnagraficheController:
    """Controller per la gestione delle anagrafiche."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Inizializza il controller delle anagrafiche.
        
        Args:
            db_manager: Gestore del database
        """
        self.db_manager = db_manager
        self.fornitori_controller = BaseController(db_manager, Fornitore)
        self.clienti_controller = BaseController(db_manager, Cliente)
        self.dipendenti_controller = BaseController(db_manager, Dipendente)
    
    # === FORNITORI ===
    
    def crea_fornitore(self, dati: Dict[str, Any]) -> Optional[Fornitore]:
        """
        Crea un nuovo fornitore.
        
        Args:
            dati: Dati del fornitore
            
        Returns:
            Il fornitore creato o None se errore
        """
        # Valida i dati
        errori = self.valida_dati_fornitore(dati)
        if errori:
            raise ValueError(f"Errori di validazione: {errori}")
        
        # Genera codice fornitore se non presente
        if not dati.get('codice_fornitore'):
            dati['codice_fornitore'] = self._genera_codice_fornitore()
        
        return self.fornitori_controller.create(**dati)
    
    def aggiorna_fornitore(self, fornitore_id: int, dati: Dict[str, Any]) -> Optional[Fornitore]:
        """
        Aggiorna un fornitore esistente.
        
        Args:
            fornitore_id: ID del fornitore
            dati: Dati da aggiornare
            
        Returns:
            Il fornitore aggiornato o None se errore
        """
        # Valida i dati (esclusi quelli non modificabili)
        dati_validazione = dati.copy()
        if 'codice_fornitore' in dati_validazione:
            del dati_validazione['codice_fornitore']
        
        errori = self.valida_dati_fornitore(dati_validazione, is_update=True)
        if errori:
            raise ValueError(f"Errori di validazione: {errori}")
        
        return self.fornitori_controller.update(fornitore_id, **dati)
    
    def elimina_fornitore(self, fornitore_id: int) -> bool:
        """Elimina un fornitore."""
        return self.fornitori_controller.delete(fornitore_id)
    
    def ottieni_fornitore(self, fornitore_id: int) -> Optional[Fornitore]:
        """Recupera un fornitore per ID."""
        return self.fornitori_controller.get_by_id(fornitore_id)
    
    def ottieni_tutti_fornitori(self, solo_attivi: bool = True) -> List[Fornitore]:
        """Recupera tutti i fornitori."""
        return self.fornitori_controller.get_all(active_only=solo_attivi)
    
    def cerca_fornitori(self, termine: str) -> List[Fornitore]:
        """Cerca fornitori per termine."""
        return self.fornitori_controller.search(termine, 
                                               ['ragione_sociale', 'partita_iva', 'codice_fornitore'])
    
    # === CLIENTI ===
    
    def crea_cliente(self, dati: Dict[str, Any]) -> Optional[Cliente]:
        """
        Crea un nuovo cliente.
        
        Args:
            dati: Dati del cliente
            
        Returns:
            Il cliente creato o None se errore
        """
        # Valida i dati
        errori = self.valida_dati_cliente(dati)
        if errori:
            raise ValueError(f"Errori di validazione: {errori}")
        
        # Genera codice cliente se non presente
        if not dati.get('codice_cliente'):
            dati['codice_cliente'] = self._genera_codice_cliente()
        
        return self.clienti_controller.create(**dati)
    
    def aggiorna_cliente(self, cliente_id: int, dati: Dict[str, Any]) -> Optional[Cliente]:
        """
        Aggiorna un cliente esistente.
        
        Args:
            cliente_id: ID del cliente
            dati: Dati da aggiornare
            
        Returns:
            Il cliente aggiornato o None se errore
        """
        # Valida i dati (esclusi quelli non modificabili)
        dati_validazione = dati.copy()
        if 'codice_cliente' in dati_validazione:
            del dati_validazione['codice_cliente']
        
        errori = self.valida_dati_cliente(dati_validazione, is_update=True)
        if errori:
            raise ValueError(f"Errori di validazione: {errori}")
        
        return self.clienti_controller.update(cliente_id, **dati)
    
    def elimina_cliente(self, cliente_id: int) -> bool:
        """Elimina un cliente."""
        return self.clienti_controller.delete(cliente_id)
    
    def ottieni_cliente(self, cliente_id: int) -> Optional[Cliente]:
        """Recupera un cliente per ID."""
        return self.clienti_controller.get_by_id(cliente_id)
    
    def ottieni_tutti_clienti(self, solo_attivi: bool = True) -> List[Cliente]:
        """Recupera tutti i clienti."""
        return self.clienti_controller.get_all(active_only=solo_attivi)
    
    def cerca_clienti(self, termine: str) -> List[Cliente]:
        """Cerca clienti per termine."""
        return self.clienti_controller.search(termine, 
                                             ['ragione_sociale', 'partita_iva', 'codice_cliente'])
    
    # === DIPENDENTI ===
    
    def crea_dipendente(self, dati: Dict[str, Any]) -> Optional[Dipendente]:
        """
        Crea un nuovo dipendente.
        
        Args:
            dati: Dati del dipendente
            
        Returns:
            Il dipendente creato o None se errore
        """
        # Valida i dati
        errori = self.valida_dati_dipendente(dati)
        if errori:
            raise ValueError(f"Errori di validazione: {errori}")
        
        # Genera matricola se non presente
        if not dati.get('matricola'):
            dati['matricola'] = self._genera_matricola()
        
        return self.dipendenti_controller.create(**dati)
    
    def aggiorna_dipendente(self, dipendente_id: int, dati: Dict[str, Any]) -> Optional[Dipendente]:
        """
        Aggiorna un dipendente esistente.
        
        Args:
            dipendente_id: ID del dipendente
            dati: Dati da aggiornare
            
        Returns:
            Il dipendente aggiornato o None se errore
        """
        # Valida i dati (esclusi quelli non modificabili)
        dati_validazione = dati.copy()
        if 'matricola' in dati_validazione:
            del dati_validazione['matricola']
        
        errori = self.valida_dati_dipendente(dati_validazione, is_update=True)
        if errori:
            raise ValueError(f"Errori di validazione: {errori}")
        
        return self.dipendenti_controller.update(dipendente_id, **dati)
    
    def elimina_dipendente(self, dipendente_id: int) -> bool:
        """Elimina un dipendente."""
        return self.dipendenti_controller.delete(dipendente_id)
    
    def ottieni_dipendente(self, dipendente_id: int) -> Optional[Dipendente]:
        """Recupera un dipendente per ID."""
        return self.dipendenti_controller.get_by_id(dipendente_id)
    
    def ottieni_tutti_dipendenti(self, solo_attivi: bool = True) -> List[Dipendente]:
        """Recupera tutti i dipendenti."""
        return self.dipendenti_controller.get_all(active_only=solo_attivi)
    
    def cerca_dipendenti(self, termine: str) -> List[Dipendente]:
        """Cerca dipendenti per termine."""
        return self.dipendenti_controller.search(termine, 
                                                ['nome', 'cognome', 'matricola', 'codice_fiscale'])
    
    # === VALIDAZIONE ===
    
    def valida_dati_fornitore(self, dati: Dict[str, Any], is_update: bool = False) -> Dict[str, str]:
        """
        Valida i dati di un fornitore.
        
        Args:
            dati: Dati da validare
            is_update: Se True, è un aggiornamento (alcuni campi possono essere omessi)
            
        Returns:
            Dizionario con eventuali errori
        """
        errori = {}
        
        # Campi obbligatori
        campi_obbligatori = ['ragione_sociale', 'partita_iva']
        if not is_update:
            for campo in campi_obbligatori:
                if not dati.get(campo):
                    errori[campo] = f"Il campo {campo} è obbligatorio"
        
        # Validazione Partita IVA
        if 'partita_iva' in dati and dati['partita_iva']:
            if not self._valida_partita_iva(dati['partita_iva']):
                errori['partita_iva'] = "Partita IVA non valida"
        
        # Validazione Codice Fiscale
        if 'codice_fiscale' in dati and dati['codice_fiscale']:
            if not self._valida_codice_fiscale(dati['codice_fiscale']):
                errori['codice_fiscale'] = "Codice fiscale non valido"
        
        # Validazione Email
        if 'email' in dati and dati['email']:
            if not self._valida_email(dati['email']):
                errori['email'] = "Email non valida"
        
        return errori
    
    def valida_dati_cliente(self, dati: Dict[str, Any], is_update: bool = False) -> Dict[str, str]:
        """
        Valida i dati di un cliente.
        
        Args:
            dati: Dati da validare
            is_update: Se True, è un aggiornamento
            
        Returns:
            Dizionario con eventuali errori
        """
        errori = {}
        
        # Campi obbligatori
        campi_obbligatori = ['ragione_sociale']
        if not is_update:
            for campo in campi_obbligatori:
                if not dati.get(campo):
                    errori[campo] = f"Il campo {campo} è obbligatorio"
        
        # Validazione Partita IVA (opzionale per clienti)
        if 'partita_iva' in dati and dati['partita_iva']:
            if not self._valida_partita_iva(dati['partita_iva']):
                errori['partita_iva'] = "Partita IVA non valida"
        
        # Validazione Codice Fiscale
        if 'codice_fiscale' in dati and dati['codice_fiscale']:
            if not self._valida_codice_fiscale(dati['codice_fiscale']):
                errori['codice_fiscale'] = "Codice fiscale non valido"
        
        # Validazione Email
        if 'email' in dati and dati['email']:
            if not self._valida_email(dati['email']):
                errori['email'] = "Email non valida"
        
        return errori
    
    def valida_dati_dipendente(self, dati: Dict[str, Any], is_update: bool = False) -> Dict[str, str]:
        """
        Valida i dati di un dipendente.
        
        Args:
            dati: Dati da validare
            is_update: Se True, è un aggiornamento
            
        Returns:
            Dizionario con eventuali errori
        """
        errori = {}
        
        # Campi obbligatori
        campi_obbligatori = ['nome', 'cognome', 'codice_fiscale']
        if not is_update:
            for campo in campi_obbligatori:
                if not dati.get(campo):
                    errori[campo] = f"Il campo {campo} è obbligatorio"
        
        # Validazione Codice Fiscale
        if 'codice_fiscale' in dati and dati['codice_fiscale']:
            if not self._valida_codice_fiscale(dati['codice_fiscale']):
                errori['codice_fiscale'] = "Codice fiscale non valido"
        
        # Validazione Email
        if 'email' in dati and dati['email']:
            if not self._valida_email(dati['email']):
                errori['email'] = "Email non valida"
        
        # Validazione Date
        if 'data_nascita' in dati and dati['data_nascita']:
            if isinstance(dati['data_nascita'], str):
                try:
                    datetime.strptime(dati['data_nascita'], '%Y-%m-%d')
                except ValueError:
                    errori['data_nascita'] = "Formato data non valido (YYYY-MM-DD)"
        
        return errori
    
    # === METODI PRIVATI ===
    
    def _genera_codice_fornitore(self) -> str:
        """Genera un codice fornitore univoco."""
        count = self.fornitori_controller.count(active_only=False)
        return f"FOR{count + 1:05d}"
    
    def _genera_codice_cliente(self) -> str:
        """Genera un codice cliente univoco."""
        count = self.clienti_controller.count(active_only=False)
        return f"CLI{count + 1:05d}"
    
    def _genera_matricola(self) -> str:
        """Genera una matricola univoca."""
        count = self.dipendenti_controller.count(active_only=False)
        return f"DIP{count + 1:05d}"
    
    def _valida_partita_iva(self, partita_iva: str) -> bool:
        """Valida il formato della partita IVA italiana."""
        if not partita_iva or len(partita_iva) != 11:
            return False
        
        return partita_iva.isdigit()
    
    def _valida_codice_fiscale(self, codice_fiscale: str) -> bool:
        """Valida il formato del codice fiscale italiano."""
        if not codice_fiscale or len(codice_fiscale) != 16:
            return False
        
        # Controllo formato base
        pattern = r'^[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]$'
        return bool(re.match(pattern, codice_fiscale.upper()))
    
    def _valida_email(self, email: str) -> bool:
        """Valida il formato dell'email."""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    # === STATISTICHE ===
    
    def ottieni_statistiche(self) -> Dict[str, Any]:
        """Ottiene statistiche sulle anagrafiche."""
        return {
            'fornitori': {
                'totale': self.fornitori_controller.count(active_only=False),
                'attivi': self.fornitori_controller.count(active_only=True)
            },
            'clienti': {
                'totale': self.clienti_controller.count(active_only=False),
                'attivi': self.clienti_controller.count(active_only=True)
            },
            'dipendenti': {
                'totale': self.dipendenti_controller.count(active_only=False),
                'attivi': self.dipendenti_controller.count(active_only=True)
            }
        }