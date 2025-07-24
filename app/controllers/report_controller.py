"""
Controller per i Report
=======================

Gestisce la generazione di report finanziari e statistiche.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import pandas as pd

from .anagrafiche_controller import AnagraficheController
from .documenti_controller import DocumentiController
from .contabilita_controller import ContabilitaController
from ..models.contabilita import TipoConto
from ..models.documenti import TipoDocumento, StatoDocumento
from ..database.connection import DatabaseManager


class ReportController:
    """Controller per la generazione di report finanziari."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Inizializza il controller dei report.
        
        Args:
            db_manager: Gestore del database
        """
        self.db_manager = db_manager
        self.anagrafiche_controller = AnagraficheController(db_manager)
        self.documenti_controller = DocumentiController(db_manager)
        self.contabilita_controller = ContabilitaController(db_manager)
    
    # === BILANCIO ===
    
    def genera_bilancio(self, data_bilancio: datetime = None) -> Dict[str, Any]:
        """
        Genera il bilancio alla data specificata.
        
        Args:
            data_bilancio: Data del bilancio (default: oggi)
            
        Returns:
            Dizionario con i dati del bilancio
        """
        if not data_bilancio:
            data_bilancio = datetime.now()
        
        # Ottieni i dati dalla contabilità
        bilancio = self.contabilita_controller.ottieni_bilancio(data_bilancio)
        
        # Aggiungi metadati
        bilancio['metadati'] = {
            'data_bilancio': data_bilancio.isoformat(),
            'data_generazione': datetime.now().isoformat(),
            'tipo_report': 'bilancio'
        }
        
        return bilancio
    
    def genera_stato_patrimoniale(self, data_bilancio: datetime = None) -> Dict[str, Any]:
        """
        Genera lo stato patrimoniale alla data specificata.
        
        Args:
            data_bilancio: Data del bilancio (default: oggi)
            
        Returns:
            Dizionario con i dati dello stato patrimoniale
        """
        bilancio = self.genera_bilancio(data_bilancio)
        
        # Estrai solo attivo, passivo e capitale
        stato_patrimoniale = {
            'attivo': bilancio.get('attivo', {}),
            'passivo': bilancio.get('passivo', {}),
            'capitale': bilancio.get('capitale', {}),
            'totali': {
                'attivo': bilancio.get('totali', {}).get('attivo', 0),
                'passivo': bilancio.get('totali', {}).get('passivo', 0),
                'capitale': bilancio.get('totali', {}).get('capitale', 0)
            },
            'metadati': bilancio.get('metadati', {})
        }
        
        # Calcola totale passivo + capitale
        stato_patrimoniale['totali']['passivo_capitale'] = (
            stato_patrimoniale['totali']['passivo'] + 
            stato_patrimoniale['totali']['capitale']
        )
        
        return stato_patrimoniale
    
    def genera_conto_economico(self, data_inizio: datetime, data_fine: datetime) -> Dict[str, Any]:
        """
        Genera il conto economico per il periodo specificato.
        
        Args:
            data_inizio: Data di inizio del periodo
            data_fine: Data di fine del periodo
            
        Returns:
            Dizionario con i dati del conto economico
        """
        # Ottieni i conti ricavi e costi
        conti_ricavi = self.contabilita_controller.ottieni_conti_per_tipo(TipoConto.RICAVO)
        conti_costi = self.contabilita_controller.ottieni_conti_per_tipo(TipoConto.COSTO)
        
        conto_economico = {
            'ricavi': {},
            'costi': {},
            'totali': {},
            'metadati': {
                'data_inizio': data_inizio.isoformat(),
                'data_fine': data_fine.isoformat(),
                'data_generazione': datetime.now().isoformat(),
                'tipo_report': 'conto_economico'
            }
        }
        
        # Calcola ricavi
        totale_ricavi = 0
        for conto in conti_ricavi:
            saldo = conto.get_saldo_attuale()
            conto_economico['ricavi'][conto.codice] = {
                'descrizione': conto.descrizione,
                'saldo': saldo
            }
            totale_ricavi += saldo
        
        # Calcola costi
        totale_costi = 0
        for conto in conti_costi:
            saldo = conto.get_saldo_attuale()
            conto_economico['costi'][conto.codice] = {
                'descrizione': conto.descrizione,
                'saldo': saldo
            }
            totale_costi += saldo
        
        # Calcola totali
        conto_economico['totali'] = {
            'ricavi': totale_ricavi,
            'costi': totale_costi,
            'utile_perdita': totale_ricavi - totale_costi
        }
        
        return conto_economico
    
    # === REPORT FATTURE ===
    
    def genera_report_fatture(self, data_inizio: datetime = None, data_fine: datetime = None) -> Dict[str, Any]:
        """
        Genera un report delle fatture per il periodo specificato.
        
        Args:
            data_inizio: Data di inizio del periodo
            data_fine: Data di fine del periodo
            
        Returns:
            Dizionario con i dati del report fatture
        """
        if not data_inizio:
            data_inizio = datetime.now().replace(day=1)  # Primo giorno del mese
        if not data_fine:
            data_fine = datetime.now()
        
        # Ottieni tutte le fatture
        fatture = self.documenti_controller.ottieni_tutte_fatture()
        
        # Filtra per periodo
        fatture_periodo = [
            f for f in fatture 
            if data_inizio <= f.data_fattura <= data_fine
        ]
        
        # Statistiche per tipo documento
        stats_per_tipo = {}
        for tipo in TipoDocumento:
            fatture_tipo = [f for f in fatture_periodo if f.tipo_documento == tipo]
            stats_per_tipo[tipo.value] = {
                'numero_fatture': len(fatture_tipo),
                'totale_imponibile': sum(f.imponibile for f in fatture_tipo),
                'totale_iva': sum(f.iva for f in fatture_tipo),
                'totale_fatturato': sum(f.totale for f in fatture_tipo)
            }
        
        # Statistiche per stato
        stats_per_stato = {}
        for stato in StatoDocumento:
            fatture_stato = [f for f in fatture_periodo if f.stato == stato]
            stats_per_stato[stato.value] = {
                'numero_fatture': len(fatture_stato),
                'totale_fatturato': sum(f.totale for f in fatture_stato)
            }
        
        # Fatture scadute
        fatture_scadute = self.documenti_controller.ottieni_fatture_scadute()
        
        report = {
            'periodo': {
                'data_inizio': data_inizio.isoformat(),
                'data_fine': data_fine.isoformat()
            },
            'statistiche_per_tipo': stats_per_tipo,
            'statistiche_per_stato': stats_per_stato,
            'fatture_scadute': {
                'numero': len(fatture_scadute),
                'totale_scaduto': sum(f.totale for f in fatture_scadute)
            },
            'totali_periodo': {
                'numero_fatture': len(fatture_periodo),
                'totale_imponibile': sum(f.imponibile for f in fatture_periodo),
                'totale_iva': sum(f.iva for f in fatture_periodo),
                'totale_fatturato': sum(f.totale for f in fatture_periodo)
            },
            'metadati': {
                'data_generazione': datetime.now().isoformat(),
                'tipo_report': 'report_fatture'
            }
        }
        
        return report
    
    def genera_estratto_conto_cliente(self, cliente_id: int, data_inizio: datetime = None, data_fine: datetime = None) -> Dict[str, Any]:
        """
        Genera l'estratto conto di un cliente.
        
        Args:
            cliente_id: ID del cliente
            data_inizio: Data di inizio del periodo
            data_fine: Data di fine del periodo
            
        Returns:
            Dizionario con i dati dell'estratto conto
        """
        # Ottieni il cliente
        cliente = self.anagrafiche_controller.ottieni_cliente(cliente_id)
        if not cliente:
            raise ValueError("Cliente non trovato")
        
        # Ottieni le fatture del cliente
        fatture = self.documenti_controller.ottieni_fatture_per_cliente(cliente_id)
        
        # Filtra per periodo se specificato
        if data_inizio and data_fine:
            fatture = [f for f in fatture if data_inizio <= f.data_fattura <= data_fine]
        
        # Ordina per data
        fatture.sort(key=lambda f: f.data_fattura)
        
        # Calcola saldi
        saldo_iniziale = 0.0
        saldo_progressivo = saldo_iniziale
        
        movimenti = []
        for fattura in fatture:
            if fattura.tipo_documento == TipoDocumento.FATTURA_VENDITA:
                importo = float(fattura.totale)
                saldo_progressivo += importo
                tipo_movimento = 'DARE'
            else:
                importo = -float(fattura.totale)
                saldo_progressivo += importo
                tipo_movimento = 'AVERE'
            
            movimenti.append({
                'data': fattura.data_fattura.isoformat(),
                'numero_documento': fattura.numero_fattura,
                'descrizione': fattura.oggetto or 'Fattura',
                'tipo_movimento': tipo_movimento,
                'importo': abs(importo),
                'saldo_progressivo': saldo_progressivo
            })
        
        estratto_conto = {
            'cliente': {
                'id': cliente.id,
                'ragione_sociale': cliente.ragione_sociale,
                'codice_cliente': cliente.codice_cliente,
                'partita_iva': cliente.partita_iva
            },
            'periodo': {
                'data_inizio': data_inizio.isoformat() if data_inizio else None,
                'data_fine': data_fine.isoformat() if data_fine else None
            },
            'saldi': {
                'saldo_iniziale': saldo_iniziale,
                'saldo_finale': saldo_progressivo
            },
            'movimenti': movimenti,
            'statistiche': {
                'numero_fatture': len(fatture),
                'totale_fatturato': sum(f.totale for f in fatture if f.tipo_documento == TipoDocumento.FATTURA_VENDITA),
                'fatture_pagate': len([f for f in fatture if f.pagata]),
                'fatture_scadute': len([f for f in fatture if f.is_scaduta()])
            },
            'metadati': {
                'data_generazione': datetime.now().isoformat(),
                'tipo_report': 'estratto_conto_cliente'
            }
        }
        
        return estratto_conto
    
    def genera_estratto_conto_fornitore(self, fornitore_id: int, data_inizio: datetime = None, data_fine: datetime = None) -> Dict[str, Any]:
        """
        Genera l'estratto conto di un fornitore.
        
        Args:
            fornitore_id: ID del fornitore
            data_inizio: Data di inizio del periodo
            data_fine: Data di fine del periodo
            
        Returns:
            Dizionario con i dati dell'estratto conto
        """
        # Ottieni il fornitore
        fornitore = self.anagrafiche_controller.ottieni_fornitore(fornitore_id)
        if not fornitore:
            raise ValueError("Fornitore non trovato")
        
        # Ottieni le fatture del fornitore
        fatture = self.documenti_controller.ottieni_fatture_per_fornitore(fornitore_id)
        
        # Filtra per periodo se specificato
        if data_inizio and data_fine:
            fatture = [f for f in fatture if data_inizio <= f.data_fattura <= data_fine]
        
        # Ordina per data
        fatture.sort(key=lambda f: f.data_fattura)
        
        # Calcola saldi
        saldo_iniziale = 0.0
        saldo_progressivo = saldo_iniziale
        
        movimenti = []
        for fattura in fatture:
            if fattura.tipo_documento == TipoDocumento.FATTURA_ACQUISTO:
                importo = float(fattura.totale)
                saldo_progressivo += importo
                tipo_movimento = 'AVERE'
            else:
                importo = -float(fattura.totale)
                saldo_progressivo += importo
                tipo_movimento = 'DARE'
            
            movimenti.append({
                'data': fattura.data_fattura.isoformat(),
                'numero_documento': fattura.numero_fattura,
                'descrizione': fattura.oggetto or 'Fattura',
                'tipo_movimento': tipo_movimento,
                'importo': abs(importo),
                'saldo_progressivo': saldo_progressivo
            })
        
        estratto_conto = {
            'fornitore': {
                'id': fornitore.id,
                'ragione_sociale': fornitore.ragione_sociale,
                'codice_fornitore': fornitore.codice_fornitore,
                'partita_iva': fornitore.partita_iva
            },
            'periodo': {
                'data_inizio': data_inizio.isoformat() if data_inizio else None,
                'data_fine': data_fine.isoformat() if data_fine else None
            },
            'saldi': {
                'saldo_iniziale': saldo_iniziale,
                'saldo_finale': saldo_progressivo
            },
            'movimenti': movimenti,
            'statistiche': {
                'numero_fatture': len(fatture),
                'totale_fatturato': sum(f.totale for f in fatture if f.tipo_documento == TipoDocumento.FATTURA_ACQUISTO),
                'fatture_pagate': len([f for f in fatture if f.pagata]),
                'fatture_scadute': len([f for f in fatture if f.is_scaduta()])
            },
            'metadati': {
                'data_generazione': datetime.now().isoformat(),
                'tipo_report': 'estratto_conto_fornitore'
            }
        }
        
        return estratto_conto
    
    # === DASHBOARD E STATISTICHE ===
    
    def genera_dashboard_data(self) -> Dict[str, Any]:
        """
        Genera i dati per la dashboard principale.
        
        Returns:
            Dizionario con i dati per la dashboard
        """
        # Statistiche anagrafiche
        stats_anagrafiche = self.anagrafiche_controller.ottieni_statistiche()
        
        # Statistiche fatture
        stats_fatture = self.documenti_controller.ottieni_statistiche_fatture()
        
        # Fatture scadute
        fatture_scadute = self.documenti_controller.ottieni_fatture_scadute()
        
        # Fatturato mensile (ultimi 12 mesi)
        fatturato_mensile = self._calcola_fatturato_mensile()
        
        # Top clienti
        top_clienti = self._calcola_top_clienti()
        
        # Costi mensili
        costi_mensili = self._calcola_costi_mensili()
        
        dashboard = {
            'anagrafiche': stats_anagrafiche,
            'fatture': stats_fatture,
            'fatture_scadute': {
                'numero': len(fatture_scadute),
                'totale': sum(f.totale for f in fatture_scadute)
            },
            'fatturato_mensile': fatturato_mensile,
            'costi_mensili': costi_mensili,
            'top_clienti': top_clienti,
            'metadati': {
                'data_generazione': datetime.now().isoformat(),
                'tipo_report': 'dashboard'
            }
        }
        
        return dashboard
    
    def genera_dati_grafici(self) -> Dict[str, Any]:
        """
        Genera i dati per i grafici della dashboard.
        
        Returns:
            Dizionario con i dati per i grafici
        """
        # Fatturato vs Costi (ultimi 12 mesi)
        fatturato_vs_costi = self._calcola_fatturato_vs_costi()
        
        # Fatture per stato (grafico a torta)
        fatture_per_stato = self.documenti_controller.ottieni_statistiche_fatture()['fatture_per_stato']
        
        # Evoluzione fatturato (grafico lineare)
        evoluzione_fatturato = self._calcola_evoluzione_fatturato()
        
        # Distribuzione clienti per fatturato
        distribuzione_clienti = self._calcola_distribuzione_clienti()
        
        grafici = {
            'fatturato_vs_costi': fatturato_vs_costi,
            'fatture_per_stato': fatture_per_stato,
            'evoluzione_fatturato': evoluzione_fatturato,
            'distribuzione_clienti': distribuzione_clienti,
            'metadati': {
                'data_generazione': datetime.now().isoformat(),
                'tipo_report': 'dati_grafici'
            }
        }
        
        return grafici
    
    # === METODI PRIVATI ===
    
    def _calcola_fatturato_mensile(self, mesi: int = 12) -> List[Dict[str, Any]]:
        """Calcola il fatturato mensile degli ultimi N mesi."""
        fatturato_mensile = []
        
        for i in range(mesi):
            data_fine = datetime.now().replace(day=1) - timedelta(days=1)
            data_inizio = data_fine.replace(day=1)
            
            # Ottieni fatture del mese
            fatture = self.documenti_controller.ottieni_tutte_fatture()
            fatture_mese = [
                f for f in fatture 
                if (data_inizio <= f.data_fattura <= data_fine and 
                    f.tipo_documento == TipoDocumento.FATTURA_VENDITA)
            ]
            
            totale = sum(f.totale for f in fatture_mese)
            
            fatturato_mensile.append({
                'mese': data_inizio.strftime('%Y-%m'),
                'fatturato': float(totale),
                'numero_fatture': len(fatture_mese)
            })
            
            # Vai al mese precedente
            data_fine = data_inizio - timedelta(days=1)
        
        return list(reversed(fatturato_mensile))
    
    def _calcola_top_clienti(self, limite: int = 10) -> List[Dict[str, Any]]:
        """Calcola i top clienti per fatturato."""
        clienti = self.anagrafiche_controller.ottieni_tutti_clienti()
        top_clienti = []
        
        for cliente in clienti:
            fatture = self.documenti_controller.ottieni_fatture_per_cliente(cliente.id)
            fatture_vendita = [f for f in fatture if f.tipo_documento == TipoDocumento.FATTURA_VENDITA]
            totale_fatturato = sum(f.totale for f in fatture_vendita)
            
            if totale_fatturato > 0:
                top_clienti.append({
                    'cliente_id': cliente.id,
                    'ragione_sociale': cliente.ragione_sociale,
                    'fatturato_totale': float(totale_fatturato),
                    'numero_fatture': len(fatture_vendita)
                })
        
        # Ordina per fatturato decrescente
        top_clienti.sort(key=lambda c: c['fatturato_totale'], reverse=True)
        
        return top_clienti[:limite]
    
    def _calcola_costi_mensili(self, mesi: int = 12) -> List[Dict[str, Any]]:
        """Calcola i costi mensili degli ultimi N mesi."""
        costi_mensili = []
        
        for i in range(mesi):
            data_fine = datetime.now().replace(day=1) - timedelta(days=1)
            data_inizio = data_fine.replace(day=1)
            
            # Ottieni fatture di acquisto del mese
            fatture = self.documenti_controller.ottieni_tutte_fatture()
            fatture_mese = [
                f for f in fatture 
                if (data_inizio <= f.data_fattura <= data_fine and 
                    f.tipo_documento == TipoDocumento.FATTURA_ACQUISTO)
            ]
            
            totale = sum(f.totale for f in fatture_mese)
            
            costi_mensili.append({
                'mese': data_inizio.strftime('%Y-%m'),
                'costi': float(totale),
                'numero_fatture': len(fatture_mese)
            })
            
            # Vai al mese precedente
            data_fine = data_inizio - timedelta(days=1)
        
        return list(reversed(costi_mensili))
    
    def _calcola_fatturato_vs_costi(self) -> Dict[str, List[Dict[str, Any]]]:
        """Calcola fatturato vs costi per confronto."""
        fatturato = self._calcola_fatturato_mensile()
        costi = self._calcola_costi_mensili()
        
        return {
            'fatturato': fatturato,
            'costi': costi
        }
    
    def _calcola_evoluzione_fatturato(self) -> List[Dict[str, Any]]:
        """Calcola l'evoluzione del fatturato nel tempo."""
        return self._calcola_fatturato_mensile(24)  # Ultimi 24 mesi
    
    def _calcola_distribuzione_clienti(self) -> List[Dict[str, Any]]:
        """Calcola la distribuzione dei clienti per fasce di fatturato."""
        top_clienti = self._calcola_top_clienti(100)  # Tutti i clienti
        
        # Definisci le fasce
        fasce = [
            {'nome': '0-1000', 'min': 0, 'max': 1000},
            {'nome': '1000-5000', 'min': 1000, 'max': 5000},
            {'nome': '5000-10000', 'min': 5000, 'max': 10000},
            {'nome': '10000-50000', 'min': 10000, 'max': 50000},
            {'nome': '50000+', 'min': 50000, 'max': float('inf')}
        ]
        
        distribuzione = []
        for fascia in fasce:
            clienti_fascia = [
                c for c in top_clienti 
                if fascia['min'] <= c['fatturato_totale'] < fascia['max']
            ]
            
            distribuzione.append({
                'fascia': fascia['nome'],
                'numero_clienti': len(clienti_fascia),
                'fatturato_totale': sum(c['fatturato_totale'] for c in clienti_fascia)
            })
        
        return distribuzione
    
    # === EXPORT ===
    
    def esporta_report_excel(self, report_data: Dict[str, Any], nome_file: str) -> str:
        """
        Esporta un report in formato Excel.
        
        Args:
            report_data: Dati del report
            nome_file: Nome del file di output
            
        Returns:
            Percorso del file creato
        """
        # Implementazione semplificata - da espandere con openpyxl
        df = pd.DataFrame(report_data)
        percorso_file = f"data/reports/{nome_file}.xlsx"
        df.to_excel(percorso_file, index=False)
        return percorso_file
    
    def esporta_report_csv(self, report_data: Dict[str, Any], nome_file: str) -> str:
        """
        Esporta un report in formato CSV.
        
        Args:
            report_data: Dati del report
            nome_file: Nome del file di output
            
        Returns:
            Percorso del file creato
        """
        df = pd.DataFrame(report_data)
        percorso_file = f"data/reports/{nome_file}.csv"
        df.to_csv(percorso_file, index=False)
        return percorso_file