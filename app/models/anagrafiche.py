"""
Modelli per le Anagrafiche
==========================

Definisce i modelli per fornitori, clienti e dipendenti.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Numeric, ForeignKey
# from sqlalchemy.orm import relationship  # commentato temporaneamente

from ..database.base import Base


class Fornitore(Base):
    """Modello per i fornitori."""
    
    __tablename__ = "fornitori"
    
    # Dati anagrafici
    ragione_sociale = Column(String(200), nullable=False)
    partita_iva = Column(String(11), unique=True, nullable=False)
    codice_fiscale = Column(String(16), unique=True, nullable=True)
    codice_fornitore = Column(String(20), unique=True, nullable=False)
    
    # Contatti
    telefono = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    sito_web = Column(String(200), nullable=True)
    
    # Indirizzo
    indirizzo = Column(String(200), nullable=True)
    cap = Column(String(10), nullable=True)
    citta = Column(String(100), nullable=True)
    provincia = Column(String(2), nullable=True)
    nazione = Column(String(50), default="Italia")
    
    # Dati commerciali
    condizioni_pagamento = Column(String(100), nullable=True)
    sconto_percentuale = Column(Numeric(5, 2), default=0.0)
    
    # Stato
    attivo = Column(Boolean, default=True)
    note = Column(Text, nullable=True)
    
    # Relazioni (commentate temporaneamente fino alla creazione del modello Fattura)
    # fatture = relationship("Fattura", back_populates="fornitore")
    
    def __repr__(self) -> str:
        return f"<Fornitore(ragione_sociale='{self.ragione_sociale}', partita_iva='{self.partita_iva}')>"
    
    def get_full_address(self) -> str:
        """Restituisce l'indirizzo completo formattato."""
        parts = [self.indirizzo, self.cap, self.citta, self.provincia, self.nazione]
        return ", ".join(filter(None, parts))
    
    def is_valid_partita_iva(self) -> bool:
        """Verifica se la partita IVA è valida (controllo di base)."""
        if not self.partita_iva:
            return False
        return len(self.partita_iva) == 11 and self.partita_iva.isdigit()


class Cliente(Base):
    """Modello per i clienti."""
    
    __tablename__ = "clienti"
    
    # Dati anagrafici
    ragione_sociale = Column(String(200), nullable=False)
    partita_iva = Column(String(11), unique=True, nullable=True)
    codice_fiscale = Column(String(16), unique=True, nullable=True)
    codice_cliente = Column(String(20), unique=True, nullable=False)
    
    # Tipo cliente
    tipo_cliente = Column(String(20), default="Azienda")  # Azienda, Privato
    
    # Contatti
    telefono = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    sito_web = Column(String(200), nullable=True)
    
    # Indirizzo
    indirizzo = Column(String(200), nullable=True)
    cap = Column(String(10), nullable=True)
    citta = Column(String(100), nullable=True)
    provincia = Column(String(2), nullable=True)
    nazione = Column(String(50), default="Italia")
    
    # Dati commerciali
    condizioni_pagamento = Column(String(100), nullable=True)
    sconto_percentuale = Column(Numeric(5, 2), default=0.0)
    fido_massimo = Column(Numeric(10, 2), default=0.0)
    
    # Stato
    attivo = Column(Boolean, default=True)
    note = Column(Text, nullable=True)
    
    # Relazioni (commentate temporaneamente fino alla creazione del modello Fattura)
    # fatture = relationship("Fattura", back_populates="cliente")
    
    def __repr__(self) -> str:
        return f"<Cliente(ragione_sociale='{self.ragione_sociale}', codice_cliente='{self.codice_cliente}')>"
    
    def get_full_address(self) -> str:
        """Restituisce l'indirizzo completo formattato."""
        parts = [self.indirizzo, self.cap, self.citta, self.provincia, self.nazione]
        return ", ".join(filter(None, parts))
    
    def is_valid_partita_iva(self) -> bool:
        """Verifica se la partita IVA è valida (controllo di base)."""
        if not self.partita_iva:
            return True  # Opzionale per i clienti privati
        return len(self.partita_iva) == 11 and self.partita_iva.isdigit()


class Dipendente(Base):
    """Modello per i dipendenti."""
    
    __tablename__ = "dipendenti"
    
    # Dati anagrafici
    nome = Column(String(100), nullable=False)
    cognome = Column(String(100), nullable=False)
    codice_fiscale = Column(String(16), unique=True, nullable=False)
    matricola = Column(String(20), unique=True, nullable=False)
    
    # Dati personali
    data_nascita = Column(DateTime, nullable=True)
    luogo_nascita = Column(String(100), nullable=True)
    
    # Contatti
    telefono = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    
    # Indirizzo
    indirizzo = Column(String(200), nullable=True)
    cap = Column(String(10), nullable=True)
    citta = Column(String(100), nullable=True)
    provincia = Column(String(2), nullable=True)
    nazione = Column(String(50), default="Italia")
    
    # Dati lavorativi
    mansione = Column(String(100), nullable=True)
    dipartimento = Column(String(100), nullable=True)
    data_assunzione = Column(DateTime, nullable=True)
    data_cessazione = Column(DateTime, nullable=True)
    stipendio_base = Column(Numeric(10, 2), nullable=True)
    
    # Stato
    attivo = Column(Boolean, default=True)
    note = Column(Text, nullable=True)
    
    def __repr__(self) -> str:
        return f"<Dipendente(nome='{self.nome}', cognome='{self.cognome}', matricola='{self.matricola}')>"
    
    def get_full_name(self) -> str:
        """Restituisce il nome completo."""
        return f"{self.nome} {self.cognome}"
    
    def get_full_address(self) -> str:
        """Restituisce l'indirizzo completo formattato."""
        parts = [self.indirizzo, self.cap, self.citta, self.provincia, self.nazione]
        return ", ".join(filter(None, parts))
    
    def is_active(self) -> bool:
        """Verifica se il dipendente è attivo."""
        return self.attivo and (self.data_cessazione is None or self.data_cessazione > datetime.now())
    
    def calculate_age(self) -> Optional[int]:
        """Calcola l'età del dipendente."""
        if not self.data_nascita:
            return None
        
        today = datetime.now()
        age = today.year - self.data_nascita.year
        if today.month < self.data_nascita.month or (today.month == self.data_nascita.month and today.day < self.data_nascita.day):
            age -= 1
        return age