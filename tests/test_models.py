"""
Test per i modelli del database
===============================

Test unitari per verificare il corretto funzionamento dei modelli.
"""

import pytest
from datetime import datetime
from decimal import Decimal

from app.models.anagrafiche import Fornitore, Cliente, Dipendente
from app.models.documenti import Fattura, RigaFattura, TipoDocumento, StatoDocumento
from app.models.contabilita import ContoContabile, MovimentoContabile, TipoConto


class TestAnagrafiche:
    """Test per i modelli delle anagrafiche."""
    
    def test_fornitore_creation(self):
        """Test creazione fornitore."""
        fornitore = Fornitore(
            ragione_sociale="Test Fornitore SRL",
            partita_iva="12345678901",
            codice_fornitore="FOR001",
            telefono="0123456789",
            email="test@fornitore.com"
        )
        
        assert fornitore.ragione_sociale == "Test Fornitore SRL"
        assert fornitore.partita_iva == "12345678901"
        assert fornitore.codice_fornitore == "FOR001"
        assert fornitore.attivo == True
    
    def test_fornitore_partita_iva_validation(self):
        """Test validazione partita IVA fornitore."""
        fornitore = Fornitore(
            ragione_sociale="Test",
            partita_iva="12345678901",
            codice_fornitore="FOR001"
        )
        
        assert fornitore.is_valid_partita_iva() == True
        
        fornitore.partita_iva = "123"  # Troppo corta
        assert fornitore.is_valid_partita_iva() == False
        
        fornitore.partita_iva = "1234567890A"  # Contiene lettere
        assert fornitore.is_valid_partita_iva() == False
    
    def test_cliente_creation(self):
        """Test creazione cliente."""
        cliente = Cliente(
            ragione_sociale="Test Cliente SPA",
            codice_cliente="CLI001",
            tipo_cliente="Azienda",
            partita_iva="98765432109"
        )
        
        assert cliente.ragione_sociale == "Test Cliente SPA"
        assert cliente.codice_cliente == "CLI001"
        assert cliente.tipo_cliente == "Azienda"
        assert cliente.attivo == True
    
    def test_dipendente_creation(self):
        """Test creazione dipendente."""
        dipendente = Dipendente(
            nome="Mario",
            cognome="Rossi",
            codice_fiscale="RSSMRA80A01H501A",
            matricola="DIP001",
            data_nascita=datetime(1980, 1, 1)
        )
        
        assert dipendente.nome == "Mario"
        assert dipendente.cognome == "Rossi"
        assert dipendente.get_full_name() == "Mario Rossi"
        assert dipendente.attivo == True
    
    def test_dipendente_age_calculation(self):
        """Test calcolo età dipendente."""
        dipendente = Dipendente(
            nome="Test",
            cognome="User",
            codice_fiscale="TSTUSER80A01H501A",
            matricola="DIP002",
            data_nascita=datetime(1990, 1, 1)
        )
        
        age = dipendente.calculate_age()
        expected_age = datetime.now().year - 1990
        if datetime.now().month == 1 and datetime.now().day == 1:
            expected_age += 1
        
        assert age >= expected_age - 1  # Tolleranza di 1 anno


class TestDocumenti:
    """Test per i modelli dei documenti."""
    
    def test_fattura_creation(self):
        """Test creazione fattura."""
        fattura = Fattura(
            numero_fattura="FV2024001",
            data_fattura=datetime.now(),
            tipo_documento=TipoDocumento.FATTURA_VENDITA,
            imponibile=Decimal("100.00"),
            iva=Decimal("22.00"),
            totale=Decimal("122.00")
        )
        
        assert fattura.numero_fattura == "FV2024001"
        assert fattura.tipo_documento == TipoDocumento.FATTURA_VENDITA
        assert fattura.stato == StatoDocumento.BOZZA
        assert fattura.imponibile == Decimal("100.00")
        assert fattura.totale == Decimal("122.00")
    
    def test_riga_fattura_calculations(self):
        """Test calcoli riga fattura."""
        riga = RigaFattura(
            descrizione="Test prodotto",
            quantita=Decimal("2.0"),
            prezzo_unitario=Decimal("50.00"),
            aliquota_iva=Decimal("22.0")
        )
        
        assert riga.get_subtotale() == 100.0  # 2 * 50
        assert riga.get_iva() == 22.0  # 100 * 22%
        assert riga.get_totale() == 122.0  # 100 + 22
    
    def test_riga_fattura_with_discount(self):
        """Test calcoli riga fattura con sconto."""
        riga = RigaFattura(
            descrizione="Test prodotto con sconto",
            quantita=Decimal("1.0"),
            prezzo_unitario=Decimal("100.00"),
            aliquota_iva=Decimal("22.0"),
            sconto_percentuale=Decimal("10.0")  # 10% sconto
        )
        
        assert riga.get_subtotale() == 90.0  # 100 - 10%
        assert riga.get_iva() == 19.8  # 90 * 22%
        assert riga.get_totale() == 109.8  # 90 + 19.8
    
    def test_fattura_scadenza(self):
        """Test verifica scadenza fattura."""
        # Fattura non scaduta
        fattura = Fattura(
            numero_fattura="FV2024002",
            data_fattura=datetime.now(),
            data_scadenza=datetime.now().replace(year=datetime.now().year + 1),
            tipo_documento=TipoDocumento.FATTURA_VENDITA
        )
        
        assert fattura.is_scaduta() == False
        
        # Fattura scaduta
        fattura.data_scadenza = datetime(2020, 1, 1)
        assert fattura.is_scaduta() == True
        
        # Fattura pagata (non può essere scaduta)
        fattura.pagata = True
        assert fattura.is_scaduta() == False


class TestContabilita:
    """Test per i modelli della contabilità."""
    
    def test_conto_contabile_creation(self):
        """Test creazione conto contabile."""
        conto = ContoContabile(
            codice="111",
            descrizione="Cassa",
            tipo_conto=TipoConto.ATTIVO,
            saldo_iniziale=Decimal("1000.00")
        )
        
        assert conto.codice == "111"
        assert conto.descrizione == "Cassa"
        assert conto.tipo_conto == TipoConto.ATTIVO
        assert conto.saldo_iniziale == Decimal("1000.00")
        assert conto.attivo == True
        assert conto.utilizzabile == True
    
    def test_conto_saldo_calculation(self):
        """Test calcolo saldo conto."""
        # Conto attivo (dare > avere)
        conto_attivo = ContoContabile(
            codice="111",
            descrizione="Cassa",
            tipo_conto=TipoConto.ATTIVO,
            saldo_iniziale=Decimal("1000.00"),
            saldo_dare=Decimal("500.00"),
            saldo_avere=Decimal("200.00")
        )
        
        # Saldo = 1000 + 500 - 200 = 1300
        assert conto_attivo.get_saldo_attuale() == 1300.0
        
        # Conto passivo (avere > dare)
        conto_passivo = ContoContabile(
            codice="211",
            descrizione="Fornitori",
            tipo_conto=TipoConto.PASSIVO,
            saldo_iniziale=Decimal("0.00"),
            saldo_dare=Decimal("200.00"),
            saldo_avere=Decimal("800.00")
        )
        
        # Saldo = 0 + 800 - 200 = 600
        assert conto_passivo.get_saldo_attuale() == 600.0
    
    def test_movimento_contabile_creation(self):
        """Test creazione movimento contabile."""
        movimento = MovimentoContabile(
            numero_movimento="MOV001",
            data_movimento=datetime.now(),
            causale="Test movimento",
            conto_dare_id=1,
            conto_avere_id=2,
            importo=Decimal("500.00")
        )
        
        assert movimento.numero_movimento == "MOV001"
        assert movimento.causale == "Test movimento"
        assert movimento.importo == Decimal("500.00")
        assert movimento.is_valido() == True
    
    def test_movimento_contabile_validation(self):
        """Test validazione movimento contabile."""
        # Movimento non valido (stesso conto dare e avere)
        movimento = MovimentoContabile(
            numero_movimento="MOV002",
            causale="Test movimento non valido",
            conto_dare_id=1,
            conto_avere_id=1,  # Stesso conto!
            importo=Decimal("100.00")
        )
        
        assert movimento.is_valido() == False
        
        # Movimento non valido (importo zero)
        movimento.conto_avere_id = 2
        movimento.importo = Decimal("0.00")
        assert movimento.is_valido() == False
        
        # Movimento non valido (causale vuota)
        movimento.importo = Decimal("100.00")
        movimento.causale = ""
        assert movimento.is_valido() == False


# Configurazione pytest
@pytest.fixture
def sample_fornitore():
    """Fixture per fornitore di esempio."""
    return Fornitore(
        ragione_sociale="Fornitore Test SRL",
        partita_iva="12345678901",
        codice_fornitore="FOR001",
        telefono="0123456789",
        email="test@fornitore.com",
        indirizzo="Via Test 123",
        cap="12345",
        citta="Test City",
        provincia="TC"
    )


@pytest.fixture
def sample_cliente():
    """Fixture per cliente di esempio."""
    return Cliente(
        ragione_sociale="Cliente Test SPA",
        codice_cliente="CLI001",
        tipo_cliente="Azienda",
        partita_iva="98765432109",
        telefono="0987654321",
        email="test@cliente.com"
    )


@pytest.fixture
def sample_fattura():
    """Fixture per fattura di esempio."""
    return Fattura(
        numero_fattura="FV2024001",
        data_fattura=datetime.now(),
        tipo_documento=TipoDocumento.FATTURA_VENDITA,
        stato=StatoDocumento.EMESSO,
        imponibile=Decimal("100.00"),
        iva=Decimal("22.00"),
        totale=Decimal("122.00"),
        oggetto="Fattura di test"
    )