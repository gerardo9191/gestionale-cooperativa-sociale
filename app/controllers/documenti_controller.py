"""
Controller per i Documenti Contabili
====================================

Gestisce le operazioni CRUD per fatture, note credito e prima nota.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from .base_controller import BaseController
from ..models.documenti import Fattura, RigaFattura, NotaCredito, RigaNotaCredito, PrimaNota, TipoDocumento, StatoDocumento
from ..database.connection import DatabaseManager


class DocumentiController:
    """Controller per la gestione dei documenti contabili."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Inizializza il controller dei documenti.
        
        Args:
            db_manager: Gestore del database
        """
        self.db_manager = db_manager
        self.fatture_controller = BaseController(db_manager, Fattura)
        self.righe_fattura_controller = BaseController(db_manager, RigaFattura)
        self.note_credito_controller = BaseController(db_manager, NotaCredito)
        self.righe_nota_credito_controller = BaseController(db_manager, RigaNotaCredito)
        self.prima_nota_controller = BaseController(db_manager, PrimaNota)
    
    # === FATTURE ===
    
    def crea_fattura(self, dati: Dict[str, Any]) -> Optional[Fattura]:
        """
        Crea una nuova fattura.
        
        Args:
            dati: Dati della fattura
            
        Returns:
            La fattura creata o None se errore
        """
        # Valida i dati
        errori = self.valida_dati_fattura(dati)
        if errori:
            raise ValueError(f"Errori di validazione: {errori}")
        
        # Genera numero fattura se non presente
        if not dati.get('numero_fattura'):
            dati['numero_fattura'] = self._genera_numero_fattura(dati.get('tipo_documento', TipoDocumento.FATTURA_VENDITA))
        
        # Imposta data scadenza se non presente
        if not dati.get('data_scadenza') and dati.get('data_fattura'):
            dati['data_scadenza'] = self._calcola_data_scadenza(dati['data_fattura'])
        
        try:
            with self.db_manager.get_session_context() as session:
                # Crea la fattura
                fattura = Fattura(**dati)
                session.add(fattura)
                session.flush()  # Per ottenere l'ID
                
                # Aggiungi righe se presenti
                if 'righe' in dati:
                    for riga_dati in dati['righe']:
                        riga_dati['fattura_id'] = fattura.id
                        riga = RigaFattura(**riga_dati)
                        session.add(riga)
                
                # Calcola totali
                session.commit()
                session.refresh(fattura)
                fattura.calcola_totali()
                session.commit()
                
                return fattura
                
        except Exception as e:
            raise ValueError(f"Errore nella creazione della fattura: {e}")
    
    def aggiorna_fattura(self, fattura_id: int, dati: Dict[str, Any]) -> Optional[Fattura]:
        """
        Aggiorna una fattura esistente.
        
        Args:
            fattura_id: ID della fattura
            dati: Dati da aggiornare
            
        Returns:
            La fattura aggiornata o None se errore
        """
        try:
            with self.db_manager.get_session_context() as session:
                fattura = session.query(Fattura).filter(Fattura.id == fattura_id).first()
                if not fattura:
                    raise ValueError("Fattura non trovata")
                
                # Aggiorna i dati della fattura
                for key, value in dati.items():
                    if key != 'righe' and hasattr(fattura, key):
                        setattr(fattura, key, value)
                
                # Aggiorna le righe se presenti
                if 'righe' in dati:
                    # Rimuovi righe esistenti
                    for riga in fattura.righe:
                        session.delete(riga)
                    
                    # Aggiungi nuove righe
                    for riga_dati in dati['righe']:
                        riga_dati['fattura_id'] = fattura.id
                        riga = RigaFattura(**riga_dati)
                        session.add(riga)
                
                # Calcola totali
                session.commit()
                session.refresh(fattura)
                fattura.calcola_totali()
                session.commit()
                
                return fattura
                
        except Exception as e:
            raise ValueError(f"Errore nell'aggiornamento della fattura: {e}")
    
    def elimina_fattura(self, fattura_id: int) -> bool:
        """Elimina una fattura."""
        return self.fatture_controller.delete(fattura_id)
    
    def ottieni_fattura(self, fattura_id: int) -> Optional[Fattura]:
        """Recupera una fattura per ID."""
        return self.fatture_controller.get_by_id(fattura_id)
    
    def ottieni_tutte_fatture(self) -> List[Fattura]:
        """Recupera tutte le fatture."""
        return self.fatture_controller.get_all(active_only=False)
    
    def cerca_fatture(self, termine: str) -> List[Fattura]:
        """Cerca fatture per termine."""
        return self.fatture_controller.search(termine, ['numero_fattura', 'oggetto'])
    
    def ottieni_fatture_per_cliente(self, cliente_id: int) -> List[Fattura]:
        """Recupera tutte le fatture di un cliente."""
        try:
            with self.db_manager.get_session_context() as session:
                return session.query(Fattura).filter(Fattura.cliente_id == cliente_id).all()
        except Exception:
            return []
    
    def ottieni_fatture_per_fornitore(self, fornitore_id: int) -> List[Fattura]:
        """Recupera tutte le fatture di un fornitore."""
        try:
            with self.db_manager.get_session_context() as session:
                return session.query(Fattura).filter(Fattura.fornitore_id == fornitore_id).all()
        except Exception:
            return []
    
    def ottieni_fatture_scadute(self) -> List[Fattura]:
        """Recupera tutte le fatture scadute."""
        try:
            with self.db_manager.get_session_context() as session:
                return session.query(Fattura).filter(
                    Fattura.data_scadenza < datetime.now(),
                    Fattura.pagata == False
                ).all()
        except Exception:
            return []
    
    def segna_fattura_pagata(self, fattura_id: int, data_pagamento: datetime = None) -> bool:
        """Segna una fattura come pagata."""
        try:
            if not data_pagamento:
                data_pagamento = datetime.now()
            
            return self.fatture_controller.update(fattura_id, 
                                                 pagata=True, 
                                                 data_pagamento=data_pagamento,
                                                 stato=StatoDocumento.PAGATO) is not None
        except Exception:
            return False
    
    # === NOTE CREDITO ===
    
    def crea_nota_credito(self, dati: Dict[str, Any]) -> Optional[NotaCredito]:
        """
        Crea una nuova nota di credito.
        
        Args:
            dati: Dati della nota di credito
            
        Returns:
            La nota di credito creata o None se errore
        """
        # Valida i dati
        errori = self.valida_dati_nota_credito(dati)
        if errori:
            raise ValueError(f"Errori di validazione: {errori}")
        
        # Genera numero nota se non presente
        if not dati.get('numero_nota'):
            dati['numero_nota'] = self._genera_numero_nota_credito()
        
        try:
            with self.db_manager.get_session_context() as session:
                # Crea la nota di credito
                nota = NotaCredito(**dati)
                session.add(nota)
                session.flush()  # Per ottenere l'ID
                
                # Aggiungi righe se presenti
                if 'righe' in dati:
                    for riga_dati in dati['righe']:
                        riga_dati['nota_credito_id'] = nota.id
                        riga = RigaNotaCredito(**riga_dati)
                        session.add(riga)
                
                # Calcola totali
                session.commit()
                session.refresh(nota)
                nota.calcola_totali()
                session.commit()
                
                return nota
                
        except Exception as e:
            raise ValueError(f"Errore nella creazione della nota di credito: {e}")
    
    def aggiorna_nota_credito(self, nota_id: int, dati: Dict[str, Any]) -> Optional[NotaCredito]:
        """
        Aggiorna una nota di credito esistente.
        
        Args:
            nota_id: ID della nota di credito
            dati: Dati da aggiornare
            
        Returns:
            La nota di credito aggiornata o None se errore
        """
        try:
            with self.db_manager.get_session_context() as session:
                nota = session.query(NotaCredito).filter(NotaCredito.id == nota_id).first()
                if not nota:
                    raise ValueError("Nota di credito non trovata")
                
                # Aggiorna i dati della nota
                for key, value in dati.items():
                    if key != 'righe' and hasattr(nota, key):
                        setattr(nota, key, value)
                
                # Aggiorna le righe se presenti
                if 'righe' in dati:
                    # Rimuovi righe esistenti
                    for riga in nota.righe:
                        session.delete(riga)
                    
                    # Aggiungi nuove righe
                    for riga_dati in dati['righe']:
                        riga_dati['nota_credito_id'] = nota.id
                        riga = RigaNotaCredito(**riga_dati)
                        session.add(riga)
                
                # Calcola totali
                session.commit()
                session.refresh(nota)
                nota.calcola_totali()
                session.commit()
                
                return nota
                
        except Exception as e:
            raise ValueError(f"Errore nell'aggiornamento della nota di credito: {e}")
    
    def elimina_nota_credito(self, nota_id: int) -> bool:
        """Elimina una nota di credito."""
        return self.note_credito_controller.delete(nota_id)
    
    def ottieni_nota_credito(self, nota_id: int) -> Optional[NotaCredito]:
        """Recupera una nota di credito per ID."""
        return self.note_credito_controller.get_by_id(nota_id)
    
    def ottieni_tutte_note_credito(self) -> List[NotaCredito]:
        """Recupera tutte le note di credito."""
        return self.note_credito_controller.get_all(active_only=False)
    
    # === PRIMA NOTA ===
    
    def crea_registrazione_prima_nota(self, dati: Dict[str, Any]) -> Optional[PrimaNota]:
        """
        Crea una nuova registrazione di prima nota.
        
        Args:
            dati: Dati della registrazione
            
        Returns:
            La registrazione creata o None se errore
        """
        # Valida i dati
        errori = self.valida_dati_prima_nota(dati)
        if errori:
            raise ValueError(f"Errori di validazione: {errori}")
        
        # Genera numero registrazione se non presente
        if not dati.get('numero_registrazione'):
            dati['numero_registrazione'] = self._genera_numero_prima_nota()
        
        return self.prima_nota_controller.create(**dati)
    
    def aggiorna_registrazione_prima_nota(self, registrazione_id: int, dati: Dict[str, Any]) -> Optional[PrimaNota]:
        """
        Aggiorna una registrazione di prima nota.
        
        Args:
            registrazione_id: ID della registrazione
            dati: Dati da aggiornare
            
        Returns:
            La registrazione aggiornata o None se errore
        """
        errori = self.valida_dati_prima_nota(dati, is_update=True)
        if errori:
            raise ValueError(f"Errori di validazione: {errori}")
        
        return self.prima_nota_controller.update(registrazione_id, **dati)
    
    def elimina_registrazione_prima_nota(self, registrazione_id: int) -> bool:
        """Elimina una registrazione di prima nota."""
        return self.prima_nota_controller.delete(registrazione_id)
    
    def ottieni_registrazione_prima_nota(self, registrazione_id: int) -> Optional[PrimaNota]:
        """Recupera una registrazione di prima nota per ID."""
        return self.prima_nota_controller.get_by_id(registrazione_id)
    
    def ottieni_tutte_registrazioni_prima_nota(self) -> List[PrimaNota]:
        """Recupera tutte le registrazioni di prima nota."""
        return self.prima_nota_controller.get_all(active_only=False)
    
    # === VALIDAZIONE ===
    
    def valida_dati_fattura(self, dati: Dict[str, Any], is_update: bool = False) -> Dict[str, str]:
        """
        Valida i dati di una fattura.
        
        Args:
            dati: Dati da validare
            is_update: Se True, è un aggiornamento
            
        Returns:
            Dizionario con eventuali errori
        """
        errori = {}
        
        # Campi obbligatori
        if not is_update:
            campi_obbligatori = ['tipo_documento']
            for campo in campi_obbligatori:
                if campo not in dati:
                    errori[campo] = f"Il campo {campo} è obbligatorio"
        
        # Validazione tipo documento
        if 'tipo_documento' in dati:
            if dati['tipo_documento'] not in [tipo.value for tipo in TipoDocumento]:
                errori['tipo_documento'] = "Tipo documento non valido"
        
        # Validazione cliente/fornitore
        if 'tipo_documento' in dati:
            if dati['tipo_documento'] == TipoDocumento.FATTURA_VENDITA.value and not dati.get('cliente_id'):
                errori['cliente_id'] = "Cliente obbligatorio per fattura di vendita"
            elif dati['tipo_documento'] == TipoDocumento.FATTURA_ACQUISTO.value and not dati.get('fornitore_id'):
                errori['fornitore_id'] = "Fornitore obbligatorio per fattura di acquisto"
        
        # Validazione importi
        if 'imponibile' in dati and dati['imponibile'] < 0:
            errori['imponibile'] = "L'imponibile non può essere negativo"
        
        if 'iva' in dati and dati['iva'] < 0:
            errori['iva'] = "L'IVA non può essere negativa"
        
        if 'totale' in dati and dati['totale'] < 0:
            errori['totale'] = "Il totale non può essere negativo"
        
        return errori
    
    def valida_dati_nota_credito(self, dati: Dict[str, Any], is_update: bool = False) -> Dict[str, str]:
        """
        Valida i dati di una nota di credito.
        
        Args:
            dati: Dati da validare
            is_update: Se True, è un aggiornamento
            
        Returns:
            Dizionario con eventuali errori
        """
        errori = {}
        
        # Campi obbligatori
        if not is_update:
            if not dati.get('motivo'):
                errori['motivo'] = "Il motivo è obbligatorio"
        
        # Validazione importi
        if 'imponibile' in dati and dati['imponibile'] < 0:
            errori['imponibile'] = "L'imponibile non può essere negativo"
        
        if 'iva' in dati and dati['iva'] < 0:
            errori['iva'] = "L'IVA non può essere negativa"
        
        if 'totale' in dati and dati['totale'] < 0:
            errori['totale'] = "Il totale non può essere negativo"
        
        return errori
    
    def valida_dati_prima_nota(self, dati: Dict[str, Any], is_update: bool = False) -> Dict[str, str]:
        """
        Valida i dati di una registrazione di prima nota.
        
        Args:
            dati: Dati da validare
            is_update: Se True, è un aggiornamento
            
        Returns:
            Dizionario con eventuali errori
        """
        errori = {}
        
        # Campi obbligatori
        if not is_update:
            campi_obbligatori = ['causale', 'dare', 'avere']
            for campo in campi_obbligatori:
                if campo not in dati:
                    errori[campo] = f"Il campo {campo} è obbligatorio"
        
        # Validazione quadratura
        if 'dare' in dati and 'avere' in dati:
            if abs(float(dati['dare']) - float(dati['avere'])) > 0.01:
                errori['quadratura'] = "La registrazione deve essere quadrata (dare = avere)"
        
        # Validazione importi
        if 'dare' in dati and dati['dare'] < 0:
            errori['dare'] = "L'importo dare non può essere negativo"
        
        if 'avere' in dati and dati['avere'] < 0:
            errori['avere'] = "L'importo avere non può essere negativo"
        
        return errori
    
    # === METODI PRIVATI ===
    
    def _genera_numero_fattura(self, tipo_documento: TipoDocumento) -> str:
        """Genera un numero fattura univoco."""
        anno = datetime.now().year
        
        # Conta fatture dell'anno corrente per tipo
        try:
            with self.db_manager.get_session_context() as session:
                count = session.query(Fattura).filter(
                    Fattura.tipo_documento == tipo_documento,
                    Fattura.created_at >= datetime(anno, 1, 1)
                ).count()
        except Exception:
            count = 0
        
        prefisso = "FV" if tipo_documento == TipoDocumento.FATTURA_VENDITA else "FA"
        return f"{prefisso}{anno}{count + 1:04d}"
    
    def _genera_numero_nota_credito(self) -> str:
        """Genera un numero nota di credito univoco."""
        anno = datetime.now().year
        
        try:
            with self.db_manager.get_session_context() as session:
                count = session.query(NotaCredito).filter(
                    NotaCredito.created_at >= datetime(anno, 1, 1)
                ).count()
        except Exception:
            count = 0
        
        return f"NC{anno}{count + 1:04d}"
    
    def _genera_numero_prima_nota(self) -> str:
        """Genera un numero registrazione prima nota univoco."""
        anno = datetime.now().year
        
        try:
            with self.db_manager.get_session_context() as session:
                count = session.query(PrimaNota).filter(
                    PrimaNota.created_at >= datetime(anno, 1, 1)
                ).count()
        except Exception:
            count = 0
        
        return f"PN{anno}{count + 1:04d}"
    
    def _calcola_data_scadenza(self, data_fattura: datetime, giorni_scadenza: int = 30) -> datetime:
        """Calcola la data di scadenza di una fattura."""
        return data_fattura + timedelta(days=giorni_scadenza)
    
    # === REPORT ===
    
    def ottieni_statistiche_fatture(self) -> Dict[str, Any]:
        """Ottiene statistiche sulle fatture."""
        try:
            with self.db_manager.get_session_context() as session:
                # Fatture totali
                totale_fatture = session.query(Fattura).count()
                
                # Fatture per stato
                fatture_per_stato = {}
                for stato in StatoDocumento:
                    count = session.query(Fattura).filter(Fattura.stato == stato).count()
                    fatture_per_stato[stato.value] = count
                
                # Fatture scadute
                fatture_scadute = session.query(Fattura).filter(
                    Fattura.data_scadenza < datetime.now(),
                    Fattura.pagata == False
                ).count()
                
                # Totale fatturato
                totale_fatturato = session.query(Fattura).filter(
                    Fattura.tipo_documento == TipoDocumento.FATTURA_VENDITA
                ).with_entities(Fattura.totale).all()
                
                fatturato = sum(f.totale for f in totale_fatturato if f.totale)
                
                return {
                    'totale_fatture': totale_fatture,
                    'fatture_per_stato': fatture_per_stato,
                    'fatture_scadute': fatture_scadute,
                    'fatturato_totale': float(fatturato) if fatturato else 0.0
                }
                
        except Exception:
            return {
                'totale_fatture': 0,
                'fatture_per_stato': {},
                'fatture_scadute': 0,
                'fatturato_totale': 0.0
            }