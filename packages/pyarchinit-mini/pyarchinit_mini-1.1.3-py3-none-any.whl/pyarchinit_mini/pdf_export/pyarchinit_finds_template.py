#!/usr/bin/env python3
"""
PyArchInit Finds Template - Based on original pyarchinit_exp_Findssheet_pdf.py
Provides authentic PyArchInit-style finds PDF generation using single_Finds_pdf_sheet
Fixed version with correct layout and full page usage
"""

import os
from datetime import date, datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, PageBreak, SimpleDocTemplate, Spacer, TableStyle, Image
from reportlab.platypus.paragraph import Paragraph
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from typing import List, Dict, Any
import tempfile


class NumberedCanvasFinds(canvas.Canvas):
    """Canvas with page numbering for finds sheets"""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """Add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 8)
        self.drawRightString(200 * mm, 20 * mm,
                             "Pag. %d di %d" % (self._pageNumber, page_count))


class SingleFindsSheet:
    """Single finds sheet based on PyArchInit original"""
    
    def __init__(self, data_dict, logo_path=None):
        """Initialize with data dictionary and optional logo path"""
        self.logo_path = logo_path
        self.sito = data_dict.get('sito', '')
        self.numero_inventario = data_dict.get('numero_inventario', '')
        self.tipo_reperto = data_dict.get('tipo_reperto', '')
        self.criterio_schedatura = data_dict.get('criterio_raccolta', '') or data_dict.get('criterio_schedatura', '')
        self.definizione = data_dict.get('definizione', '')
        self.descrizione = data_dict.get('descrizione', '')
        self.area = data_dict.get('area', '')
        self.us = data_dict.get('us', '')
        self.lavato = data_dict.get('lavato', '')
        self.nr_cassa = data_dict.get('nr_cassa', '') or data_dict.get('n_cassa', '')
        self.luogo_conservazione = data_dict.get('luogo_conservazione', '')
        self.stato_conservazione = data_dict.get('stato_conservazione', '')
        self.datazione_reperto = data_dict.get('datazione_reperto', '') or data_dict.get('datazione', '')
        self.elementi_reperto = data_dict.get('elementi_reperto', '[]')
        self.misurazioni = data_dict.get('misurazioni', '[]')
        self.rif_biblio = data_dict.get('rif_biblio', '[]') 
        self.tecnologie = data_dict.get('tecnologie', '[]')
        self.tipo = data_dict.get('tipo', '') or data_dict.get('forma', '')
        self.repertato = data_dict.get('repertato', '')
        self.diagnostico = data_dict.get('diagnostico', '')
        self.n_reperto = data_dict.get('n_reperto', '') or data_dict.get('numero_inventario', '')
        self.struttura = data_dict.get('struttura', '')
        self.years = data_dict.get('years', '') or data_dict.get('anno_scavo', '')
        self.thumbnail = data_dict.get('thumbnail', '')
        self.materiale = data_dict.get('materiale', '') or data_dict.get('classe_materiale', '')
        
        # Additional fields
        self.peso = data_dict.get('peso', '')
        self.lunghezza_max = data_dict.get('lunghezza_max', '')
        self.larghezza_max = data_dict.get('larghezza_max', '')
        self.spessore_max = data_dict.get('spessore_max', '')
        self.colore = data_dict.get('colore', '')
        self.consistenza = data_dict.get('consistenza', '')
        
    def datestrfdate(self):
        """Get current date formatted"""
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today
        
    def safe_str(self, value):
        """Safely convert value to string"""
        if value is None or str(value).lower() in ['none', 'null', '[]', '']:
            return ''
        return str(value)
        
    def create_sheet(self):
        """Create the finds sheet following PyArchInit original format exactly"""
        
        # Setup styles exactly like PyArchInit original
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 9
        styNormal.fontName = 'Helvetica'
        
        styDescrizione = styleSheet['Normal'].clone('styDescrizione')
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.alignment = 4  # Justified
        styDescrizione.fontSize = 9
        styDescrizione.fontName = 'Helvetica'
        
        # Header
        intestazione = Paragraph("<b>SCHEDA REPERTI</b>", styNormal)
        
        # Create logo - use provided logo or placeholder
        try:
            if self.logo_path and os.path.exists(self.logo_path):
                logo = Image(self.logo_path)
                logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
                logo.drawWidth = 1.5 * inch
                logo.hAlign = "CENTER"
            else:
                logo = Paragraph("<b>PYARCHINIT</b>", styNormal)
        except:
            logo = Paragraph("<b>PYARCHINIT</b>", styNormal)
        
        # Handle thumbnail
        try:
            if self.thumbnail and os.path.exists(self.thumbnail):
                th = Image(self.thumbnail)
                th.drawHeight = 2.5 * inch * th.drawHeight / th.drawWidth
                th.drawWidth = 2.5 * inch
                th.hAlign = "CENTER"
            else:
                th = Paragraph("<b>IMG</b><br/>" + "Immagine non presente", styNormal)
        except:
            th = Paragraph("<b>IMG</b><br/>" + "Immagine non disponibile", styNormal)
        
        # Data fields following PyArchInit original
        sito = Paragraph("<b>Sito</b><br/>" + self.safe_str(self.sito), styNormal)
        n_reperto = Paragraph("<b>N° reperto</b><br/>" + self.safe_str(self.n_reperto) + 
                             "<br/><b>(n. inv.: </b>" + self.safe_str(self.numero_inventario) + "<b>)</b>", styNormal)
        
        area = Paragraph("<b>Area</b><br/>" + self.safe_str(self.area), styNormal)
        us = Paragraph("<b>US</b><br/>" + self.safe_str(self.us), styNormal)
        anno = Paragraph("<b>Anno</b><br/>" + self.safe_str(self.years), styNormal)
        struttura = Paragraph("<b>Rif. Struttura</b><br/>" + self.safe_str(self.struttura), styNormal)
        
        tipo_reperto = Paragraph("<b>Tipo reperto</b><br/>" + self.safe_str(self.tipo_reperto), styNormal)
        criterio_schedatura = Paragraph("<b>Classe materiale</b><br/>" + self.safe_str(self.materiale), styNormal)
        definizione = Paragraph("<b>Definizione</b><br/>" + self.safe_str(self.definizione), styNormal)
        
        descrizione = Paragraph("<b>Descrizione</b><br/>" + self.safe_str(self.descrizione), styDescrizione)
        
        datazione = Paragraph("<b>Datazione</b><br/>" + self.safe_str(self.datazione_reperto), styNormal)
        stato_conservazione = Paragraph("<b>Stato Conservazione</b><br/>" + self.safe_str(self.stato_conservazione), styNormal)
        
        # Build measurements text
        measurements_text = ""
        if self.peso:
            measurements_text += f"Peso: {self.peso}g"
        if self.lunghezza_max:
            if measurements_text: measurements_text += "<br/>"
            measurements_text += f"Lunghezza: {self.lunghezza_max}cm"
        if self.larghezza_max:
            if measurements_text: measurements_text += "<br/>"
            measurements_text += f"Larghezza: {self.larghezza_max}cm"
        if self.spessore_max:
            if measurements_text: measurements_text += "<br/>"
            measurements_text += f"Spessore: {self.spessore_max}cm"
            
        misurazioni = Paragraph("<b>Misurazioni</b><br/>" + measurements_text, styNormal)
        
        # Material properties combined
        material_text = ""
        if self.materiale:
            material_text += f"<b>Materiale</b><br/>{self.safe_str(self.materiale)}"
        if self.colore:
            if material_text: material_text += "<br/>"
            material_text += f"<b>Colore</b><br/>{self.safe_str(self.colore)}"
        if self.consistenza:
            if material_text: material_text += "<br/>"
            material_text += f"<b>Consistenza</b><br/>{self.safe_str(self.consistenza)}"
        material_combined = Paragraph(material_text, styNormal)
        
        tipologia = Paragraph("<b>Tipologia</b><br/>" + self.safe_str(self.tipo), styNormal)
        
        # Additional fields matching the original
        elementi_reperto = Paragraph("<b>Elementi reperto</b><br/>" + self.safe_str(self.elementi_reperto), styNormal)
        tecnologie = Paragraph("<b>Tecnologie</b><br/>" + self.safe_str(self.tecnologie), styNormal)
        
        repertato = Paragraph("<b>Repertato</b><br/>" + self.safe_str(self.repertato), styNormal)
        diagnostico = Paragraph("<b>Diagnostico</b><br/>" + self.safe_str(self.diagnostico), styNormal)
        
        lavato = Paragraph("<b>Lavato</b><br/>" + self.safe_str(self.lavato), styNormal)
        nr_cassa = Paragraph("<b>N° cassa</b><br/>" + self.safe_str(self.nr_cassa), styNormal)
        luogo_conservazione = Paragraph("<b>Luogo di conservazione</b><br/>" + self.safe_str(self.luogo_conservazione), styNormal)
        
        # Bibliografia per il footer
        bibliografia_text = ""
        # Handle bibliography references
        if hasattr(self, 'rif_biblio') and self.rif_biblio and self.rif_biblio != '[]':
            try:
                import ast
                bibliografia_refs = ast.literal_eval(str(self.rif_biblio))
                if isinstance(bibliografia_refs, list) and bibliografia_refs:
                    bib_entries = []
                    for ref in bibliografia_refs:
                        if isinstance(ref, dict):
                            author = ref.get('autore', '')
                            anno = ref.get('anno', '')
                            titolo = ref.get('titolo', '')
                            pagine = ref.get('pagine', '')
                            figure = ref.get('figure', '')
                            entry = f"Autore: {author}, Anno: {anno}, Titolo: {titolo}"
                            if pagine:
                                entry += f", Pag.: {pagine}"
                            if figure:
                                entry += f", Fig.: {figure}"
                            bib_entries.append(entry)
                    bibliografia_text = "<br/>".join(bib_entries)
            except:
                bibliografia_text = str(self.rif_biblio) if self.rif_biblio != '[]' else ""
        
        bibliografia = Paragraph("<b>Riferimenti bibliografici</b><br/>" + bibliografia_text, styNormal)

        # Create table schema following PyArchInit original layout exactly
        cell_schema = [
            # Row 0 - Header with logo on the right
            [intestazione, '', '', '', '', '', '', '', '', logo, '', '', '', '', '', '', '', ''],
            # Row 1 - Site and find number with image on the right
            [sito, '', '', '', '', n_reperto, '', '', '' , '', '', th, '', '', '', '', '', ''],
            # Row 2 - Stratigraphic context
            [area, '', us, '', anno, '', struttura, '', '', '', '', '', '', '', '', '', '', ''],
            # Row 3 - Find type
            [tipo_reperto, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
            # Row 4 - Material class
            [criterio_schedatura, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
            # Row 5 - Definition
            [definizione, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
            # Row 6 - Description (large area spanning multiple rows)
            [descrizione, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
            # Row 7-9 - Continuation of description area
            ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
            # Row 10 - Dating and conservation
            [datazione, '', '', '', stato_conservazione, '', '', '', '', '', '', '', '', '', '', '', '', ''],
            # Row 11 - Elements
            [elementi_reperto, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
            # Row 12 - Measurements
            [misurazioni, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
            # Row 13 - Technologies and typology
            [tecnologie, '', '', '', '', '', '', '', tipologia, '', '', '', '', '', '', '', '', ''],
            # Row 14 - Archive info
            [repertato, '', diagnostico, '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
            # Row 15 - Storage
            [lavato, '', nr_cassa, '', '', luogo_conservazione, '', '', '', '', '', '', '', '', '', '', '', ''],
            # Row 16 - Bibliography
            [bibliografia, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
        ]
        
        # Table style following PyArchInit original exactly
        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            
            # Row 0 - Header
            ('SPAN', (0, 0), (8, 0)),  # Title "SCHEDA REPERTI"
            ('SPAN', (9, 0), (17, 0)),  # Logo space
            ('VALIGN', (0, 0), (8, 0), 'MIDDLE'),
            ('VALIGN', (9, 0), (17, 0), 'MIDDLE'),
            ('ALIGN', (9, 0), (17, 0), 'CENTER'),
            
            # Row 1 - Site and find number with image
            ('SPAN', (0, 1), (4, 1)),  # Sito
            ('SPAN', (5, 1), (10, 1)),  # N° reperto (n. inv.: xxx)
            ('SPAN', (11, 1), (17, 2)),  # IMG - Image area  
            ('VALIGN', (0, 1), (10, 1), 'TOP'),
            ('VALIGN', (11, 1), (17, 2), 'MIDDLE'),
            ('ALIGN', (11, 1), (17, 2), 'CENTER'),
            
            # Row 2 - Stratigraphic context
            ('SPAN', (0, 2), (1, 2)),  # Area
            ('SPAN', (2, 2), (3, 2)),  # US
            ('SPAN', (4, 2), (5, 2)),  # Anno
            ('SPAN', (6, 2), (10, 2)),  # Rif. Struttura
            ('VALIGN', (0, 2), (10, 2), 'TOP'),
            
            # Row 3 - Tipo reperto (full width)
            ('SPAN', (0, 3), (17, 3)),  # Tipo reperto
            
            # Row 4 - Classe materiale (full width)
            ('SPAN', (0, 4), (17, 4)),  # Classe materiale
            
            # Row 5 - Definizione (full width) 
            ('SPAN', (0, 5), (17, 5)),  # Definizione
            
            # Row 6-9 - Descrizione (large area spanning multiple rows)
            ('SPAN', (0, 6), (17, 9)),  # Descrizione
            ('VALIGN', (0, 6), (17, 9), 'TOP'),
            
            # Row 10 - Datazione and Stato Conservazione
            ('SPAN', (0, 10), (3, 10)),  # Datazione
            ('SPAN', (4, 10), (17, 10)),  # Stato Conservazione
            
            # Row 11 - Elementi reperto (full width)
            ('SPAN', (0, 11), (17, 11)),  # Elementi reperto
            
            # Row 12 - Misurazioni (full width)
            ('SPAN', (0, 12), (17, 12)),  # Misurazioni
            
            # Row 13 - Tecnologie and Tipologia
            ('SPAN', (0, 13), (7, 13)),  # Tecnologie
            ('SPAN', (8, 13), (17, 13)),  # Tipologia
            
            # Row 14 - Repertato and Diagnostico
            ('SPAN', (0, 14), (2, 14)),  # Repertato
            ('SPAN', (3, 14), (17, 14)),  # Diagnostico
            
            # Row 15 - Storage info
            ('SPAN', (0, 15), (1, 15)),  # Lavato
            ('SPAN', (2, 15), (4, 15)),  # N° cassa
            ('SPAN', (5, 15), (17, 15)),  # Luogo di conservazione
            
            # Row 16 - Bibliografia (full width)
            ('SPAN', (0, 16), (17, 16)),  # Riferimenti bibliografici
            
            # Set alignment for all cells
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT')
        ]
        
        # Column widths exactly like PyArchInit original (scaled for A4)
        colWidths = (15, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 20, 30, 30, 30, 30, 30)
        rowHeights = [30, 40, 30, 30, 30, 30, 130, 30, 30, 30, 30, 30, 30, 30, 30, 30, 40]  # Added row for bibliography
        
        # Create table
        table = Table(cell_schema, colWidths=colWidths, rowHeights=rowHeights)
        table.setStyle(TableStyle(table_style))
        
        return table


class PyArchInitFindsTemplate:
    """PyArchInit finds template manager"""
    
    def __init__(self):
        pass
        
    def generate_finds_sheets(self, finds_list: List[Dict[str, Any]], 
                            output_path: str, site_name: str = "", logo_path: str = None) -> str:
        """
        Generate finds sheets in authentic PyArchInit format
        
        Args:
            finds_list: List of find dictionaries
            output_path: Output PDF path
            site_name: Site name for header
            
        Returns:
            Output path if successful
        """
        try:
            # Create document with full page usage
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=10*mm,  # Smaller margins for full page usage
                leftMargin=10*mm,
                topMargin=10*mm,
                bottomMargin=15*mm,
                canvasmaker=NumberedCanvasFinds
            )
            
            # Build story
            story = []
            
            for i, find_data in enumerate(finds_list):
                # Create finds sheet with logo
                sheet = SingleFindsSheet(find_data, logo_path)
                finds_table = sheet.create_sheet()
                story.append(finds_table)
                
                # Add page break between finds (except for last)
                if i < len(finds_list) - 1:
                    story.append(PageBreak())
            
            # Build PDF
            doc.build(story)
            
            return output_path
            
        except Exception as e:
            print(f"Error generating finds sheets: {e}")
            import traceback
            traceback.print_exc()
            return None