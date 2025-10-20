#!/usr/bin/env python3
"""
PyArchInit Inventory Template - Based on original pyarchinit_exp_Invlapsheet_pdf.py
Provides authentic PyArchInit-style inventory PDF generation
"""

from datetime import date, datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A3, A5
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, PageBreak, SimpleDocTemplate, Spacer, TableStyle, Image
from reportlab.platypus.paragraph import Paragraph
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from typing import List, Dict, Any
import os


class PyArchInitInventoryTemplate:
    """
    Authentic PyArchInit inventory template following the original design
    """
    
    def __init__(self):
        self.setup_styles()
    
    def setup_styles(self):
        """Setup PyArchInit specific styles"""
        self.styles = getSampleStyleSheet()
        
        # PyArchInit title style
        self.styles.add(ParagraphStyle(
            'PyArchInitTitle',
            parent=self.styles['Title'],
            fontSize=16,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            spaceAfter=30,
            textColor=colors.black
        ))
        
        # Field label style (small, bold)
        self.styles.add(ParagraphStyle(
            'PyArchInitLabel',
            fontSize=7,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            leading=8,
            textColor=colors.black
        ))
        
        # Field value style
        self.styles.add(ParagraphStyle(
            'PyArchInitValue',
            fontSize=8,
            fontName='Helvetica',
            alignment=TA_LEFT,
            leading=9,
            textColor=colors.black
        ))
        
        # Large number style for inventory number
        self.styles.add(ParagraphStyle(
            'PyArchInitBigNum',
            fontSize=12,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            textColor=colors.black
        ))
        
        # Description text
        self.styles.add(ParagraphStyle(
            'PyArchInitDescription',
            fontSize=8,
            fontName='Helvetica',
            alignment=TA_LEFT,
            leading=10
        ))
    
    def generate_inventory_sheets(self, inventario_list: List[Dict[str, Any]], 
                                output_path: str, site_name: str = "") -> str:
        """
        Generate inventory sheets in authentic PyArchInit A5 format
        
        Args:
            inventario_list: List of inventory items
            output_path: Output file path
            site_name: Site name for header
            
        Returns:
            Generated file path
        """
        
        # Create document with A5 size like original PyArchInit
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A5,
            rightMargin=0.5*cm,
            leftMargin=0.5*cm,
            topMargin=0.5*cm,
            bottomMargin=0.5*cm
        )
        
        story = []
        
        def safe_str(value):
            """Safely convert value to string"""
            if value is None:
                return ""
            return str(value)
        
        # Generate individual inventory sheets
        for i, inv_data in enumerate(inventario_list):
            if i > 0:
                story.append(PageBreak())
            
            # Sheet header with site info
            if site_name:
                header_table = Table([
                    [Paragraph(f"<b>SCHEDA INVENTARIO - {site_name.upper()}</b>", 
                              self.styles['PyArchInitTitle'])],
                ], colWidths=[A5[0] - 1*cm])
                
                header_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey)
                ]))
                story.append(header_table)
                story.append(Spacer(1, 3*mm))
            
            # Main inventory number box
            num_inventario = safe_str(inv_data.get('numero_inventario', ''))
            
            # Context information section
            today = datetime.now().strftime("%d/%m/%Y")
            us_str = safe_str(inv_data.get('us', ''))
            area_str = safe_str(inv_data.get('area', ''))
            sito_str = safe_str(inv_data.get('sito', site_name))
            
            context_data = [
                [Paragraph("<b>N° INVENTARIO</b>", self.styles['PyArchInitLabel']),
                 Paragraph(f"<b>{num_inventario}</b>", self.styles['PyArchInitBigNum'])],
                [Paragraph("<b>DATA</b>", self.styles['PyArchInitLabel']),
                 Paragraph(today, self.styles['PyArchInitValue'])],
                [Paragraph("<b>SITO</b>", self.styles['PyArchInitLabel']),
                 Paragraph(sito_str, self.styles['PyArchInitValue'])],
                [Paragraph("<b>AREA</b>", self.styles['PyArchInitLabel']),
                 Paragraph(area_str, self.styles['PyArchInitValue'])],
                [Paragraph("<b>US</b>", self.styles['PyArchInitLabel']),
                 Paragraph(us_str, self.styles['PyArchInitValue'])],
            ]
            
            context_table = Table(context_data, colWidths=[3*cm, 4*cm])
            context_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey)
            ]))
            
            story.append(context_table)
            story.append(Spacer(1, 3*mm))
            
            # Object classification section
            classification_data = [
                [Paragraph("<b>TIPO REPERTO</b>", self.styles['PyArchInitLabel']),
                 Paragraph(safe_str(inv_data.get('tipo_reperto', '')), self.styles['PyArchInitValue'])],
                [Paragraph("<b>DEFINIZIONE</b>", self.styles['PyArchInitLabel']),
                 Paragraph(safe_str(inv_data.get('definizione', '')), self.styles['PyArchInitValue'])],
                [Paragraph("<b>CRITERIO DI RACCOLTA</b>", self.styles['PyArchInitLabel']),
                 Paragraph(safe_str(inv_data.get('criterio_raccolta', '')), self.styles['PyArchInitValue'])],
                [Paragraph("<b>MATERIALE</b>", self.styles['PyArchInitLabel']),
                 Paragraph(safe_str(inv_data.get('materiale', '')), self.styles['PyArchInitValue'])],
            ]
            
            classification_table = Table(classification_data, colWidths=[3*cm, 4*cm])
            classification_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey)
            ]))
            
            story.append(classification_table)
            story.append(Spacer(1, 3*mm))
            
            # Physical characteristics
            physical_data = [
                [Paragraph("<b>LUNGHEZZA (cm)</b>", self.styles['PyArchInitLabel']),
                 Paragraph(safe_str(inv_data.get('lunghezza_max', '')), self.styles['PyArchInitValue'])],
                [Paragraph("<b>LARGHEZZA (cm)</b>", self.styles['PyArchInitLabel']),
                 Paragraph(safe_str(inv_data.get('larghezza_max', '')), self.styles['PyArchInitValue'])],
                [Paragraph("<b>SPESSORE (cm)</b>", self.styles['PyArchInitLabel']),
                 Paragraph(safe_str(inv_data.get('spessore_max', '')), self.styles['PyArchInitValue'])],
                [Paragraph("<b>PESO (g)</b>", self.styles['PyArchInitLabel']),
                 Paragraph(safe_str(inv_data.get('peso', '')), self.styles['PyArchInitValue'])],
            ]
            
            physical_table = Table(physical_data, colWidths=[3*cm, 4*cm])
            physical_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey)
            ]))
            
            story.append(physical_table)
            story.append(Spacer(1, 3*mm))
            
            # Conservation and technical data
            conservation_data = [
                [Paragraph("<b>STATO CONSERVAZIONE</b>", self.styles['PyArchInitLabel']),
                 Paragraph(safe_str(inv_data.get('stato_conservazione', '')), self.styles['PyArchInitValue'])],
                [Paragraph("<b>COLORE</b>", self.styles['PyArchInitLabel']),
                 Paragraph(safe_str(inv_data.get('colore', '')), self.styles['PyArchInitValue'])],
                [Paragraph("<b>CONSISTENZA</b>", self.styles['PyArchInitLabel']),
                 Paragraph(safe_str(inv_data.get('consistenza', '')), self.styles['PyArchInitValue'])],
                [Paragraph("<b>FORMA</b>", self.styles['PyArchInitLabel']),
                 Paragraph(safe_str(inv_data.get('forma', '')), self.styles['PyArchInitValue'])],
            ]
            
            conservation_table = Table(conservation_data, colWidths=[3*cm, 4*cm])
            conservation_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey)
            ]))
            
            story.append(conservation_table)
            story.append(Spacer(1, 3*mm))
            
            # Description and notes section
            descrizione = safe_str(inv_data.get('descrizione', ''))
            osservazioni = safe_str(inv_data.get('osservazioni', ''))
            
            if descrizione or osservazioni:
                desc_data = []
                if descrizione:
                    desc_data.append([Paragraph("<b>DESCRIZIONE</b>", self.styles['PyArchInitLabel']),
                                    Paragraph(descrizione, self.styles['PyArchInitDescription'])])
                if osservazioni:
                    desc_data.append([Paragraph("<b>OSSERVAZIONI</b>", self.styles['PyArchInitLabel']),
                                    Paragraph(osservazioni, self.styles['PyArchInitDescription'])])
                
                if desc_data:
                    desc_table = Table(desc_data, colWidths=[3*cm, 4*cm])
                    desc_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey)
                    ]))
                    
                    story.append(desc_table)
        
        # Build the PDF
        doc.build(story)
        return output_path
    
    def generate_inventory_catalog(self, inventario_list: List[Dict[str, Any]], 
                                 output_path: str, site_name: str = "") -> str:
        """
        Generate inventory catalog (summary table) in A4 format
        
        Args:
            inventario_list: List of inventory items
            output_path: Output file path 
            site_name: Site name for header
            
        Returns:
            Generated file path
        """
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # Title
        title = f"CATALOGO INVENTARIO MATERIALI{' - ' + site_name.upper() if site_name else ''}"
        story.append(Paragraph(title, self.styles['PyArchInitTitle']))
        story.append(Spacer(1, 1*cm))
        
        # Summary statistics
        total_items = len(inventario_list)
        ceramics = len([x for x in inventario_list if x.get('tipo_reperto', '').lower() == 'ceramica'])
        metals = len([x for x in inventario_list if x.get('tipo_reperto', '').lower() == 'metallo'])
        
        stats_data = [
            ['TOTALE REPERTI', str(total_items)],
            ['CERAMICHE', str(ceramics)],
            ['METALLI', str(metals)],
            ['ALTRI', str(total_items - ceramics - metals)]
        ]
        
        stats_table = Table(stats_data, colWidths=[5*cm, 3*cm])
        stats_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold')
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 1*cm))
        
        # Main catalog table
        table_data = [['N. INV.', 'TIPO', 'DEFINIZIONE', 'MATERIALE', 'US/AREA', 'STATO', 'PESO']]
        
        for inv in inventario_list:
            row = [
                str(inv.get('numero_inventario', '')),
                str(inv.get('tipo_reperto', '')),
                str(inv.get('definizione', ''))[:20] + ('...' if len(str(inv.get('definizione', ''))) > 20 else ''),
                str(inv.get('materiale', '')),
                f"{inv.get('us', '')}/{inv.get('area', '')}",
                str(inv.get('stato_conservazione', ''))[:10],
                str(inv.get('peso', '')) + 'g' if inv.get('peso') else ''
            ]
            table_data.append(row)
        
        # Create table with appropriate column widths
        catalog_table = Table(table_data, colWidths=[2*cm, 2*cm, 4*cm, 2*cm, 2*cm, 2*cm, 1.5*cm])
        catalog_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        story.append(catalog_table)
        
        # Build PDF
        doc.build(story)
        return output_path