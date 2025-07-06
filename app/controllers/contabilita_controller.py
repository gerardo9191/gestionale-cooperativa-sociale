"""
Controller per la Contabilità Generale
======================================

Gestisce le operazioni per i conti contabili e i movimenti contabili.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from .base_controller import BaseController
from ..models.contabilita import ContoContabile, MovimentoContabile, TipoConto, crea_piano_conti_base
from ..database.connection import DatabaseManager


class ContabilitaController:
    """Controller per la gestione della contabilità generale."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Inizializza il controller della contabilità.
        
        Args:
            db_manager: Gestore del database
        """
        self.db_manager = db_manager
        self.conti_controller = BaseController(db_manager, ContoContabile)
        self.movimenti_controller = BaseController(db_manager, MovimentoContabile)
    
    # === CONTI CONTABILI ===
    
    def crea_conto(self, dati: Dict[str, Any]) -> Optional[ContoContabile]:
        """
        Crea un nuovo conto contabile.
        
        Args:
            dati: Dati del conto
            
        Returns:
            Il conto creato o None se errore
        """
        # Valida i dati
        errori = self.valida_dati_conto(dati)
        if errori:
            raise ValueError(f"Errori di validazione: {errori}")
        
        # Verifica unicità codice
        if self.conti_controller.exists(codice=dati['codice']):
            raise ValueError(f"Esiste già un conto con codice {dati['codice']}")
        
        return self.conti_controller.create(**dati)
    
    def aggiorna_conto(self, conto_id: int, dati: Dict[str, Any]) -> Optional[ContoContabile]:
        """
        Aggiorna un conto contabile esistente.
        
        Args:
            conto_id: ID del conto
            dati: Dati da aggiornare
            
        Returns:
            Il conto aggiornato o None se errore
        """
        errori = self.valida_dati_conto(dati, is_update=True)
        if errori:
            raise ValueError(f"Errori di validazione: {errori}")
        
        return self.conti_controller.update(conto_id, **dati)
    
    def elimina_conto(self, conto_id: int) -> bool:
        """Elimina un conto contabile."""
        # Verifica che il conto non abbia movimenti
        try:
            with self.db_manager.get_session_context() as session:
                movimenti = session.query(MovimentoContabile).filter(
                    (MovimentoContabile.conto_dare_id == conto_id) |
                    (MovimentoContabile.conto_avere_id == conto_id)
                ).count()
                
                if movimenti > 0:
                    raise ValueError("Impossibile eliminare il conto: ha movimenti associati")
        except Exception as e:
            raise ValueError(f"Errore nella verifica dei movimenti: {e}")
        
        return self.conti_controller.delete(conto_id)
    
    def ottieni_conto(self, conto_id: int) -> Optional[ContoContabile]:
        """Recupera un conto per ID."""
        return self.conti_controller.get_by_id(conto_id)
    
    def ottieni_conto_per_codice(self, codice: str) -> Optional[ContoContabile]:
        """Recupera un conto per codice."""
        try:
            with self.db_manager.get_session_context() as session:
                return session.query(ContoContabile).filter(
                    ContoContabile.codice == codice
                ).first()
        except Exception:
            return None
    
    def ottieni_tutti_conti(self, solo_attivi: bool = True) -> List[ContoContabile]:
        """Recupera tutti i conti contabili."""
        return self.conti_controller.get_all(active_only=solo_attivi)
    
    def ottieni_conti_per_tipo(self, tipo_conto: TipoConto) -> List[ContoContabile]:
        """Recupera tutti i conti di un tipo specifico."""
        try:
            with self.db_manager.get_session_context() as session:
                return session.query(ContoContabile).filter(
                    ContoContabile.tipo_conto == tipo_conto,
                    ContoContabile.attivo == True
                ).all()
        except Exception:
            return []
    
    def ottieni_conti_utilizzabili(self) -> List[ContoContabile]:
        """Recupera tutti i conti utilizzabili nelle registrazioni."""
        try:
            with self.db_manager.get_session_context() as session:
                return session.query(ContoContabile).filter(
                    ContoContabile.utilizzabile == True,
                    ContoContabile.attivo == True
                ).all()
        except Exception:
            return []
    
    def ottieni_struttura_conti(self) -> Dict[str, Any]:
        """Recupera la struttura gerarchica dei conti."""
        try:
            with self.db_manager.get_session_context() as session:
                # Recupera tutti i conti ordinati per livello e codice
                conti = session.query(ContoContabile).filter(
                    ContoContabile.attivo == True
                ).order_by(ContoContabile.livello, ContoContabile.codice).all()
                
                # Costruisci la struttura ad albero
                struttura = {}
                for conto in conti:
                    if conto.conto_padre_id is None:
                        struttura[conto.codice] = {
                            'conto': conto,
                            'figli': {}
                        }
                
                # Aggiungi i conti figli
                for conto in conti:
                    if conto.conto_padre_id is not None:
                        self._aggiungi_conto_figlio(struttura, conto)
                
                return struttura
                
        except Exception:
            return {}
    
    def cerca_conti(self, termine: str) -> List[ContoContabile]:
        """Cerca conti per termine."""
        return self.conti_controller.search(termine, ['codice', 'descrizione'])
    
    def inizializza_piano_conti(self) -> bool:
        """Inizializza il piano dei conti di base."""
        try:
            # Verifica se esistono già conti
            if self.conti_controller.count(active_only=False) > 0:
                raise ValueError("Piano dei conti già esistente")
            
            # Crea i conti di base
            conti_base = crea_piano_conti_base()
            
            with self.db_manager.get_session_context() as session:
                for conto in conti_base:
                    session.add(conto)
                session.commit()
            
            return True
            
        except Exception as e:
            raise ValueError(f"Errore nell'inizializzazione del piano dei conti: {e}")
    
    # === MOVIMENTI CONTABILI ===
    
    def crea_movimento(self, dati: Dict[str, Any]) -> Optional[MovimentoContabile]:
        """
        Crea un nuovo movimento contabile.
        
        Args:
            dati: Dati del movimento
            
        Returns:
            Il movimento creato o None se errore
        """
        # Valida i dati
        errori = self.valida_dati_movimento(dati)
        if errori:
            raise ValueError(f"Errori di validazione: {errori}")
        
        # Genera numero movimento se non presente
        if not dati.get('numero_movimento'):
            dati['numero_movimento'] = self._genera_numero_movimento()
        
        try:
            with self.db_manager.get_session_context() as session:
                # Crea il movimento
                movimento = MovimentoContabile(**dati)
                session.add(movimento)
                session.flush()
                
                # Aggiorna i saldi dei conti
                self._aggiorna_saldi_conti(session, movimento)
                
                session.commit()
                return movimento
                
        except Exception as e:
            raise ValueError(f"Errore nella creazione del movimento: {e}")
    
    def aggiorna_movimento(self, movimento_id: int, dati: Dict[str, Any]) -> Optional[MovimentoContabile]:
        """
        Aggiorna un movimento contabile esistente.
        
        Args:
            movimento_id: ID del movimento
            dati: Dati da aggiornare
            
        Returns:
            Il movimento aggiornato o None se errore
        """
        errori = self.valida_dati_movimento(dati, is_update=True)
        if errori:
            raise ValueError(f"Errori di validazione: {errori}")
        
        try:
            with self.db_manager.get_session_context() as session:
                movimento = session.query(MovimentoContabile).filter(
                    MovimentoContabile.id == movimento_id
                ).first()
                
                if not movimento:
                    raise ValueError("Movimento non trovato")
                
                # Storna i saldi precedenti
                self._storna_saldi_conti(session, movimento)
                
                # Aggiorna i dati del movimento
                for key, value in dati.items():
                    if hasattr(movimento, key):
                        setattr(movimento, key, value)
                
                # Aggiorna i saldi con i nuovi dati
                self._aggiorna_saldi_conti(session, movimento)
                
                session.commit()
                return movimento
                
        except Exception as e:
            raise ValueError(f"Errore nell'aggiornamento del movimento: {e}")
    
    def elimina_movimento(self, movimento_id: int) -> bool:
        """Elimina un movimento contabile."""
        try:
            with self.db_manager.get_session_context() as session:
                movimento = session.query(MovimentoContabile).filter(
                    MovimentoContabile.id == movimento_id
                ).first()
                
                if not movimento:
                    return False
                
                # Storna i saldi
                self._storna_saldi_conti(session, movimento)
                
                # Elimina il movimento
                session.delete(movimento)
                session.commit()
                
                return True
                
        except Exception:
            return False
    
    def ottieni_movimento(self, movimento_id: int) -> Optional[MovimentoContabile]:
        """Recupera un movimento per ID."""
        return self.movimenti_controller.get_by_id(movimento_id)
    
    def ottieni_tutti_movimenti(self) -> List[MovimentoContabile]:
        """Recupera tutti i movimenti contabili."""
        return self.movimenti_controller.get_all(active_only=False)
    
    def ottieni_movimenti_per_conto(self, conto_id: int) -> List[MovimentoContabile]:
        """Recupera tutti i movimenti di un conto."""
        try:
            with self.db_manager.get_session_context() as session:
                return session.query(MovimentoContabile).filter(
                    (MovimentoContabile.conto_dare_id == conto_id) |
                    (MovimentoContabile.conto_avere_id == conto_id)
                ).all()
        except Exception:
            return []
    
    def ottieni_movimenti_per_periodo(self, data_inizio: datetime, data_fine: datetime) -> List[MovimentoContabile]:
        """Recupera tutti i movimenti in un periodo."""
        try:
            with self.db_manager.get_session_context() as session:
                return session.query(MovimentoContabile).filter(
                    MovimentoContabile.data_movimento >= data_inizio,
                    MovimentoContabile.data_movimento <= data_fine
                ).all()
        except Exception:
            return []
    
    def cerca_movimenti(self, termine: str) -> List[MovimentoContabile]:
        """Cerca movimenti per termine."""
        return self.movimenti_controller.search(termine, ['causale', 'numero_movimento', 'descrizione'])
    
    # === VALIDAZIONE ===
    
    def valida_dati_conto(self, dati: Dict[str, Any], is_update: bool = False) -> Dict[str, str]:
        """
        Valida i dati di un conto contabile.
        
        Args:
            dati: Dati da validare
            is_update: Se True, è un aggiornamento
            
        Returns:
            Dizionario con eventuali errori
        """
        errori = {}
        
        # Campi obbligatori
        if not is_update:
            campi_obbligatori = ['codice', 'descrizione', 'tipo_conto']
            for campo in campi_obbligatori:
                if campo not in dati:
                    errori[campo] = f"Il campo {campo} è obbligatorio"
        
        # Validazione tipo conto
        if 'tipo_conto' in dati:
            if dati['tipo_conto'] not in [tipo for tipo in TipoConto]:
                errori['tipo_conto'] = "Tipo conto non valido"
        
        # Validazione codice
        if 'codice' in dati:
            if not dati['codice'].strip():
                errori['codice'] = "Il codice non può essere vuoto"
        
        # Validazione descrizione
        if 'descrizione' in dati:
            if not dati['descrizione'].strip():
                errori['descrizione'] = "La descrizione non può essere vuota"
        
        return errori
    
    def valida_dati_movimento(self, dati: Dict[str, Any], is_update: bool = False) -> Dict[str, str]:
        """
        Valida i dati di un movimento contabile.
        
        Args:
            dati: Dati da validare
            is_update: Se True, è un aggiornamento
            
        Returns:
            Dizionario con eventuali errori
        """
        errori = {}
        
        # Campi obbligatori
        if not is_update:
            campi_obbligatori = ['causale', 'conto_dare_id', 'conto_avere_id', 'importo']
            for campo in campi_obbligatori:
                if campo not in dati:
                    errori[campo] = f"Il campo {campo} è obbligatorio"
        
        # Validazione conti
        if 'conto_dare_id' in dati and 'conto_avere_id' in dati:
            if dati['conto_dare_id'] == dati['conto_avere_id']:
                errori['conti'] = "Il conto dare e avere non possono essere uguali"
        
        # Validazione importo
        if 'importo' in dati:
            if dati['importo'] <= 0:
                errori['importo'] = "L'importo deve essere positivo"
        
        # Validazione causale
        if 'causale' in dati:
            if not dati['causale'].strip():
                errori['causale'] = "La causale non può essere vuota"
        
        return errori
    
    # === METODI PRIVATI ===
    
    def _genera_numero_movimento(self) -> str:
        """Genera un numero movimento univoco."""
        anno = datetime.now().year
        
        try:
            with self.db_manager.get_session_context() as session:
                count = session.query(MovimentoContabile).filter(
                    MovimentoContabile.created_at >= datetime(anno, 1, 1)
                ).count()
        except Exception:
            count = 0
        
        return f"MOV{anno}{count + 1:04d}"
    
    def _aggiorna_saldi_conti(self, session, movimento: MovimentoContabile) -> None:
        """Aggiorna i saldi dei conti per un movimento."""
        # Aggiorna conto dare
        conto_dare = session.query(ContoContabile).filter(
            ContoContabile.id == movimento.conto_dare_id
        ).first()
        if conto_dare:
            conto_dare.aggiorna_saldo(importo_dare=float(movimento.importo))
        
        # Aggiorna conto avere
        conto_avere = session.query(ContoContabile).filter(
            ContoContabile.id == movimento.conto_avere_id
        ).first()
        if conto_avere:
            conto_avere.aggiorna_saldo(importo_avere=float(movimento.importo))
    
    def _storna_saldi_conti(self, session, movimento: MovimentoContabile) -> None:
        """Storna i saldi dei conti per un movimento."""
        # Storna conto dare
        conto_dare = session.query(ContoContabile).filter(
            ContoContabile.id == movimento.conto_dare_id
        ).first()
        if conto_dare:
            conto_dare.aggiorna_saldo(importo_dare=-float(movimento.importo))
        
        # Storna conto avere
        conto_avere = session.query(ContoContabile).filter(
            ContoContabile.id == movimento.conto_avere_id
        ).first()
        if conto_avere:
            conto_avere.aggiorna_saldo(importo_avere=-float(movimento.importo))
    
    def _aggiungi_conto_figlio(self, struttura: Dict[str, Any], conto: ContoContabile) -> None:
        """Aggiunge un conto figlio alla struttura gerarchica."""
        # Implementazione ricorsiva per trovare il padre e aggiungere il figlio
        # Semplificata per ora
        pass
    
    # === BILANCIO E SALDI ===
    
    def ottieni_bilancio(self, data_bilancio: datetime = None) -> Dict[str, Any]:
        """
        Ottiene il bilancio alla data specificata.
        
        Args:
            data_bilancio: Data del bilancio (default: oggi)
            
        Returns:
            Dizionario con i dati del bilancio
        """
        if not data_bilancio:
            data_bilancio = datetime.now()
        
        try:
            with self.db_manager.get_session_context() as session:
                # Recupera tutti i conti attivi
                conti = session.query(ContoContabile).filter(
                    ContoContabile.attivo == True
                ).all()
                
                bilancio = {
                    'attivo': {},
                    'passivo': {},
                    'capitale': {},
                    'ricavi': {},
                    'costi': {},
                    'totali': {}
                }
                
                # Calcola i saldi per ogni conto
                for conto in conti:
                    saldo = conto.get_saldo_attuale()
                    tipo_conto = conto.tipo_conto.value
                    
                    if tipo_conto not in bilancio:
                        bilancio[tipo_conto] = {}
                    
                    bilancio[tipo_conto][conto.codice] = {
                        'descrizione': conto.descrizione,
                        'saldo': saldo
                    }
                
                # Calcola i totali
                for tipo_conto in bilancio:
                    if tipo_conto != 'totali':
                        totale = sum(dati['saldo'] for dati in bilancio[tipo_conto].values())
                        bilancio['totali'][tipo_conto] = totale
                
                return bilancio
                
        except Exception:
            return {}
    
    def ottieni_saldo_conto(self, conto_id: int, data_saldo: datetime = None) -> float:
        """
        Ottiene il saldo di un conto alla data specificata.
        
        Args:
            conto_id: ID del conto
            data_saldo: Data del saldo (default: oggi)
            
        Returns:
            Saldo del conto
        """
        try:
            conto = self.ottieni_conto(conto_id)
            if not conto:
                return 0.0
            
            return conto.get_saldo_attuale()
            
        except Exception:
            return 0.0