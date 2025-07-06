"""
Anagrafiche Widget
==================

Widget per la gestione delle anagrafiche (fornitori, clienti, dipendenti).
"""

from typing import Dict, Any, List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QTabWidget, QTableWidget, QTableWidgetItem,
    QLineEdit, QComboBox, QTextEdit, QCheckBox, QDateEdit,
    QGroupBox, QDialog, QDialogButtonBox, QMessageBox,
    QHeaderView, QAbstractItemView, QMenu
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QAction, QFont

from ..config import Config
from ..controllers.anagrafiche_controller import AnagraficheController


class AnagraficaDialog(QDialog):
    """Dialog per inserimento/modifica anagrafica."""
    
    def __init__(self, tipo_anagrafica: str, dati: Dict[str, Any] = None, parent=None):
        super().__init__(parent)
        self.tipo_anagrafica = tipo_anagrafica
        self.dati = dati or {}
        
        self.setWindowTitle(f"{'Modifica' if dati else 'Nuova'} {tipo_anagrafica}")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Configura l'interfaccia utente."""
        layout = QVBoxLayout(self)
        
        # Form
        form_group = QGroupBox("Dati Anagrafici")
        form_layout = QGridLayout(form_group)
        
        row = 0
        
        if self.tipo_anagrafica in ["Fornitore", "Cliente"]:
            # Ragione sociale
            form_layout.addWidget(QLabel("Ragione Sociale *:"), row, 0)
            self.ragione_sociale_edit = QLineEdit()
            form_layout.addWidget(self.ragione_sociale_edit, row, 1)
            row += 1
            
            # Partita IVA
            form_layout.addWidget(QLabel("Partita IVA *:"), row, 0)
            self.partita_iva_edit = QLineEdit()
            form_layout.addWidget(self.partita_iva_edit, row, 1)
            row += 1
            
            # Codice Fiscale
            form_layout.addWidget(QLabel("Codice Fiscale:"), row, 0)
            self.codice_fiscale_edit = QLineEdit()
            form_layout.addWidget(self.codice_fiscale_edit, row, 1)
            row += 1
            
        elif self.tipo_anagrafica == "Dipendente":
            # Nome
            form_layout.addWidget(QLabel("Nome *:"), row, 0)
            self.nome_edit = QLineEdit()
            form_layout.addWidget(self.nome_edit, row, 1)
            row += 1
            
            # Cognome
            form_layout.addWidget(QLabel("Cognome *:"), row, 0)
            self.cognome_edit = QLineEdit()
            form_layout.addWidget(self.cognome_edit, row, 1)
            row += 1
            
            # Codice Fiscale
            form_layout.addWidget(QLabel("Codice Fiscale *:"), row, 0)
            self.codice_fiscale_edit = QLineEdit()
            form_layout.addWidget(self.codice_fiscale_edit, row, 1)
            row += 1
            
            # Data nascita
            form_layout.addWidget(QLabel("Data Nascita:"), row, 0)
            self.data_nascita_edit = QDateEdit()
            self.data_nascita_edit.setCalendarPopup(True)
            form_layout.addWidget(self.data_nascita_edit, row, 1)
            row += 1
        
        # Dati comuni
        # Telefono
        form_layout.addWidget(QLabel("Telefono:"), row, 0)
        self.telefono_edit = QLineEdit()
        form_layout.addWidget(self.telefono_edit, row, 1)
        row += 1
        
        # Email
        form_layout.addWidget(QLabel("Email:"), row, 0)
        self.email_edit = QLineEdit()
        form_layout.addWidget(self.email_edit, row, 1)
        row += 1
        
        # Indirizzo
        form_layout.addWidget(QLabel("Indirizzo:"), row, 0)
        self.indirizzo_edit = QLineEdit()
        form_layout.addWidget(self.indirizzo_edit, row, 1)
        row += 1
        
        # CAP
        form_layout.addWidget(QLabel("CAP:"), row, 0)
        self.cap_edit = QLineEdit()
        form_layout.addWidget(self.cap_edit, row, 1)
        row += 1
        
        # Città
        form_layout.addWidget(QLabel("Città:"), row, 0)
        self.citta_edit = QLineEdit()
        form_layout.addWidget(self.citta_edit, row, 1)
        row += 1
        
        # Provincia
        form_layout.addWidget(QLabel("Provincia:"), row, 0)
        self.provincia_edit = QLineEdit()
        form_layout.addWidget(self.provincia_edit, row, 1)
        row += 1
        
        # Note
        form_layout.addWidget(QLabel("Note:"), row, 0)
        self.note_edit = QTextEdit()
        self.note_edit.setMaximumHeight(80)
        form_layout.addWidget(self.note_edit, row, 1)
        row += 1
        
        # Attivo
        self.attivo_check = QCheckBox("Attivo")
        self.attivo_check.setChecked(True)
        form_layout.addWidget(self.attivo_check, row, 0, 1, 2)
        
        layout.addWidget(form_group)
        
        # Pulsanti
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_data(self):
        """Carica i dati nell'interfaccia."""
        if not self.dati:
            return
        
        if self.tipo_anagrafica in ["Fornitore", "Cliente"]:
            self.ragione_sociale_edit.setText(self.dati.get('ragione_sociale', ''))
            self.partita_iva_edit.setText(self.dati.get('partita_iva', ''))
            self.codice_fiscale_edit.setText(self.dati.get('codice_fiscale', ''))
        elif self.tipo_anagrafica == "Dipendente":
            self.nome_edit.setText(self.dati.get('nome', ''))
            self.cognome_edit.setText(self.dati.get('cognome', ''))
            self.codice_fiscale_edit.setText(self.dati.get('codice_fiscale', ''))
            if 'data_nascita' in self.dati and self.dati['data_nascita']:
                self.data_nascita_edit.setDate(QDate.fromString(self.dati['data_nascita'], Qt.ISODate))
        
        self.telefono_edit.setText(self.dati.get('telefono', ''))
        self.email_edit.setText(self.dati.get('email', ''))
        self.indirizzo_edit.setText(self.dati.get('indirizzo', ''))
        self.cap_edit.setText(self.dati.get('cap', ''))
        self.citta_edit.setText(self.dati.get('citta', ''))
        self.provincia_edit.setText(self.dati.get('provincia', ''))
        self.note_edit.setPlainText(self.dati.get('note', ''))
        self.attivo_check.setChecked(self.dati.get('attivo', True))
    
    def get_data(self) -> Dict[str, Any]:
        """Restituisce i dati del form."""
        data = {}
        
        if self.tipo_anagrafica in ["Fornitore", "Cliente"]:
            data['ragione_sociale'] = self.ragione_sociale_edit.text().strip()
            data['partita_iva'] = self.partita_iva_edit.text().strip()
            data['codice_fiscale'] = self.codice_fiscale_edit.text().strip()
        elif self.tipo_anagrafica == "Dipendente":
            data['nome'] = self.nome_edit.text().strip()
            data['cognome'] = self.cognome_edit.text().strip()
            data['codice_fiscale'] = self.codice_fiscale_edit.text().strip()
            data['data_nascita'] = self.data_nascita_edit.date().toString(Qt.ISODate)
        
        data.update({
            'telefono': self.telefono_edit.text().strip(),
            'email': self.email_edit.text().strip(),
            'indirizzo': self.indirizzo_edit.text().strip(),
            'cap': self.cap_edit.text().strip(),
            'citta': self.citta_edit.text().strip(),
            'provincia': self.provincia_edit.text().strip(),
            'note': self.note_edit.toPlainText().strip(),
            'attivo': self.attivo_check.isChecked()
        })
        
        return data


class AnagraficheWidget(QWidget):
    """Widget principale per la gestione delle anagrafiche."""
    
    def __init__(self, controller: AnagraficheController, config: Config):
        super().__init__()
        self.controller = controller
        self.config = config
        
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """Configura l'interfaccia utente."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("👥 Gestione Anagrafiche")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Pulsanti azioni
        self.nuovo_button = QPushButton("➕ Nuovo")
        self.nuovo_button.clicked.connect(self.new_record)
        header_layout.addWidget(self.nuovo_button)
        
        self.modifica_button = QPushButton("✏️ Modifica")
        self.modifica_button.clicked.connect(self.edit_record)
        self.modifica_button.setEnabled(False)
        header_layout.addWidget(self.modifica_button)
        
        self.elimina_button = QPushButton("🗑️ Elimina")
        self.elimina_button.clicked.connect(self.delete_record)
        self.elimina_button.setEnabled(False)
        header_layout.addWidget(self.elimina_button)
        
        layout.addLayout(header_layout)
        
        # Tab widget per i diversi tipi di anagrafica
        self.tab_widget = QTabWidget()
        
        # Tab Fornitori
        self.fornitori_table = self.create_table(['Codice', 'Ragione Sociale', 'P.IVA', 'Telefono', 'Email', 'Attivo'])
        self.tab_widget.addTab(self.fornitori_table, "Fornitori")
        
        # Tab Clienti
        self.clienti_table = self.create_table(['Codice', 'Ragione Sociale', 'P.IVA', 'Telefono', 'Email', 'Attivo'])
        self.tab_widget.addTab(self.clienti_table, "Clienti")
        
        # Tab Dipendenti
        self.dipendenti_table = self.create_table(['Matricola', 'Nome', 'Cognome', 'Codice Fiscale', 'Telefono', 'Email', 'Attivo'])
        self.tab_widget.addTab(self.dipendenti_table, "Dipendenti")
        
        # Collega i segnali
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        layout.addWidget(self.tab_widget)
        
        # Barra di ricerca
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 Cerca:"))
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Inserisci termine di ricerca...")
        self.search_edit.textChanged.connect(self.search_records)
        search_layout.addWidget(self.search_edit)
        
        layout.addLayout(search_layout)
    
    def create_table(self, headers: List[str]) -> QTableWidget:
        """Crea una tabella con le intestazioni specificate."""
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        # Configura la tabella
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setSortingEnabled(True)
        
        # Adatta le colonne
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        # Collega i segnali
        table.itemSelectionChanged.connect(self.on_selection_changed)
        table.itemDoubleClicked.connect(self.edit_record)
        
        # Menu contestuale
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self.show_context_menu)
        
        return table
    
    def get_current_table(self) -> QTableWidget:
        """Restituisce la tabella attualmente selezionata."""
        current_index = self.tab_widget.currentIndex()
        return [self.fornitori_table, self.clienti_table, self.dipendenti_table][current_index]
    
    def get_current_type(self) -> str:
        """Restituisce il tipo di anagrafica attualmente selezionato."""
        current_index = self.tab_widget.currentIndex()
        return ["Fornitore", "Cliente", "Dipendente"][current_index]
    
    def refresh_data(self):
        """Aggiorna tutti i dati delle tabelle."""
        try:
            # Aggiorna fornitori
            fornitori = self.controller.ottieni_tutti_fornitori()
            self.populate_fornitori_table(fornitori)
            
            # Aggiorna clienti
            clienti = self.controller.ottieni_tutti_clienti()
            self.populate_clienti_table(clienti)
            
            # Aggiorna dipendenti
            dipendenti = self.controller.ottieni_tutti_dipendenti()
            self.populate_dipendenti_table(dipendenti)
            
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Errore nel caricamento dei dati: {e}")
    
    def populate_fornitori_table(self, fornitori):
        """Popola la tabella dei fornitori."""
        self.fornitori_table.setRowCount(len(fornitori))
        
        for row, fornitore in enumerate(fornitori):
            self.fornitori_table.setItem(row, 0, QTableWidgetItem(fornitore.codice_fornitore or ''))
            self.fornitori_table.setItem(row, 1, QTableWidgetItem(fornitore.ragione_sociale or ''))
            self.fornitori_table.setItem(row, 2, QTableWidgetItem(fornitore.partita_iva or ''))
            self.fornitori_table.setItem(row, 3, QTableWidgetItem(fornitore.telefono or ''))
            self.fornitori_table.setItem(row, 4, QTableWidgetItem(fornitore.email or ''))
            self.fornitori_table.setItem(row, 5, QTableWidgetItem("Sì" if fornitore.attivo else "No"))
            
            # Salva l'ID nella prima colonna
            self.fornitori_table.item(row, 0).setData(Qt.UserRole, fornitore.id)
    
    def populate_clienti_table(self, clienti):
        """Popola la tabella dei clienti."""
        self.clienti_table.setRowCount(len(clienti))
        
        for row, cliente in enumerate(clienti):
            self.clienti_table.setItem(row, 0, QTableWidgetItem(cliente.codice_cliente or ''))
            self.clienti_table.setItem(row, 1, QTableWidgetItem(cliente.ragione_sociale or ''))
            self.clienti_table.setItem(row, 2, QTableWidgetItem(cliente.partita_iva or ''))
            self.clienti_table.setItem(row, 3, QTableWidgetItem(cliente.telefono or ''))
            self.clienti_table.setItem(row, 4, QTableWidgetItem(cliente.email or ''))
            self.clienti_table.setItem(row, 5, QTableWidgetItem("Sì" if cliente.attivo else "No"))
            
            # Salva l'ID nella prima colonna
            self.clienti_table.item(row, 0).setData(Qt.UserRole, cliente.id)
    
    def populate_dipendenti_table(self, dipendenti):
        """Popola la tabella dei dipendenti."""
        self.dipendenti_table.setRowCount(len(dipendenti))
        
        for row, dipendente in enumerate(dipendenti):
            self.dipendenti_table.setItem(row, 0, QTableWidgetItem(dipendente.matricola or ''))
            self.dipendenti_table.setItem(row, 1, QTableWidgetItem(dipendente.nome or ''))
            self.dipendenti_table.setItem(row, 2, QTableWidgetItem(dipendente.cognome or ''))
            self.dipendenti_table.setItem(row, 3, QTableWidgetItem(dipendente.codice_fiscale or ''))
            self.dipendenti_table.setItem(row, 4, QTableWidgetItem(dipendente.telefono or ''))
            self.dipendenti_table.setItem(row, 5, QTableWidgetItem(dipendente.email or ''))
            self.dipendenti_table.setItem(row, 6, QTableWidgetItem("Sì" if dipendente.attivo else "No"))
            
            # Salva l'ID nella prima colonna
            self.dipendenti_table.item(row, 0).setData(Qt.UserRole, dipendente.id)
    
    def on_tab_changed(self):
        """Gestisce il cambio di tab."""
        self.on_selection_changed()
    
    def on_selection_changed(self):
        """Gestisce il cambio di selezione."""
        table = self.get_current_table()
        has_selection = len(table.selectedItems()) > 0
        
        self.modifica_button.setEnabled(has_selection)
        self.elimina_button.setEnabled(has_selection)
    
    def new_record(self):
        """Crea un nuovo record."""
        tipo = self.get_current_type()
        
        dialog = AnagraficaDialog(tipo, parent=self)
        if dialog.exec() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                
                if tipo == "Fornitore":
                    self.controller.crea_fornitore(data)
                elif tipo == "Cliente":
                    self.controller.crea_cliente(data)
                elif tipo == "Dipendente":
                    self.controller.crea_dipendente(data)
                
                self.refresh_data()
                QMessageBox.information(self, "Successo", f"{tipo} creato con successo!")
                
            except Exception as e:
                QMessageBox.warning(self, "Errore", f"Errore nella creazione: {e}")
    
    def edit_record(self):
        """Modifica il record selezionato."""
        table = self.get_current_table()
        current_row = table.currentRow()
        
        if current_row < 0:
            return
        
        # Ottieni l'ID dal primo item
        record_id = table.item(current_row, 0).data(Qt.UserRole)
        tipo = self.get_current_type()
        
        try:
            # Carica i dati del record
            if tipo == "Fornitore":
                record = self.controller.ottieni_fornitore(record_id)
            elif tipo == "Cliente":
                record = self.controller.ottieni_cliente(record_id)
            elif tipo == "Dipendente":
                record = self.controller.ottieni_dipendente(record_id)
            
            if not record:
                QMessageBox.warning(self, "Errore", "Record non trovato!")
                return
            
            # Apri dialog di modifica
            dialog = AnagraficaDialog(tipo, record.to_dict(), parent=self)
            if dialog.exec() == QDialog.Accepted:
                data = dialog.get_data()
                
                if tipo == "Fornitore":
                    self.controller.aggiorna_fornitore(record_id, data)
                elif tipo == "Cliente":
                    self.controller.aggiorna_cliente(record_id, data)
                elif tipo == "Dipendente":
                    self.controller.aggiorna_dipendente(record_id, data)
                
                self.refresh_data()
                QMessageBox.information(self, "Successo", f"{tipo} aggiornato con successo!")
                
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Errore nella modifica: {e}")
    
    def delete_record(self):
        """Elimina il record selezionato."""
        table = self.get_current_table()
        current_row = table.currentRow()
        
        if current_row < 0:
            return
        
        record_id = table.item(current_row, 0).data(Qt.UserRole)
        tipo = self.get_current_type()
        
        # Conferma eliminazione
        reply = QMessageBox.question(
            self, 
            "Conferma eliminazione",
            f"Sei sicuro di voler eliminare questo {tipo.lower()}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if tipo == "Fornitore":
                    self.controller.elimina_fornitore(record_id)
                elif tipo == "Cliente":
                    self.controller.elimina_cliente(record_id)
                elif tipo == "Dipendente":
                    self.controller.elimina_dipendente(record_id)
                
                self.refresh_data()
                QMessageBox.information(self, "Successo", f"{tipo} eliminato con successo!")
                
            except Exception as e:
                QMessageBox.warning(self, "Errore", f"Errore nell'eliminazione: {e}")
    
    def search_records(self):
        """Cerca record in base al termine inserito."""
        search_term = self.search_edit.text().strip()
        
        if not search_term:
            self.refresh_data()
            return
        
        try:
            tipo = self.get_current_type()
            
            if tipo == "Fornitore":
                results = self.controller.cerca_fornitori(search_term)
                self.populate_fornitori_table(results)
            elif tipo == "Cliente":
                results = self.controller.cerca_clienti(search_term)
                self.populate_clienti_table(results)
            elif tipo == "Dipendente":
                results = self.controller.cerca_dipendenti(search_term)
                self.populate_dipendenti_table(results)
                
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Errore nella ricerca: {e}")
    
    def show_context_menu(self, position):
        """Mostra il menu contestuale."""
        table = self.get_current_table()
        item = table.itemAt(position)
        
        if item is None:
            return
        
        menu = QMenu(self)
        
        edit_action = QAction("Modifica", self)
        edit_action.triggered.connect(self.edit_record)
        menu.addAction(edit_action)
        
        delete_action = QAction("Elimina", self)
        delete_action.triggered.connect(self.delete_record)
        menu.addAction(delete_action)
        
        menu.exec(table.mapToGlobal(position))