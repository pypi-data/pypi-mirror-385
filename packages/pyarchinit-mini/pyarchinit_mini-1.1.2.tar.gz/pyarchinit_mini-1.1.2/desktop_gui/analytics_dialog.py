"""
Analytics Dashboard Dialog for Desktop GUI

Displays charts and statistics using matplotlib.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class AnalyticsDialog:
    """Analytics dashboard dialog with matplotlib charts"""

    def __init__(self, parent, db_manager):
        """
        Initialize analytics dialog

        Args:
            parent: Parent window
            db_manager: Database manager instance
        """
        self.parent = parent
        self.db_manager = db_manager

        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Analytics Dashboard")
        self.dialog.geometry("1200x800")

        # Import AnalyticsService
        from pyarchinit_mini.services.analytics_service import AnalyticsService
        self.analytics_service = AnalyticsService(db_manager)

        # Create UI
        self.create_widgets()

        # Load data and draw charts
        self.load_analytics()

    def create_widgets(self):
        """Create UI widgets"""
        # Main container with scrollbar
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas for scrolling
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Title
        title_label = ttk.Label(
            self.scrollable_frame,
            text="Dashboard Analytics",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)

        # Overview stats frame
        self.stats_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="Statistiche Generali",
            padding=10
        )
        self.stats_frame.pack(fill=tk.X, padx=10, pady=5)

        # Chart frames (will be filled dynamically)
        self.charts_frame = ttk.Frame(self.scrollable_frame)
        self.charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Close button
        close_btn = ttk.Button(
            self.scrollable_frame,
            text="Chiudi",
            command=self.dialog.destroy
        )
        close_btn.pack(pady=10)

    def load_analytics(self):
        """Load analytics data and create charts"""
        try:
            # Get all analytics data
            data = self.analytics_service.get_complete_dashboard_data()

            # Display overview stats
            self.display_overview_stats(data['overview'])

            # Create charts
            self.create_charts(data)

        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento analytics: {str(e)}")

    def display_overview_stats(self, overview):
        """Display overview statistics"""
        stats_text = f"""
        Siti Totali: {overview['total_sites']}
        US Totali: {overview['total_us']}
        Reperti Totali: {overview['total_inventario']}
        Regioni: {overview['total_regions']}
        Province: {overview['total_provinces']}
        """

        label = ttk.Label(self.stats_frame, text=stats_text, font=("Arial", 12))
        label.pack()

    def create_charts(self, data):
        """Create all matplotlib charts"""
        # Create figure with multiple subplots
        fig = Figure(figsize=(12, 16), dpi=100)

        # Chart 1: Sites by Region (Pie)
        if data['sites_by_region']:
            ax1 = fig.add_subplot(4, 2, 1)
            labels = list(data['sites_by_region'].keys())
            values = list(data['sites_by_region'].values())
            ax1.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
            ax1.set_title('Siti per Regione')

        # Chart 2: Sites by Province (Bar)
        if data['sites_by_province']:
            ax2 = fig.add_subplot(4, 2, 2)
            labels = list(data['sites_by_province'].keys())
            values = list(data['sites_by_province'].values())
            ax2.barh(labels, values, color='#2E86AB')
            ax2.set_xlabel('Numero Siti')
            ax2.set_title('Siti per Provincia (Top 10)')
            ax2.grid(axis='x', alpha=0.3)

        # Chart 3: US by Period (Bar)
        if data['us_by_period']:
            ax3 = fig.add_subplot(4, 2, 3)
            labels = list(data['us_by_period'].keys())
            values = list(data['us_by_period'].values())
            ax3.bar(labels, values, color='#A23B72')
            ax3.set_ylabel('Numero US')
            ax3.set_title('US per Periodo Cronologico')
            ax3.tick_params(axis='x', rotation=45)
            ax3.grid(axis='y', alpha=0.3)

        # Chart 4: US by Type (Pie)
        if data['us_by_type']:
            ax4 = fig.add_subplot(4, 2, 4)
            labels = list(data['us_by_type'].keys())
            values = list(data['us_by_type'].values())
            ax4.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
            ax4.set_title('US per Tipologia')

        # Chart 5: Inventario by Type (Bar)
        if data['inventario_by_type']:
            ax5 = fig.add_subplot(4, 2, 5)
            labels = list(data['inventario_by_type'].keys())
            values = list(data['inventario_by_type'].values())
            ax5.barh(labels, values, color='#F18F01')
            ax5.set_xlabel('Numero Reperti')
            ax5.set_title('Reperti per Tipologia (Top 10)')
            ax5.grid(axis='x', alpha=0.3)

        # Chart 6: Inventario by Conservation (Pie)
        if data['inventario_by_conservation']:
            ax6 = fig.add_subplot(4, 2, 6)
            labels = list(data['inventario_by_conservation'].keys())
            values = list(data['inventario_by_conservation'].values())
            colors = ['#6A994E', '#BC4B51', '#5B8E7D', '#8B5A3C']
            ax6.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
            ax6.set_title('Reperti per Stato di Conservazione')

        # Chart 7: US by Site (Bar)
        if data['us_by_site']:
            ax7 = fig.add_subplot(4, 2, 7)
            labels = list(data['us_by_site'].keys())
            values = list(data['us_by_site'].values())
            ax7.bar(labels, values, color='#6D597A')
            ax7.set_ylabel('Numero US')
            ax7.set_title('US per Sito (Top 10)')
            ax7.tick_params(axis='x', rotation=45)
            ax7.grid(axis='y', alpha=0.3)

        # Chart 8: Inventario by Site (Bar)
        if data['inventario_by_site']:
            ax8 = fig.add_subplot(4, 2, 8)
            labels = list(data['inventario_by_site'].keys())
            values = list(data['inventario_by_site'].values())
            ax8.bar(labels, values, color='#B56576')
            ax8.set_ylabel('Numero Reperti')
            ax8.set_title('Reperti per Sito (Top 10)')
            ax8.tick_params(axis='x', rotation=45)
            ax8.grid(axis='y', alpha=0.3)

        # Adjust layout
        fig.tight_layout(pad=3.0)

        # Embed matplotlib figure in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add matplotlib toolbar
        toolbar = NavigationToolbar2Tk(canvas, self.charts_frame)
        toolbar.update()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def show_analytics_dialog(parent, db_manager):
    """
    Show analytics dashboard dialog

    Args:
        parent: Parent window
        db_manager: Database manager instance
    """
    AnalyticsDialog(parent, db_manager)
