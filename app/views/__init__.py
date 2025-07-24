"""
Views Package
=============

Contiene tutte le viste GUI dell'applicazione di contabilità.
"""

from .main_window import MainWindow
from .dashboard_widget import DashboardWidget
from .anagrafiche_widget import AnagraficheWidget
from .documenti_widget import DocumentiWidget
from .contabilita_widget import ContabilitaWidget
from .report_widget import ReportWidget

__all__ = [
    "MainWindow",
    "DashboardWidget",
    "AnagraficheWidget", 
    "DocumentiWidget",
    "ContabilitaWidget",
    "ReportWidget"
]