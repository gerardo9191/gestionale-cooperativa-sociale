"""
Modelli per i Documenti Contabili
=================================

Definisce i modelli per fatture, note credito e prima nota.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Numeric, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from ..database.base import Base


class TipoDocumento(enum.Enum):
    """Tipi di documento contabile."""
    FATTURA_VENDITA = "fattura_vendita"
    FATTURA_ACQUISTO = "fattura_acquisto"
    NOTA_CREDITO = "nota_credito"
    PRIMA_NOTA = "prima_nota"


class StatoDocumento(enum.Enum):
    """Stati del documento."""
    BOZZA = "bozza"
    EMESSO = "emesso"
    PAGATO = "pagato"
    ANNULLATO = "annullato"


class Fattura(Base):
    """Modello per le fatture."""
    
    __tablename__ = "fatture"
    
    # Dati del documento
    numero_fattura = Column(String(20), unique=True, nullable=False)
    data_fattura = Column(DateTime, nullable=False, default=datetime.now)
    data_scadenza = Column(DateTime, nullable=True)
    tipo_documento = Column(Enum(TipoDocumento), nullable=False)
    stato = Column(Enum(StatoDocumento), default=StatoDocumento.BOZZA)
    
    # Relazioni con anagrafiche
    cliente_id = Column(Integer, ForeignKey("clienti.id"), nullable=True)
    fornitore_id = Column(Integer, ForeignKey("fornitori.id"), nullable=True)
    
    # Importi
    imponibile = Column(Numeric(10, 2), nullable=False, default=0.0)
    iva = Column(Numeric(10, 2), nullable=False, default=0.0)
    totale = Column(Numeric(10, 2), nullable=False, default=0.0)
    sconto_percentuale = Column(Numeric(5, 2), default=0.0)
    sconto_importo = Column(Numeric(10, 2), default=0.0)
    
    # Dati aggiuntivi
    oggetto = Column(String(200), nullable=True)
    note = Column(Text, nullable=True)
    pagata = Column(Boolean, default=False)
    data_pagamento = Column(DateTime, nullable=True)
    
    # Relazioni (commentate temporaneamente)
    # cliente = relationship("Cliente", back_populates="fatture")
    # fornitore = relationship("Fornitore", back_populates="fatture")
    righe = relationship("RigaFattura", back_populates="fattura", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Fattura(numero='{self.numero_fattura}', data='{self.data_fattura}', totale={self.totale})>"
    
    def calcola_totali(self) -> None:
        """Calcola i totali della fattura dalle righe."""
        if not self.righe:
            self.imponibile = 0.0
            self.iva = 0.0
            self.totale = 0.0
            return
        
        # Calcola imponibile
        self.imponibile = sum(riga.get_subtotale() for riga in self.righe)
        
        # Applica sconto
        if self.sconto_percentuale > 0:
            self.sconto_importo = self.imponibile * (self.sconto_percentuale / 100)
            self.imponibile -= self.sconto_importo
        
        # Calcola IVA
        self.iva = sum(riga.get_iva() for riga in self.righe)
        
        # Calcola totale
        self.totale = self.imponibile + self.iva
    
    def is_scaduta(self) -> bool:
        """Verifica se la fattura è scaduta."""
        if not self.data_scadenza or self.pagata:
            return False
        return datetime.now() > self.data_scadenza
    
    def get_giorni_scadenza(self) -> Optional[int]:
        """Restituisce i giorni alla scadenza (negativi se scaduta)."""
        if not self.data_scadenza:
            return None
        delta = self.data_scadenza - datetime.now()
        return delta.days


class RigaFattura(Base):
    """Modello per le righe delle fatture."""
    
    __tablename__ = "righe_fattura"
    
    # Relazione con la fattura
    fattura_id = Column(Integer, ForeignKey("fatture.id"), nullable=False)
    
    # Dati della riga
    descrizione = Column(String(300), nullable=False)
    quantita = Column(Numeric(10, 3), nullable=False, default=1.0)
    prezzo_unitario = Column(Numeric(10, 2), nullable=False, default=0.0)
    aliquota_iva = Column(Numeric(5, 2), nullable=False, default=22.0)
    
    # Sconti
    sconto_percentuale = Column(Numeric(5, 2), default=0.0)
    sconto_importo = Column(Numeric(10, 2), default=0.0)
    
    # Relazioni
    fattura = relationship("Fattura", back_populates="righe")
    
    def __repr__(self) -> str:
        return f"<RigaFattura(descrizione='{self.descrizione[:30]}...', quantita={self.quantita}, prezzo={self.prezzo_unitario})>"
    
    def get_subtotale(self) -> float:
        """Calcola il subtotale della riga (senza IVA)."""
        subtotale = float(self.quantita) * float(self.prezzo_unitario)
        
        # Applica sconto percentuale
        if self.sconto_percentuale > 0:
            subtotale *= (1 - float(self.sconto_percentuale) / 100)
        
        # Applica sconto importo
        if self.sconto_importo > 0:
            subtotale -= float(self.sconto_importo)
        
        return max(0.0, subtotale)
    
    def get_iva(self) -> float:
        """Calcola l'IVA della riga."""
        return self.get_subtotale() * (float(self.aliquota_iva) / 100)
    
    def get_totale(self) -> float:
        """Calcola il totale della riga (con IVA)."""
        return self.get_subtotale() + self.get_iva()


class NotaCredito(Base):
    """Modello per le note di credito."""
    
    __tablename__ = "note_credito"
    
    # Dati del documento
    numero_nota = Column(String(20), unique=True, nullable=False)
    data_nota = Column(DateTime, nullable=False, default=datetime.now)
    stato = Column(Enum(StatoDocumento), default=StatoDocumento.BOZZA)
    
    # Relazioni
    fattura_id = Column(Integer, ForeignKey("fatture.id"), nullable=True)
    cliente_id = Column(Integer, ForeignKey("clienti.id"), nullable=True)
    fornitore_id = Column(Integer, ForeignKey("fornitori.id"), nullable=True)
    
    # Importi
    imponibile = Column(Numeric(10, 2), nullable=False, default=0.0)
    iva = Column(Numeric(10, 2), nullable=False, default=0.0)
    totale = Column(Numeric(10, 2), nullable=False, default=0.0)
    
    # Dati aggiuntivi
    motivo = Column(String(300), nullable=False)
    note = Column(Text, nullable=True)
    
    # Relazioni (commentate temporaneamente)
    # fattura = relationship("Fattura")
    # cliente = relationship("Cliente")
    # fornitore = relationship("Fornitore")
    righe = relationship("RigaNotaCredito", back_populates="nota_credito", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<NotaCredito(numero='{self.numero_nota}', data='{self.data_nota}', totale={self.totale})>"
    
    def calcola_totali(self) -> None:
        """Calcola i totali della nota di credito."""
        if not self.righe:
            self.imponibile = 0.0
            self.iva = 0.0
            self.totale = 0.0
            return
        
        self.imponibile = sum(riga.get_subtotale() for riga in self.righe)
        self.iva = sum(riga.get_iva() for riga in self.righe)
        self.totale = self.imponibile + self.iva


class RigaNotaCredito(Base):
    """Modello per le righe delle note di credito."""
    
    __tablename__ = "righe_nota_credito"
    
    # Relazione con la nota di credito
    nota_credito_id = Column(Integer, ForeignKey("note_credito.id"), nullable=False)
    
    # Dati della riga
    descrizione = Column(String(300), nullable=False)
    quantita = Column(Numeric(10, 3), nullable=False, default=1.0)
    prezzo_unitario = Column(Numeric(10, 2), nullable=False, default=0.0)
    aliquota_iva = Column(Numeric(5, 2), nullable=False, default=22.0)
    
    # Relazioni
    nota_credito = relationship("NotaCredito", back_populates="righe")
    
    def __repr__(self) -> str:
        return f"<RigaNotaCredito(descrizione='{self.descrizione[:30]}...', quantita={self.quantita})>"
    
    def get_subtotale(self) -> float:
        """Calcola il subtotale della riga (senza IVA)."""
        return float(self.quantita) * float(self.prezzo_unitario)
    
    def get_iva(self) -> float:
        """Calcola l'IVA della riga."""
        return self.get_subtotale() * (float(self.aliquota_iva) / 100)
    
    def get_totale(self) -> float:
        """Calcola il totale della riga (con IVA)."""
        return self.get_subtotale() + self.get_iva()


class PrimaNota(Base):
    """Modello per le registrazioni di prima nota."""
    
    __tablename__ = "prima_nota"
    
    # Dati della registrazione
    numero_registrazione = Column(String(20), unique=True, nullable=False)
    data_registrazione = Column(DateTime, nullable=False, default=datetime.now)
    causale = Column(String(200), nullable=False)
    
    # Importi
    dare = Column(Numeric(10, 2), nullable=False, default=0.0)
    avere = Column(Numeric(10, 2), nullable=False, default=0.0)
    
    # Dati aggiuntivi
    descrizione = Column(Text, nullable=True)
    documento_riferimento = Column(String(100), nullable=True)
    
    # Relazioni
    conto_dare_id = Column(Integer, ForeignKey("conti_contabili.id"), nullable=True)
    conto_avere_id = Column(Integer, ForeignKey("conti_contabili.id"), nullable=True)
    
    def __repr__(self) -> str:
        return f"<PrimaNota(numero='{self.numero_registrazione}', causale='{self.causale}', dare={self.dare}, avere={self.avere})>"
    
    def is_quadrata(self) -> bool:
        """Verifica se la registrazione è quadrata (dare = avere)."""
        return abs(float(self.dare) - float(self.avere)) < 0.01