# 📊 Contabilità Manager

Un'applicazione desktop completa e professionale per la gestione della contabilità aziendale, sviluppata in Python con interfaccia grafica moderna.

## ✨ Caratteristiche Principali

### 🎯 Gestione Completa
- **Anagrafiche**: Gestione completa di fornitori, clienti e dipendenti
- **Documenti Contabili**: Fatture di vendita/acquisto, note di credito, prima nota
- **Contabilità Generale**: Piano dei conti, movimenti contabili, bilanci
- **Report Finanziari**: Bilancio, conto economico, estratti conto
- **Dashboard Interattiva**: Grafici e statistiche in tempo reale

### 🎨 Interfaccia Moderna
- **Design Flat**: Interfaccia moderna e user-friendly
- **Temi**: Supporto per modalità chiara e scura
- **Layout Responsive**: Adattabile a diverse risoluzioni
- **Grafici Interattivi**: Visualizzazioni con Matplotlib
- **Navigazione Intuitiva**: Menu a schede e barre strumenti

### 🔧 Architettura Professionale
- **Pattern MVC**: Separazione tra logica, dati e presentazione
- **Modularità**: Codice organizzato in moduli riutilizzabili
- **Database**: SQLite per prototipo, espandibile a PostgreSQL/MySQL
- **Validazione**: Controlli in tempo reale sui dati inseriti
- **Internazionalizzazione**: Supporto multilingua (IT/EN)

## 🚀 Installazione e Avvio

### Requisiti di Sistema
- **Python**: 3.10 o superiore
- **Sistema Operativo**: Windows, macOS, Linux
- **Memoria**: Almeno 512 MB RAM
- **Spazio Disco**: 100 MB per l'installazione

### Installazione Rapida

1. **Clona il repository**:
   ```bash
   git clone <repository-url>
   cd contabilita-manager
   ```

2. **Crea ambiente virtuale** (consigliato):
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Installa le dipendenze**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Avvia l'applicazione**:
   ```bash
   python main.py
   ```

### Installazione Avanzata

Per uno sviluppo avanzato o personalizzazioni:

```bash
# Installa dipendenze di sviluppo
pip install -r requirements.txt pytest pytest-qt

# Esegui i test
python -m pytest tests/

# Avvia con logging dettagliato
python main.py --debug
```

## 📖 Guida Rapida

### Primo Avvio
1. **Avvia l'applicazione**: Esegui `python main.py`
2. **Database**: Il database SQLite viene creato automaticamente in `data/contabilita.db`
3. **Configurazione**: Usa Menu → Modifica → Impostazioni per personalizzare

### Funzionalità Base

#### 👥 Gestione Anagrafiche
- **Accesso**: Scheda "Anagrafiche"
- **Fornitori**: Aggiungi, modifica, elimina fornitori
- **Clienti**: Gestione completa della base clienti
- **Dipendenti**: Anagrafica del personale aziendale
- **Ricerca**: Filtro rapido per trovare record

#### 📄 Documenti Contabili
- **Fatture**: Emissione fatture di vendita e acquisto
- **Note Credito**: Gestione note di accredito
- **Prima Nota**: Registrazioni contabili manuali
- **Stati**: Bozza → Emesso → Pagato

#### 💼 Contabilità Generale
- **Piano dei Conti**: Struttura gerarchica dei conti
- **Movimenti**: Registrazioni dare/avere
- **Bilancio**: Situazione patrimoniale
- **Saldi**: Calcolo automatico dei saldi contabili

#### 📈 Report e Dashboard
- **Dashboard**: Panoramica con grafici interattivi
- **Bilancio**: Report della situazione patrimoniale
- **Conto Economico**: Analisi ricavi/costi
- **Estratti Conto**: Per clienti e fornitori
- **Export**: Esportazione in Excel, CSV, PDF

## 🛠️ Configurazione

### Impostazioni Applicazione
Accedi alle impostazioni tramite **Menu → Modifica → Impostazioni**:

- **Tema**: Chiaro o Scuro
- **Lingua**: Italiano o Inglese
- **Dimensioni Finestra**: Personalizzabili
- **Valuta**: Simbolo e decimali
- **Database**: Configurazione connessione

### Personalizzazione Tema
L'applicazione supporta temi personalizzabili. I temi sono definiti in `app/views/main_window.py` nella classe `ThemeManager`.

### Database
- **Predefinito**: SQLite (`data/contabilita.db`)
- **Avanzato**: Modificare `DATABASE_URL` in `app/config.py` per PostgreSQL/MySQL

## 🏗️ Architettura

### Struttura del Progetto
```
contabilita-manager/
├── app/                      # Applicazione principale
│   ├── __init__.py
│   ├── config.py            # Configurazioni
│   ├── database/            # Gestione database
│   │   ├── __init__.py
│   │   ├── base.py          # Classe base SQLAlchemy
│   │   └── connection.py    # Gestore connessioni
│   ├── models/              # Modelli dati
│   │   ├── __init__.py
│   │   ├── anagrafiche.py   # Fornitori, clienti, dipendenti
│   │   ├── documenti.py     # Fatture, note credito
│   │   └── contabilita.py   # Conti e movimenti
│   ├── controllers/         # Logica di business
│   │   ├── __init__.py
│   │   ├── base_controller.py
│   │   ├── anagrafiche_controller.py
│   │   ├── documenti_controller.py
│   │   ├── contabilita_controller.py
│   │   └── report_controller.py
│   └── views/               # Interfaccia grafica
│       ├── __init__.py
│       ├── main_window.py   # Finestra principale
│       ├── dashboard_widget.py
│       ├── anagrafiche_widget.py
│       ├── documenti_widget.py
│       ├── contabilita_widget.py
│       └── report_widget.py
├── tests/                   # Test unitari
├── data/                    # Database e file dati
├── logs/                    # File di log
├── resources/               # Risorse (temi, traduzioni)
├── requirements.txt         # Dipendenze Python
├── main.py                 # File principale
└── README.md               # Documentazione
```

### Pattern Architetturali
- **MVC (Model-View-Controller)**: Separazione responsabilità
- **Repository Pattern**: Astrazione accesso dati
- **Factory Pattern**: Creazione oggetti complessi
- **Observer Pattern**: Aggiornamenti interfaccia

## 🧪 Test

### Esecuzione Test
```bash
# Test completi
python -m pytest

# Test con copertura
python -m pytest --cov=app

# Test specifici
python -m pytest tests/test_models.py

# Test interfaccia grafica
python -m pytest tests/test_gui.py
```

### Tipologie di Test
- **Unit Test**: Test dei singoli moduli
- **Integration Test**: Test di integrazione
- **GUI Test**: Test dell'interfaccia (con pytest-qt)
- **Performance Test**: Test delle prestazioni

## 📊 Funzionalità Avanzate

### Dashboard Interattiva
- **Metriche Principali**: Fatturato, costi, margini
- **Grafici**: Linee, barre, torta
- **Aggiornamento**: Automatico ogni 5 minuti
- **Esportazione**: PNG, PDF, Excel

### Validazione Dati
- **Partita IVA**: Controllo formato italiano
- **Codice Fiscale**: Validazione algoritmica
- **Email**: Controllo formato RFC
- **Date**: Validazione e conversione automatica

### Export e Import
- **Formati Supportati**: Excel, CSV, PDF
- **Report Personalizzati**: Template modificabili
- **Backup**: Esportazione completa database
- **Import**: Da sistemi contabili esistenti

## 🔒 Sicurezza

### Protezione Dati
- **Database**: Backup automatici
- **Validazione**: Input sanitization
- **Logging**: Tracciamento operazioni
- **Errori**: Gestione graceful

### Best Practices
- **Password**: Non gestite (focus su applicazione locale)
- **Backup**: Consigliato backup regolare del database
- **Aggiornamenti**: Mantenere dipendenze aggiornate

## 🚧 Roadmap

### Versione 1.1 (Q2 2024)
- [ ] Generazione PDF fatture
- [ ] Import/Export CSV avanzato
- [ ] Gestione multi-azienda
- [ ] API REST per integrazioni

### Versione 1.2 (Q3 2024)
- [ ] Modulo magazzino
- [ ] Gestione ordini
- [ ] CRM integrato
- [ ] App mobile companion

### Versione 2.0 (Q4 2024)
- [ ] Architettura cloud
- [ ] Collaborazione multi-utente
- [ ] BI e analytics avanzate
- [ ] Integrazione PagoPa

## 🤝 Contributi

### Come Contribuire
1. **Fork** del repository
2. **Branch** per la feature: `git checkout -b feature/nuova-funzionalita`
3. **Commit** delle modifiche: `git commit -m 'Aggiunge nuova funzionalità'`
4. **Push** del branch: `git push origin feature/nuova-funzionalita`
5. **Pull Request**

### Linee Guida
- **Codice**: Seguire PEP 8
- **Documentazione**: Docstring per ogni funzione
- **Test**: Aggiungere test per nuove funzionalità
- **Commit**: Messaggi descrittivi

## 📝 Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi il file `LICENSE` per i dettagli.

## 📞 Supporto

### Canali di Supporto
- **Issues**: GitHub Issues per bug e richieste
- **Discussioni**: GitHub Discussions per domande
- **Email**: support@contabilita-manager.com
- **Documentazione**: Wiki del progetto

### FAQ

**Q: Posso usare un database diverso da SQLite?**
A: Sì, modificando la configurazione in `app/config.py` per PostgreSQL o MySQL.

**Q: L'applicazione funziona offline?**
A: Completamente. Non richiede connessione internet.

**Q: Posso personalizzare i report?**
A: Sì, i template sono modificabili nella directory `resources/templates/`.

**Q: È possibile importare dati da altri software?**
A: Attualmente supporta CSV. Import da altri formati in sviluppo.

---

## 🎉 Ringraziamenti

Sviluppato con ❤️ utilizzando:
- **Python** & **PySide6** per l'interfaccia
- **SQLAlchemy** per il database
- **Matplotlib** per i grafici
- **Pandas** per l'analisi dati

---

**Contabilità Manager** - *La soluzione completa per la tua contabilità aziendale*
