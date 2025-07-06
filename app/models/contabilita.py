"""
Modelli per la Contabilità Generale
===================================

Definisce i modelli per i conti contabili e i movimenti contabili.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Numeric, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from ..database.base import Base


class TipoConto(enum.Enum):
    """Tipi di conto contabile."""
    ATTIVO = "attivo"
    PASSIVO = "passivo"
    RICAVO = "ricavo"
    COSTO = "costo"
    CAPITALE = "capitale"


class ContoContabile(Base):
    """Modello per i conti contabili."""
    
    __tablename__ = "conti_contabili"
    
    # Dati del conto
    codice = Column(String(20), unique=True, nullable=False)
    descrizione = Column(String(200), nullable=False)
    tipo_conto = Column(Enum(TipoConto), nullable=False)
    
    # Struttura gerarchica
    conto_padre_id = Column(Integer, ForeignKey("conti_contabili.id"), nullable=True)
    livello = Column(Integer, default=1)
    
    # Configurazione
    attivo = Column(Boolean, default=True)
    utilizzabile = Column(Boolean, default=True)  # Se False, è solo un raggruppamento
    
    # Saldi
    saldo_iniziale = Column(Numeric(12, 2), default=0.0)
    saldo_dare = Column(Numeric(12, 2), default=0.0)
    saldo_avere = Column(Numeric(12, 2), default=0.0)
    
    # Relazioni (commentate temporaneamente per risolvere problemi di configurazione)
    # conto_padre = relationship("ContoContabile", remote_side=[id], back_populates="conti_figli")
    # conti_figli = relationship("ContoContabile", back_populates="conto_padre")
    # movimenti_dare = relationship("MovimentoContabile", 
    #                              foreign_keys="MovimentoContabile.conto_dare_id",
    #                              back_populates="conto_dare")
    # movimenti_avere = relationship("MovimentoContabile", 
    #                               foreign_keys="MovimentoContabile.conto_avere_id",
    #                               back_populates="conto_avere")
    
    def __repr__(self) -> str:
        return f"<ContoContabile(codice='{self.codice}', descrizione='{self.descrizione}')>"
    
    def get_saldo_attuale(self) -> float:
        """Calcola il saldo attuale del conto."""
        saldo_base = float(self.saldo_iniziale)
        
        if self.tipo_conto in [TipoConto.ATTIVO, TipoConto.COSTO]:
            # Conti a saldi dare
            return saldo_base + float(self.saldo_dare) - float(self.saldo_avere)
        else:
            # Conti a saldi avere
            return saldo_base + float(self.saldo_avere) - float(self.saldo_dare)
    
    def get_codice_completo(self) -> str:
        """Restituisce il codice completo con la gerarchia."""
        if self.conto_padre:
            return f"{self.conto_padre.get_codice_completo()}.{self.codice}"
        return self.codice
    
    def get_descrizione_completa(self) -> str:
        """Restituisce la descrizione completa con la gerarchia."""
        if self.conto_padre:
            return f"{self.conto_padre.get_descrizione_completa()} > {self.descrizione}"
        return self.descrizione
    
    def is_foglia(self) -> bool:
        """Verifica se il conto è una foglia (non ha conti figli)."""
        return len(self.conti_figli) == 0
    
    def aggiorna_saldo(self, importo_dare: float = 0.0, importo_avere: float = 0.0) -> None:
        """Aggiorna i saldi del conto."""
        self.saldo_dare += importo_dare
        self.saldo_avere += importo_avere


class MovimentoContabile(Base):
    """Modello per i movimenti contabili."""
    
    __tablename__ = "movimenti_contabili"
    
    # Dati del movimento
    numero_movimento = Column(String(20), unique=True, nullable=False)
    data_movimento = Column(DateTime, nullable=False, default=datetime.now)
    data_registrazione = Column(DateTime, nullable=False, default=datetime.now)
    
    # Causale
    causale = Column(String(200), nullable=False)
    descrizione = Column(Text, nullable=True)
    
    # Conti
    conto_dare_id = Column(Integer, ForeignKey("conti_contabili.id"), nullable=False)
    conto_avere_id = Column(Integer, ForeignKey("conti_contabili.id"), nullable=False)
    
    # Importi
    importo = Column(Numeric(10, 2), nullable=False)
    
    # Riferimenti
    documento_riferimento = Column(String(100), nullable=True)
    numero_documento = Column(String(50), nullable=True)
    
    # Relazioni (commentate temporaneamente)
    # conto_dare = relationship("ContoContabile", 
    #                          foreign_keys=[conto_dare_id],
    #                          back_populates="movimenti_dare")
    # conto_avere = relationship("ContoContabile", 
    #                           foreign_keys=[conto_avere_id],
    #                           back_populates="movimenti_avere")
    
    def __repr__(self) -> str:
        return f"<MovimentoContabile(numero='{self.numero_movimento}', causale='{self.causale}', importo={self.importo})>"
    
    def is_valido(self) -> bool:
        """Verifica se il movimento è valido."""
        return (self.conto_dare_id != self.conto_avere_id and 
                self.importo > 0 and 
                self.causale.strip() != "")
    
    def get_descrizione_completa(self) -> str:
        """Restituisce una descrizione completa del movimento."""
        dare_desc = self.conto_dare.descrizione if self.conto_dare else "N/A"
        avere_desc = self.conto_avere.descrizione if self.conto_avere else "N/A"
        return f"{dare_desc} a {avere_desc} - {self.causale}"


# Funzioni di utilità per la gestione dei conti
def crea_piano_conti_base() -> List[ContoContabile]:
    """Crea un piano dei conti di base."""
    conti = []
    
    # Conti principali
    conti_principali = [
        {"codice": "1", "descrizione": "ATTIVO", "tipo": TipoConto.ATTIVO, "utilizzabile": False},
        {"codice": "2", "descrizione": "PASSIVO", "tipo": TipoConto.PASSIVO, "utilizzabile": False},
        {"codice": "3", "descrizione": "CAPITALE", "tipo": TipoConto.CAPITALE, "utilizzabile": False},
        {"codice": "4", "descrizione": "RICAVI", "tipo": TipoConto.RICAVO, "utilizzabile": False},
        {"codice": "5", "descrizione": "COSTI", "tipo": TipoConto.COSTO, "utilizzabile": False},
    ]
    
    # Sottocategorie esempio
    sottocategorie = [
        # Attivo
        {"codice": "11", "descrizione": "Attivo Circolante", "tipo": TipoConto.ATTIVO, "padre": "1"},
        {"codice": "12", "descrizione": "Attivo Immobilizzato", "tipo": TipoConto.ATTIVO, "padre": "1"},
        {"codice": "111", "descrizione": "Cassa", "tipo": TipoConto.ATTIVO, "padre": "11"},
        {"codice": "112", "descrizione": "Banca", "tipo": TipoConto.ATTIVO, "padre": "11"},
        {"codice": "113", "descrizione": "Clienti", "tipo": TipoConto.ATTIVO, "padre": "11"},
        
        # Passivo
        {"codice": "21", "descrizione": "Debiti", "tipo": TipoConto.PASSIVO, "padre": "2"},
        {"codice": "211", "descrizione": "Fornitori", "tipo": TipoConto.PASSIVO, "padre": "21"},
        {"codice": "212", "descrizione": "Debiti Tributari", "tipo": TipoConto.PASSIVO, "padre": "21"},
        
        # Ricavi
        {"codice": "41", "descrizione": "Ricavi da Vendite", "tipo": TipoConto.RICAVO, "padre": "4"},
        {"codice": "42", "descrizione": "Altri Ricavi", "tipo": TipoConto.RICAVO, "padre": "4"},
        
        # Costi
        {"codice": "51", "descrizione": "Costi per Materie Prime", "tipo": TipoConto.COSTO, "padre": "5"},
        {"codice": "52", "descrizione": "Costi per Servizi", "tipo": TipoConto.COSTO, "padre": "5"},
        {"codice": "53", "descrizione": "Costi del Personale", "tipo": TipoConto.COSTO, "padre": "5"},
    ]
    
    # Crea i conti principali
    for conto_data in conti_principali:
        conto = ContoContabile(
            codice=conto_data["codice"],
            descrizione=conto_data["descrizione"],
            tipo_conto=conto_data["tipo"],
            utilizzabile=conto_data.get("utilizzabile", True),
            livello=1
        )
        conti.append(conto)
    
    # Mappa dei conti per padre
    conti_map = {c.codice: c for c in conti}
    
    # Crea le sottocategorie
    for conto_data in sottocategorie:
        conto = ContoContabile(
            codice=conto_data["codice"],
            descrizione=conto_data["descrizione"],
            tipo_conto=conto_data["tipo"],
            utilizzabile=conto_data.get("utilizzabile", True),
            livello=len(conto_data["codice"])
        )
        
        # Imposta il padre se specificato
        if "padre" in conto_data and conto_data["padre"] in conti_map:
            conto.conto_padre = conti_map[conto_data["padre"]]
        
        conti.append(conto)
        conti_map[conto.codice] = conto
    
    return conti