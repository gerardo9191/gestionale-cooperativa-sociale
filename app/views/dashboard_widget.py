"""
Dashboard Widget
================

Widget per la dashboard principale con grafici e statistiche.
"""

from typing import Dict, Any, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QFrame, QScrollArea, QGroupBox, QProgressBar,
    QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QFont, QPalette, QColor

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np

from ..config import Config
from ..controllers.report_controller import ReportController


class MetricCard(QFrame):
    """Widget per visualizzare una metrica con valore e descrizione."""
    
    def __init__(self, title: str, value: str, subtitle: str = "", color: str = "#2196f3"):
        super().__init__()
        self.setFrameStyle(QFrame.Box)
        self.setFixedSize(200, 120)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Titolo
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {color};")
        layout.addWidget(title_label)
        
        # Valore principale
        value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(18)
        value_font.setBold(True)
        value_label.setFont(value_font)
        layout.addWidget(value_label)
        
        # Sottotitolo
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_font = QFont()
            subtitle_font.setPointSize(8)
            subtitle_label.setFont(subtitle_font)
            subtitle_label.setStyleSheet("color: #757575;")
            layout.addWidget(subtitle_label)
        
        layout.addStretch()
    
    def update_value(self, value: str, subtitle: str = ""):
        """Aggiorna il valore della metrica."""
        # Trova e aggiorna il label del valore
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, QLabel) and widget.font().pointSize() == 18:
                    widget.setText(value)
                elif isinstance(widget, QLabel) and widget.font().pointSize() == 8 and subtitle:
                    widget.setText(subtitle)


class ChartWidget(QFrame):
    """Widget base per i grafici."""
    
    def __init__(self, title: str, width: int = 400, height: int = 300):
        super().__init__()
        self.setFrameStyle(QFrame.Box)
        self.setMinimumSize(width, height)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Titolo
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Canvas per il grafico
        self.figure = Figure(figsize=(width/100, height/100), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Configura il grafico
        self.figure.patch.set_facecolor('white')
        self.ax = self.figure.add_subplot(111)
    
    def clear_chart(self):
        """Pulisce il grafico."""
        self.ax.clear()
        self.canvas.draw()
    
    def update_chart(self):
        """Aggiorna il grafico - da implementare nelle sottoclassi."""
        self.canvas.draw()


class LineChartWidget(ChartWidget):
    """Widget per grafici a linee."""
    
    def plot_line(self, x_data: List, y_data: List, label: str = "", color: str = '#2196f3'):
        """Disegna una linea sul grafico."""
        self.ax.plot(x_data, y_data, label=label, color=color, linewidth=2, marker='o')
        self.ax.grid(True, alpha=0.3)
        self.ax.legend()
        self.update_chart()
    
    def plot_multiple_lines(self, data: Dict[str, tuple]):
        """Disegna multiple linee sul grafico."""
        colors = ['#2196f3', '#4caf50', '#ff9800', '#f44336', '#9c27b0']
        
        for i, (label, (x_data, y_data)) in enumerate(data.items()):
            color = colors[i % len(colors)]
            self.ax.plot(x_data, y_data, label=label, color=color, linewidth=2, marker='o')
        
        self.ax.grid(True, alpha=0.3)
        self.ax.legend()
        self.update_chart()


class BarChartWidget(ChartWidget):
    """Widget per grafici a barre."""
    
    def plot_bar(self, labels: List[str], values: List[float], colors: List[str] = None):
        """Disegna un grafico a barre."""
        if not colors:
            colors = ['#2196f3'] * len(values)
        
        bars = self.ax.bar(labels, values, color=colors)
        
        # Aggiungi valori sopra le barre
        for bar, value in zip(bars, values):
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{value:.0f}', ha='center', va='bottom')
        
        self.ax.grid(True, alpha=0.3, axis='y')
        self.update_chart()


class PieChartWidget(ChartWidget):
    """Widget per grafici a torta."""
    
    def plot_pie(self, labels: List[str], values: List[float], colors: List[str] = None):
        """Disegna un grafico a torta."""
        if not colors:
            colors = ['#2196f3', '#4caf50', '#ff9800', '#f44336', '#9c27b0']
        
        # Filtra i valori zero
        filtered_data = [(l, v) for l, v in zip(labels, values) if v > 0]
        if not filtered_data:
            self.ax.text(0.5, 0.5, 'Nessun dato disponibile', 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.update_chart()
            return
        
        labels, values = zip(*filtered_data)
        
        wedges, texts, autotexts = self.ax.pie(values, labels=labels, colors=colors[:len(values)], 
                                              autopct='%1.1f%%', startangle=90)
        
        # Migliora la leggibilità
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_weight('bold')
        
        self.update_chart()


class DashboardWidget(QWidget):
    """Widget principale della dashboard."""
    
    def __init__(self, report_controller: ReportController, config: Config):
        super().__init__()
        self.report_controller = report_controller
        self.config = config
        
        self.setup_ui()
        self.refresh_data()
        
        # Timer per aggiornamenti automatici
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(300000)  # Aggiorna ogni 5 minuti
    
    def setup_ui(self):
        """Configura l'interfaccia utente."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("📊 Dashboard")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Pulsante aggiorna
        refresh_button = QPushButton("🔄 Aggiorna")
        refresh_button.clicked.connect(self.refresh_data)
        header_layout.addWidget(refresh_button)
        
        layout.addLayout(header_layout)
        
        # Scroll area per il contenuto
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        # Metriche principali
        self.setup_metrics_section(content_layout)
        
        # Grafici
        self.setup_charts_section(content_layout)
        
        # Tabelle riassuntive
        self.setup_summary_section(content_layout)
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
    
    def setup_metrics_section(self, layout: QVBoxLayout):
        """Configura la sezione delle metriche principali."""
        metrics_group = QGroupBox("📈 Metriche Principali")
        metrics_layout = QHBoxLayout(metrics_group)
        
        # Crea le card delle metriche
        self.fatturato_card = MetricCard("Fatturato Totale", "€ 0", "Ultimi 12 mesi", "#4caf50")
        self.costi_card = MetricCard("Costi Totali", "€ 0", "Ultimi 12 mesi", "#f44336")
        self.margine_card = MetricCard("Margine", "€ 0", "Fatturato - Costi", "#2196f3")
        self.fatture_card = MetricCard("Fatture", "0", "Emesse quest'anno", "#ff9800")
        self.clienti_card = MetricCard("Clienti Attivi", "0", "Totale clienti", "#9c27b0")
        
        metrics_layout.addWidget(self.fatturato_card)
        metrics_layout.addWidget(self.costi_card)
        metrics_layout.addWidget(self.margine_card)
        metrics_layout.addWidget(self.fatture_card)
        metrics_layout.addWidget(self.clienti_card)
        metrics_layout.addStretch()
        
        layout.addWidget(metrics_group)
    
    def setup_charts_section(self, layout: QVBoxLayout):
        """Configura la sezione dei grafici."""
        charts_group = QGroupBox("📊 Grafici")
        charts_layout = QGridLayout(charts_group)
        
        # Grafico fatturato vs costi
        self.fatturato_chart = LineChartWidget("Fatturato vs Costi (Ultimi 12 mesi)", 500, 300)
        charts_layout.addWidget(self.fatturato_chart, 0, 0)
        
        # Grafico fatture per stato
        self.fatture_stato_chart = PieChartWidget("Distribuzione Fatture per Stato", 400, 300)
        charts_layout.addWidget(self.fatture_stato_chart, 0, 1)
        
        # Grafico top clienti
        self.top_clienti_chart = BarChartWidget("Top 10 Clienti per Fatturato", 500, 300)
        charts_layout.addWidget(self.top_clienti_chart, 1, 0)
        
        # Grafico evoluzione fatturato
        self.evoluzione_chart = LineChartWidget("Evoluzione Fatturato (24 mesi)", 400, 300)
        charts_layout.addWidget(self.evoluzione_chart, 1, 1)
        
        layout.addWidget(charts_group)
    
    def setup_summary_section(self, layout: QVBoxLayout):
        """Configura la sezione delle tabelle riassuntive."""
        summary_group = QGroupBox("📋 Riassunto")
        summary_layout = QVBoxLayout(summary_group)
        
        # Fatture scadute
        scadute_frame = QFrame()
        scadute_frame.setFrameStyle(QFrame.Box)
        scadute_layout = QVBoxLayout(scadute_frame)
        
        scadute_title = QLabel("⚠️ Fatture Scadute")
        scadute_title.setStyleSheet("font-weight: bold; color: #f44336; font-size: 12pt;")
        scadute_layout.addWidget(scadute_title)
        
        self.scadute_label = QLabel("Caricamento...")
        scadute_layout.addWidget(self.scadute_label)
        
        summary_layout.addWidget(scadute_frame)
        
        # Progress bars per obiettivi
        obiettivi_frame = QFrame()
        obiettivi_frame.setFrameStyle(QFrame.Box)
        obiettivi_layout = QVBoxLayout(obiettivi_frame)
        
        obiettivi_title = QLabel("🎯 Obiettivi Mensili")
        obiettivi_title.setStyleSheet("font-weight: bold; color: #2196f3; font-size: 12pt;")
        obiettivi_layout.addWidget(obiettivi_title)
        
        # Progress bar fatturato
        fatturato_progress_layout = QHBoxLayout()
        fatturato_progress_layout.addWidget(QLabel("Fatturato:"))
        self.fatturato_progress = QProgressBar()
        self.fatturato_progress.setRange(0, 100)
        fatturato_progress_layout.addWidget(self.fatturato_progress)
        self.fatturato_progress_label = QLabel("0%")
        fatturato_progress_layout.addWidget(self.fatturato_progress_label)
        obiettivi_layout.addLayout(fatturato_progress_layout)
        
        summary_layout.addWidget(obiettivi_frame)
        
        layout.addWidget(summary_group)
    
    def refresh_data(self):
        """Aggiorna tutti i dati della dashboard."""
        try:
            # Ottieni i dati dal controller
            dashboard_data = self.report_controller.genera_dashboard_data()
            grafici_data = self.report_controller.genera_dati_grafici()
            
            # Aggiorna le metriche
            self.update_metrics(dashboard_data)
            
            # Aggiorna i grafici
            self.update_charts(grafici_data)
            
            # Aggiorna il riassunto
            self.update_summary(dashboard_data)
            
        except Exception as e:
            print(f"Errore nell'aggiornamento della dashboard: {e}")
    
    def update_metrics(self, data: Dict[str, Any]):
        """Aggiorna le metriche principali."""
        # Calcola totali
        fatturato_totale = sum(m['fatturato'] for m in data.get('fatturato_mensile', []))
        costi_totali = sum(m['costi'] for m in data.get('costi_mensili', []))
        margine = fatturato_totale - costi_totali
        
        fatture_stats = data.get('fatture', {})
        anagrafiche_stats = data.get('anagrafiche', {})
        
        # Aggiorna le card
        self.fatturato_card.update_value(f"€ {fatturato_totale:,.0f}")
        self.costi_card.update_value(f"€ {costi_totali:,.0f}")
        self.margine_card.update_value(f"€ {margine:,.0f}")
        self.fatture_card.update_value(str(fatture_stats.get('totale_fatture', 0)))
        self.clienti_card.update_value(str(anagrafiche_stats.get('clienti', {}).get('attivi', 0)))
    
    def update_charts(self, data: Dict[str, Any]):
        """Aggiorna i grafici."""
        try:
            # Fatturato vs Costi
            fatturato_vs_costi = data.get('fatturato_vs_costi', {})
            if fatturato_vs_costi:
                self.fatturato_chart.clear_chart()
                
                fatturato_data = fatturato_vs_costi.get('fatturato', [])
                costi_data = fatturato_vs_costi.get('costi', [])
                
                if fatturato_data and costi_data:
                    mesi_fat = [item['mese'] for item in fatturato_data]
                    valori_fat = [item['fatturato'] for item in fatturato_data]
                    valori_costi = [item['costi'] for item in costi_data]
                    
                    self.fatturato_chart.plot_multiple_lines({
                        'Fatturato': (mesi_fat, valori_fat),
                        'Costi': (mesi_fat, valori_costi)
                    })
            
            # Fatture per stato
            fatture_per_stato = data.get('fatture_per_stato', {})
            if fatture_per_stato:
                self.fatture_stato_chart.clear_chart()
                
                labels = list(fatture_per_stato.keys())
                values = [fatture_per_stato[label] for label in labels]
                
                if any(values):
                    self.fatture_stato_chart.plot_pie(labels, values)
            
            # Top clienti - dati fittizi per ora
            self.top_clienti_chart.clear_chart()
            clienti_labels = ['Cliente A', 'Cliente B', 'Cliente C', 'Cliente D', 'Cliente E']
            clienti_values = [15000, 12000, 8000, 6000, 4000]
            self.top_clienti_chart.plot_bar(clienti_labels, clienti_values)
            
            # Evoluzione fatturato
            evoluzione = data.get('evoluzione_fatturato', [])
            if evoluzione:
                self.evoluzione_chart.clear_chart()
                
                mesi = [item['mese'] for item in evoluzione]
                valori = [item['fatturato'] for item in evoluzione]
                
                self.evoluzione_chart.plot_line(mesi, valori, 'Fatturato', '#4caf50')
                
        except Exception as e:
            print(f"Errore nell'aggiornamento dei grafici: {e}")
    
    def update_summary(self, data: Dict[str, Any]):
        """Aggiorna la sezione riassunto."""
        try:
            # Fatture scadute
            fatture_scadute = data.get('fatture_scadute', {})
            numero_scadute = fatture_scadute.get('numero', 0)
            totale_scaduto = fatture_scadute.get('totale', 0)
            
            if numero_scadute > 0:
                scadute_text = f"⚠️ {numero_scadute} fatture scadute per un totale di € {totale_scaduto:,.2f}"
                self.scadute_label.setStyleSheet("color: #f44336; font-weight: bold;")
            else:
                scadute_text = "✅ Nessuna fattura scaduta"
                self.scadute_label.setStyleSheet("color: #4caf50; font-weight: bold;")
            
            self.scadute_label.setText(scadute_text)
            
            # Progress obiettivi (esempio con dati fittizi)
            fatturato_obiettivo = 50000  # Obiettivo mensile
            fatturato_corrente = sum(m['fatturato'] for m in data.get('fatturato_mensile', [])[-1:])
            
            if fatturato_obiettivo > 0:
                percentuale = min(100, (fatturato_corrente / fatturato_obiettivo) * 100)
                self.fatturato_progress.setValue(int(percentuale))
                self.fatturato_progress_label.setText(f"{percentuale:.1f}%")
            
        except Exception as e:
            print(f"Errore nell'aggiornamento del riassunto: {e}")
    
    def export_dashboard(self):
        """Esporta i dati della dashboard."""
        try:
            # Implementazione dell'export - per ora placeholder
            print("Export dashboard non ancora implementato")
        except Exception as e:
            print(f"Errore nell'export della dashboard: {e}")