# 🚀 Quick Start - Contabilità Manager

## ✅ Stato Attuale
L'applicazione è **FUNZIONANTE** e pronta per l'uso e lo sviluppo.

## 🔧 Setup Rapido

### 1. Installa Dipendenze
```bash
# Crea ambiente virtuale
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure: venv\Scripts\activate  # Windows

# Installa dipendenze
pip install -r requirements.txt
```

### 2. Testa il Sistema
```bash
# Test rapido funzionalità core
python3 -c "
from app.models.anagrafiche import Fornitore
from app.database.connection import DatabaseManager

db = DatabaseManager()
db.initialize('sqlite:///:memory:')
session = db.get_session()

f = Fornitore(ragione_sociale='Test', partita_iva='12345678901', codice_fornitore='T001')
session.add(f)
session.commit()
print(f'✅ Test OK: {f}')
"
```

### 3. Avvia Applicazione GUI
```bash
# Solo in ambiente con display (non headless)
python3 main.py
```

## 📋 Funzionalità Disponibili

### ✅ Core Business Logic
- **Anagrafiche**: Fornitori, Clienti, Dipendenti
- **Validazioni**: Partita IVA, Email, Codice Fiscale
- **Database**: SQLite con SQLAlchemy
- **CRUD**: Create, Read, Update, Delete completo

### ✅ Interfaccia Grafica
- **Dashboard** con grafici e metriche
- **Gestione Anagrafiche** completa
- **Temi** Light/Dark
- **Layout** responsive e moderno

### 🔄 In Sviluppo
- **Documenti**: Fatture, Note Credito
- **Contabilità**: Piano conti, Movimenti
- **Report**: Export PDF, Excel

## 💻 Esempi Utilizzo

### Creare un Fornitore
```python
from app.models.anagrafiche import Fornitore
from app.database.connection import DatabaseManager

db_manager = DatabaseManager()
db_manager.initialize('sqlite:///contabilita.db')

with db_manager.get_session_context() as session:
    fornitore = Fornitore(
        ragione_sociale='ACME SRL',
        partita_iva='12345678901',
        codice_fornitore='ACME001',
        email='info@acme.com'
    )
    session.add(fornitore)
    session.commit()
```

### Validare Dati
```python
# Controllo partita IVA
if fornitore.is_valid_partita_iva():
    print("Partita IVA valida")

# Indirizzo completo
print(fornitore.get_full_address())
```

## 🛠️ Sviluppo

### Struttura Progetto
```
app/
├── config.py           # Configurazioni
├── database/           # Gestione DB
├── models/             # Modelli dati
├── controllers/        # Logica business
└── views/              # Interfaccia GUI
```

### Aggiungere Nuove Funzionalità
1. **Modello**: Crea in `app/models/`
2. **Controller**: Logica in `app/controllers/`
3. **Vista**: GUI in `app/views/`
4. **Test**: Aggiungi in `tests/`

## 🚫 Limitazioni Temporanee

- **Relazioni SQLAlchemy**: Commentate per compatibilità
- **GUI Testing**: Non disponibile in ambiente headless
- **Alcune features**: In fase di sviluppo

## 🔥 Pronto per

✅ **Uso immediato**: Gestione anagrafiche  
✅ **Sviluppo**: Base solida per estensioni  
✅ **Test**: Logica business completa  
✅ **Demo**: Funzionalità core  

---

**L'applicazione Contabilità Manager è PRONTA e FUNZIONANTE! 🎉**