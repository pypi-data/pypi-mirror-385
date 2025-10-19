"""
PDF generation for archaeological reports
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io
import os
import base64
from typing import List, Dict, Any, Optional

class PDFGenerator:
    """
    Generate PDF reports for archaeological data
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=6,
            spaceBefore=12,
            textColor=colors.black,
            backColor=colors.lightgrey
        ))
        
        # Field label
        self.styles.add(ParagraphStyle(
            name='FieldLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.darkblue,
            leftIndent=10
        ))
        
        # Field value
        self.styles.add(ParagraphStyle(
            name='FieldValue',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20
        ))
    
    def generate_site_report(self, site_data: Dict[str, Any], 
                           us_list: List[Dict[str, Any]] = None,
                           inventory_list: List[Dict[str, Any]] = None,
                           media_list: List[Dict[str, Any]] = None,
                           output_path: Optional[str] = None) -> bytes:
        """
        Generate comprehensive site report
        
        Args:
            site_data: Site information
            us_list: List of stratigraphic units
            inventory_list: List of inventory items
            media_list: List of media files
            output_path: Optional output file path
            
        Returns:
            PDF bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer if not output_path else output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # Title page
        story.extend(self._create_title_page(site_data))
        story.append(PageBreak())
        
        # Site information
        story.extend(self._create_site_section(site_data))
        
        # US section
        if us_list:
            story.append(PageBreak())
            story.extend(self._create_us_section(us_list))
        
        # Inventory section
        if inventory_list:
            story.append(PageBreak())
            story.extend(self._create_inventory_section(inventory_list))
        
        # Media section
        if media_list:
            story.append(PageBreak())
            story.extend(self._create_media_section(media_list))
        
        # Build PDF
        doc.build(story)
        
        # Always return bytes regardless of output_path
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
    
    def _create_title_page(self, site_data: Dict[str, Any]) -> List:
        """Create title page"""
        elements = []
        
        # Main title
        title = f"Relazione Archeologica\\n{site_data.get('sito', 'Sito Archeologico')}"
        elements.append(Paragraph(title, self.styles['CustomTitle']))
        elements.append(Spacer(1, 2*inch))
        
        # Site details table
        site_info = [
            ['Sito:', site_data.get('sito', 'N/A')],
            ['Comune:', site_data.get('comune', 'N/A')],
            ['Provincia:', site_data.get('provincia', 'N/A')],
            ['Regione:', site_data.get('regione', 'N/A')],
            ['Nazione:', site_data.get('nazione', 'N/A')],
            ['Definizione:', site_data.get('definizione_sito', 'N/A')]
        ]
        
        site_table = Table(site_info, colWidths=[3*cm, 8*cm])
        site_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey)
        ]))
        
        elements.append(site_table)
        elements.append(Spacer(1, 2*inch))
        
        # Date and signature
        date_str = datetime.now().strftime("%d/%m/%Y")
        elements.append(Paragraph(f"Data: {date_str}", self.styles['Normal']))
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("Generato da PyArchInit-Mini", self.styles['Normal']))
        
        return elements
    
    def _create_site_section(self, site_data: Dict[str, Any]) -> List:
        """Create site information section"""
        elements = []
        
        elements.append(Paragraph("1. INFORMAZIONI SITO", self.styles['Subtitle']))
        
        # Location section
        elements.append(Paragraph("1.1 Localizzazione", self.styles['SectionHeader']))
        
        location_fields = [
            ('Nome Sito', site_data.get('sito', '')),
            ('Comune', site_data.get('comune', '')),
            ('Provincia', site_data.get('provincia', '')),
            ('Regione', site_data.get('regione', '')),
            ('Nazione', site_data.get('nazione', ''))
        ]
        
        for label, value in location_fields:
            if value:
                elements.append(Paragraph(f"<b>{label}:</b> {value}", self.styles['FieldLabel']))
        
        # Description section
        if site_data.get('descrizione'):
            elements.append(Spacer(1, 0.3*inch))
            elements.append(Paragraph("1.2 Descrizione", self.styles['SectionHeader']))
            elements.append(Paragraph(site_data['descrizione'], self.styles['Normal']))
        
        # Site definition
        if site_data.get('definizione_sito'):
            elements.append(Spacer(1, 0.3*inch))
            elements.append(Paragraph("1.3 Definizione Sito", self.styles['SectionHeader']))
            elements.append(Paragraph(site_data['definizione_sito'], self.styles['Normal']))
        
        return elements
    
    def _create_us_section(self, us_list: List[Dict[str, Any]]) -> List:
        """Create stratigraphic units section"""
        elements = []
        
        elements.append(Paragraph("2. UNITÀ STRATIGRAFICHE", self.styles['Subtitle']))
        
        # Summary table
        elements.append(Paragraph("2.1 Elenco US", self.styles['SectionHeader']))
        
        # Create table data
        table_data = [['US', 'Area', 'Descrizione Stratigrafica', 'Interpretazione', 'Anno Scavo']]
        
        for us in us_list:
            # Safe string handling
            d_strat = us.get('d_stratigrafica') or ''
            d_interp = us.get('d_interpretativa') or ''
            
            row = [
                str(us.get('us', '')),
                us.get('area', '') or '',
                d_strat[:50] + '...' if len(d_strat) > 50 else d_strat,
                d_interp[:40] + '...' if len(d_interp) > 40 else d_interp,
                str(us.get('anno_scavo', '') or '')
            ]
            table_data.append(row)
        
        us_table = Table(table_data, colWidths=[1.5*cm, 1.5*cm, 5*cm, 4*cm, 2*cm])
        us_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        elements.append(us_table)
        
        # Detailed US descriptions
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("2.2 Descrizioni Dettagliate", self.styles['SectionHeader']))
        
        for us in us_list[:10]:  # Limit to first 10 for space
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph(f"<b>US {us.get('us', 'N/A')} - Area {us.get('area', 'N/A')}</b>", 
                                    self.styles['FieldLabel']))
            
            if us.get('d_stratigrafica'):
                elements.append(Paragraph(f"<b>Descrizione:</b> {us['d_stratigrafica']}", 
                                        self.styles['Normal']))
            
            if us.get('d_interpretativa'):
                elements.append(Paragraph(f"<b>Interpretazione:</b> {us['d_interpretativa']}", 
                                        self.styles['Normal']))
        
        return elements
    
    def _create_inventory_section(self, inventory_list: List[Dict[str, Any]]) -> List:
        """Create inventory section"""
        elements = []
        
        elements.append(Paragraph("3. INVENTARIO MATERIALI", self.styles['Subtitle']))
        
        # Summary statistics
        total_items = len(inventory_list)
        ceramic_count = len([item for item in inventory_list if item.get('tipo_reperto') == 'Ceramica'])
        metal_count = len([item for item in inventory_list if item.get('tipo_reperto') == 'Metallo'])
        
        elements.append(Paragraph("3.1 Statistiche", self.styles['SectionHeader']))
        elements.append(Paragraph(f"Totale reperti catalogati: {total_items}", self.styles['Normal']))
        elements.append(Paragraph(f"Materiali ceramici: {ceramic_count}", self.styles['Normal']))
        elements.append(Paragraph(f"Materiali metallici: {metal_count}", self.styles['Normal']))
        
        # Inventory table
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("3.2 Elenco Reperti", self.styles['SectionHeader']))
        
        table_data = [['N. Inv.', 'Tipo', 'Definizione', 'Area/US', 'Peso (g)', 'Stato']]
        
        for item in inventory_list[:20]:  # Limit for space
            row = [
                str(item.get('numero_inventario', '')),
                item.get('tipo_reperto', ''),
                item.get('definizione', ''),
                f"{item.get('area', '')}/{item.get('us', '')}",
                str(item.get('peso', '')) if item.get('peso') else '',
                item.get('stato_conservazione', '')
            ]
            table_data.append(row)
        
        inv_table = Table(table_data, colWidths=[2*cm, 2*cm, 3*cm, 2*cm, 1.5*cm, 3*cm])
        inv_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(inv_table)
        
        return elements
    
    def _create_media_section(self, media_list: List[Dict[str, Any]]) -> List:
        """Create media documentation section"""
        elements = []
        
        elements.append(Paragraph("4. DOCUMENTAZIONE FOTOGRAFICA", self.styles['Subtitle']))
        
        # Media statistics
        total_media = len(media_list)
        images = [m for m in media_list if m.get('media_type') == 'image']
        documents = [m for m in media_list if m.get('media_type') == 'document']
        
        elements.append(Paragraph(f"Totale file media: {total_media}", self.styles['Normal']))
        elements.append(Paragraph(f"Immagini: {len(images)}", self.styles['Normal']))
        elements.append(Paragraph(f"Documenti: {len(documents)}", self.styles['Normal']))
        
        # Media table
        if media_list:
            elements.append(Spacer(1, 0.3*inch))
            elements.append(Paragraph("4.1 Elenco Media", self.styles['SectionHeader']))
            
            table_data = [['Nome File', 'Tipo', 'Entità', 'Descrizione', 'Autore']]
            
            for media in media_list[:15]:  # Limit for space
                row = [
                    media.get('media_name', ''),
                    media.get('media_type', ''),
                    f"{media.get('entity_type', '')}:{media.get('entity_id', '')}",
                    (media.get('description', '')[:40] + '...') if len(media.get('description', '')) > 40 else media.get('description', ''),
                    media.get('author', '')
                ]
                table_data.append(row)
            
            media_table = Table(table_data, colWidths=[4*cm, 2*cm, 2*cm, 4*cm, 2*cm])
            media_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightyellow),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            elements.append(media_table)
        
        return elements
    
    def generate_harris_matrix_report(self, site_name: str, matrix_image_path: str,
                                    relationships: List[Dict[str, Any]],
                                    statistics: Dict[str, Any],
                                    output_path: Optional[str] = None) -> bytes:
        """Generate Harris Matrix documentation report"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer if not output_path else output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # Title
        story.append(Paragraph(f"Harris Matrix - {site_name}", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*inch))
        
        # Statistics
        story.append(Paragraph("Statistiche Matrix", self.styles['Subtitle']))
        stats_data = [
            ['Totale US:', str(statistics.get('total_us', 0))],
            ['Relazioni:', str(statistics.get('total_relationships', 0))],
            ['Livelli:', str(statistics.get('levels', 0))],
            ['Matrix Valida:', 'Sì' if statistics.get('is_valid', False) else 'No'],
            ['US Isolate:', str(statistics.get('isolated_us', 0))]
        ]
        
        stats_table = Table(stats_data, colWidths=[4*cm, 3*cm])
        stats_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold')
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Matrix image
        if matrix_image_path and os.path.exists(matrix_image_path):
            story.append(Paragraph("Diagramma Harris Matrix", self.styles['Subtitle']))
            matrix_img = Image(matrix_image_path, width=15*cm, height=10*cm)
            story.append(matrix_img)
        
        # Build PDF
        doc.build(story)
        
        # Always return bytes regardless of output_path  
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
    
    def generate_us_pdf(self, site_name: str, us_list: List[Dict[str, Any]], 
                       output_path: str, logo_path: str = None) -> str:
        """Generate US PDF report following exact PyArchInit ICCD format"""
        
        # Create document with PyArchInit original margins
        doc = SimpleDocTemplate(
            output_path, 
            pagesize=A4,
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=0.5*cm,
            bottomMargin=1*cm
        )
        story = []
        
        # Define PyArchInit ICCD styles
        styNormal = ParagraphStyle(
            'ICCDNormal',
            fontSize=8,
            fontName='Helvetica',
            alignment=0,
            spaceBefore=1,
            spaceAfter=1,
            leading=9
        )
        
        styBold = ParagraphStyle(
            'ICCDBold', 
            fontSize=8,
            fontName='Helvetica-Bold',
            alignment=0,
            spaceBefore=1,
            spaceAfter=1,
            leading=9
        )
        
        styTitle = ParagraphStyle(
            'ICCDTitle',
            fontSize=16,
            fontName='Helvetica-Bold',
            alignment=0,  # LEFT for "US" title
            spaceBefore=5,
            spaceAfter=5
        )
        
        styVertical = ParagraphStyle(
            'ICCDVertical',
            fontSize=7,
            fontName='Helvetica-Bold',
            alignment=1,
            leading=8
        )

        def safe_str(value):
            """Safely convert value to string"""
            if value is None or str(value) == 'None':
                return ''
            return str(value)
        
        # Generate individual US sheets in PyArchInit format
        for i, us_data in enumerate(us_list):
            if i > 0:
                story.append(PageBreak())
                
            # Add logo at top center of page (separate from table)
            if logo_path and os.path.exists(logo_path):
                try:
                    us_logo = Image(logo_path)
                    us_logo.drawHeight = 2.5 * inch * us_logo.drawHeight / us_logo.drawWidth
                    us_logo.drawWidth = 2.5 * inch
                    us_logo.hAlign = "CENTER"
                    story.append(us_logo)
                    story.append(Spacer(1, 0.3*inch))  # Space after logo
                except:
                    pass  # If logo fails, continue without it
            
            # Determine unit type (US or USM)
            unit_type = safe_str(us_data.get('unita_tipo', 'US'))
            if unit_type == '':
                unit_type = 'US'
                    
            # Unit type header
            unita_tipo = Paragraph(unit_type, styTitle)
            
            if unit_type == 'USM':
                # USM-specific sheet generation
                self._generate_usm_sheet(us_data, story, styNormal, styBold, styTitle, styVertical, colWidths)
            else:
                # Standard US sheet generation
                self._generate_us_sheet(us_data, story, styNormal, styBold, styTitle, styVertical, colWidths, unita_tipo)
            
            # Formation type
            formazione = us_data.get('formazione', '')
            if formazione == 'Naturale':
                label_NAT = Paragraph("<i>NAT.</i><br/>Naturale", styNormal)
                label_ART = Paragraph("<i>ART.</i>", styNormal)
            elif formazione == 'Artificiale':
                label_NAT = Paragraph("<i>NAT.</i>", styNormal)
                label_ART = Paragraph("<i>ART.</i><br/>Artificiale", styNormal)
            else:
                label_NAT = Paragraph("<i>NAT.</i>", styNormal)
                label_ART = Paragraph("<i>ART.</i>", styNormal)
            
            # Definition fields
            d_stratigrafica = Paragraph(f"<b>DEFINIZIONE E POSIZIONE</b><br/>Definizione stratigrafica: {safe_str(us_data.get('d_stratigrafica', ''))}<br/>Definizione interpretativa: {safe_str(us_data.get('d_interpretativa', ''))}", styNormal)
            
            # Description field
            descrizione = Paragraph(f"<b>DESCRIZIONE</b><br/>{safe_str(us_data.get('descrizione', ''))}", styNormal)
            
            # Interpretation field  
            interpretazione = Paragraph(f"<b>INTERPRETAZIONE</b><br/>{safe_str(us_data.get('interpretazione', ''))}", styNormal)
            
            # Extract stratigraphic relationships from rapporti field
            relationship_data = self._extract_stratigraphic_relationships(us_data.get('rapporti', []))
            
            # Stratigraphic relationships
            si_lega_a = Paragraph(f"<b>SI LEGA A</b><br/>{relationship_data['si_lega_a']}", styNormal)
            uguale_a = Paragraph(f"<b>UGUALE A</b><br/>{relationship_data['uguale_a']}", styNormal)
            copre = Paragraph(f"<b>COPRE</b><br/>{relationship_data['copre']}", styNormal)
            coperto_da = Paragraph(f"<b>COPERTO DA</b><br/>{relationship_data['coperto_da']}", styNormal)
            taglia = Paragraph(f"<b>TAGLIA</b><br/>{relationship_data['taglia']}", styNormal)
            tagliato_da = Paragraph(f"<b>TAGLIATO DA</b><br/>{relationship_data['tagliato_da']}", styNormal)
            riempie = Paragraph(f"<b>RIEMPIE</b><br/>{relationship_data['riempie']}", styNormal)
            riempito_da = Paragraph(f"<b>RIEMPITO DA</b><br/>{relationship_data['riempito_da']}", styNormal)
            si_appoggia = Paragraph(f"<b>SI APPOGGIA</b><br/>{relationship_data['si_appoggia']}", styNormal)
            gli_si_appoggia = Paragraph(f"<b>GLI SI APPOGGIA</b><br/>{relationship_data['gli_si_appoggia']}", styNormal)
            
            # Sequence labels
            posteriore_a = Paragraph("<b>POSTERIORE A</b><br/>", styNormal)
            anteriore_a = Paragraph("<b>ANTERIORE A</b><br/>", styNormal)
            
            # Additional ICCD standard fields
            stato_conservazione = Paragraph(f"<b>STATO DI CONSERVAZIONE</b><br/>{safe_str(us_data.get('stato_di_conservazione', ''))}", styNormal)
            consistenza = Paragraph(f"<b>CONSISTENZA</b><br/>{safe_str(us_data.get('consistenza', ''))}", styNormal)
            colore = Paragraph(f"<b>COLORE</b><br/>{safe_str(us_data.get('colore', ''))}", styNormal)
            inclusi = Paragraph(f"<b>INCLUSI</b><br/>{safe_str(us_data.get('inclusi', ''))}", styNormal)
            campioni = Paragraph(f"<b>CAMPIONI</b><br/>Flottazione: {safe_str(us_data.get('flottazione', ''))}<br/>Setacciatura: {safe_str(us_data.get('setacciatura', ''))}", styNormal)
            
            # Additional ICCD fields from original template - exactly like original
            ambiente = Paragraph(f"<b>AMBIENTE</b><br/>{safe_str(us_data.get('ambiente', ''))}", styNormal)
            pos_ambiente = Paragraph(f"<b>POS. NELL'AMBIENTE</b><br/>{safe_str(us_data.get('pos_ambiente', ''))}", styNormal)
            settore = Paragraph(f"<b>SETTORE/I</b><br/>{safe_str(us_data.get('settore', ''))}", styNormal) 
            quadrato = Paragraph(f"<b>QUADRATO/I</b><br/>{safe_str(us_data.get('quadrato', ''))}", styNormal)
            saggio = Paragraph(f"<b>SAGGIO</b><br/>{safe_str(us_data.get('saggio', ''))}", styNormal)
            
            # Quote field unified like the original - one field with min/max inside
            quote_min = safe_str(us_data.get('quota_min', ''))
            quote_max = safe_str(us_data.get('quota_max', ''))
            quote = Paragraph(f"<b>QUOTE</b><br/>min: {quote_min}<br/>max: {quote_max}", styNormal)
            
            # Posizione field  
            posizione = Paragraph(f"<b>POS. NELL'AMBIENTE</b><br/>{safe_str(us_data.get('posizione', ''))}", styNormal)
            
            # Documentation fields exactly like original
            piante = Paragraph(f"<b>PIANTE</b><br/>{safe_str(us_data.get('piante', ''))}", styNormal)
            prospetti = Paragraph(f"<b>PROSPETTI</b><br/>{safe_str(us_data.get('prospetti', ''))}", styNormal)
            sezioni = Paragraph(f"<b>SEZIONI</b><br/>{safe_str(us_data.get('sezioni', 'tavola 4'))}", styNormal)
            fotografie = Paragraph(f"<b>FOTOGRAFIE</b><br/>{safe_str(us_data.get('fotografie', ''))}", styNormal)
            
            # Formation criteria exactly like original
            criteri_distinzione = Paragraph(f"<b>CRITERI DI DISTINZIONE</b><br/>{safe_str(us_data.get('criteri_distinzione', 'CCC'))}", styNormal)
            modo_formazione = Paragraph(f"<b>MODO FORMAZIONE</b><br/>{safe_str(us_data.get('modo_formazione', ''))}", styNormal)
            
            # Misure field
            misure = Paragraph(f"<b>MISURE</b><br/>{safe_str(us_data.get('misure', ''))}", styNormal)
            
            # Component fields
            organici = Paragraph(f"<b>ORGANICI</b><br/>{safe_str(us_data.get('organici', ''))}", styNormal)
            inorganici = Paragraph(f"<b>INORGANICI</b><br/>{safe_str(us_data.get('inorganici', ''))}", styNormal)
            
            # Remove duplicate foto definition since we already have fotografie
            
            # Move these definitions before they're used in cell_schema
            # Datazione and period/phase content for the integrated table
            datazione_content = Paragraph(f"<b>DATAZIONE</b><br/>{safe_str(us_data.get('datazione', ''))}", styNormal)
            
            # Period and phase fields exactly like original
            periodo_iniziale = safe_str(us_data.get('periodo_iniziale', ''))
            fase_iniziale = safe_str(us_data.get('fase_iniziale', ''))  
            periodo_finale = safe_str(us_data.get('periodo_finale', ''))
            fase_finale = safe_str(us_data.get('fase_finale', ''))
            
            periodo_fase_content = Paragraph(f"<b>PERIODO O FASE</b><br/>Periodo iniziale: {periodo_iniziale}<br/>Fase iniziale: {fase_iniziale}<br/>Periodo finale: {periodo_finale}<br/>Fase finale: {fase_finale}", styNormal)
            attivita_content = Paragraph(f"<b>ATTIVITÀ</b><br/>{safe_str(us_data.get('attivita', ''))}", styNormal)
            
            # Additional fields
            elementi_datanti = Paragraph(f"<b>ELEMENTI DATANTI</b><br/>{safe_str(us_data.get('elementi_datanti', ''))}", styNormal)
            dati_quantitativi = Paragraph(f"<b>DATI QUANTITATIVI DEI REPERTI</b><br/>{safe_str(us_data.get('dati_quantitativi', ''))}", styNormal)
            
            # Sampling fields exactly like original
            campionature = Paragraph(f"<b>CAMPIONATURE</b><br/>{safe_str(us_data.get('campionature', ''))}", styNormal)
            flottazione = Paragraph(f"<b>FLOTTAZIONE</b><br/>{safe_str(us_data.get('flottazione', ''))}", styNormal)
            setacciatura = Paragraph(f"<b>SETACCIATURA</b><br/>{safe_str(us_data.get('setacciatura', ''))}", styNormal)
            
            # Affidabilita
            affidabilita = Paragraph(f"<b>AFFIDABILITÀ STRATIGRAFICA</b><br/>{safe_str(us_data.get('affidabilita', ''))}", styNormal)
            
            # Responsibility fields
            direttore = Paragraph(f"<b>RESPONSABILE SCIENTIFICO DELLE INDAGINI</b><br/>{safe_str(us_data.get('responsabile_scientifico', ''))}", styNormal)
            data_rilievo = Paragraph(f"<b>DATA RILEVAMENTO SUL CAMPO</b><br/>{safe_str(us_data.get('data_schedatura', ''))}", styNormal)
            data_rielaborazione = Paragraph(f"<b>DATA RIELABORAZIONE</b><br/>{safe_str(us_data.get('data_rielaborazione', ''))}", styNormal)
            
            # Prepare label variables like original PyArchInit
            label_ente_responsabile = Paragraph("<b>ENTE RESPONSABILE</b><br/>" + safe_str(us_data.get('cod_ente_schedatore', '')), styBold)
            label_unita_stratigrafica = Paragraph("<b>NUMERO/CODICE IDENTIFICATIVO DELL'UNITÀ STRATIGRAFICA</b><br/>" + safe_str(us_data.get('us', '')), styBold)
            label_sas = Paragraph("<b>NUMERO/CODICE IDENTIFICATIVO DEL SAGGIO<br/>STRATIGRAFICO/DELL'EDIFICIO/DELLA STRUTTURA/DELLA<br/>DEPOSIZIONE FUNERARIA DI RIFERIMENTO</b><br/>" + safe_str(us_data.get('nr_scheda_tma', '')), styBold)
            sop = Paragraph("<b>SOPRINTENDENZA MIBACT COMPETENTE PER TUTELA</b><br/>" + safe_str(us_data.get('soprintendenza', 'SABAP-RA')), styBold)
            
            # Components headers
            label_organici = Paragraph("<b>ORGANICI</b>", styBold)
            label_inorganici = Paragraph("<b>INORGANICI</b>", styBold)
            label_componenti = Paragraph("<b>C<br/>O<br/>M<br/>P<br/>O<br/>N<br/>E<br/>N<br/>T<br/>I</b>", styVertical)
            
            # Relationships
            label_sequenza_stratigrafica = Paragraph("<b>S<br/>E<br/>Q<br/>U<br/>E<br/>N<br/>Z<br/>A<br/><br/>S<br/>T<br/>R<br/>A<br/>T<br/>I<br/>G<br/>R<br/>A<br/>F<br/>I<br/>C<br/>A</b>", styVertical)
            
            # Components content
            comp_organici = Paragraph(safe_str(us_data.get('organici', '')), styNormal)
            comp_inorganici = Paragraph(safe_str(us_data.get('inorganici', '')), styNormal)
            
            # Si appoggia fields
            si_appoggia_a = Paragraph(f"<b>SI APPOGGIA</b><br/>{relationship_data['si_appoggia']}", styNormal)
            
            # Responsibility fields
            responsabile = Paragraph(f"<b>RESPONSABILE COMPILAZIONE SUL CAMPO</b><br/>{safe_str(us_data.get('schedatore', ''))}", styNormal)
            responsabile2 = Paragraph(f"<b>RESPONSABILE RIELABORAZIONE</b><br/>{safe_str(us_data.get('responsabile_rielaborazione', ''))}", styNormal)
            
            # Additional fields
            osservazioni = Paragraph("<b>OSSERVAZIONI</b><br/>" + safe_str(us_data.get('osservazioni', '')), styNormal)
            tabelle_materiali = Paragraph(f"<b>RIFERIMENTI TABELLE MATERIALI</b><br/>RA: {safe_str(us_data.get('ref_ra', ''))}", styNormal)
            
            # Create table schema EXACTLY following PyArchInit original ICCD structure
            cell_schema = [
                # Row 0-1: Header with unita_tipo, ente responsabile and label_unita_stratigrafica
                [unita_tipo, '01', label_ente_responsabile, '03', '04', '05', '06', '07', '08', '09', '10', label_unita_stratigrafica, '12', '13', '14', '15', '16', '17'],
                ['00', '01', sop, '03', '04', '05', '06', '07', '08', '09', '10', label_sas, '12', '13', '14', '15', '16', '17'],
                
                # Row 2: Sito
                [sito, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                # Row 3: Area and Saggio
                [area, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', saggio, '12', '13', '14', '15', '16', '17'],
                
                # Row 4: Location details
                [ambiente, '01', '02', '03', posizione, '05', '06', settore, '08', quadrato, '10', quote, '12', '13', label_NAT, '15', label_ART, '17'],
                
                # Row 5: Documentation
                [piante, '01', prospetti, '03', sezioni, '05', '06', fotografie, '08', '09', '10', tabelle_materiali, '12', '13', '14', '15', '16', '17'],
                
                # Row 6: Definizione stratigrafica
                [d_stratigrafica, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                # Row 7: Criteri distinzione
                [criteri_distinzione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                # Row 8: Modo formazione
                [modo_formazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                # Row 9: Components headers
                [label_organici, '01', '02', '03', '04', '05', '06', '07', '08', label_inorganici, '10', '11', '12', '13', '14', '15', '16', '17'],
                
                # Row 10: Components content
                [label_componenti, comp_organici, '02', '03', '04', '05', '06', '07', '08', comp_inorganici, '10', '11', '12', '13', '14', '15', '16', '17'],
                
                # Row 11: Consistenza, colore, misure
                [consistenza, '01', '02', '03', '04', '05', colore, '07', '08', '09', '10', '11', misure, '13', '14', '15', '16', '17'],
                
                # Row 12: Stato conservazione
                [stato_conservazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                # Row 13: Relationships header
                [uguale_a, '01', '02', '03', '04', '05', si_lega_a, '07', '08', '09', '10', '11', label_sequenza_stratigrafica, posteriore_a, '14', '15', '16', '17'],
                
                # Row 14: Empty row
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                # Row 15: Gli si appoggia / Si appoggia
                [gli_si_appoggia, '01', '02', '03', '04', '05', si_appoggia_a, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                # Row 16: Empty row
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                # Row 17: Coperto da / Copre
                [coperto_da, '01', '02', '03', '04', '05', copre, '07', '08', '09', '10', '11', '12', anteriore_a, '14', '15', '16', '17'],
                
                # Row 18: Empty row
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                # Row 19: Tagliato da / Taglia
                [tagliato_da, '01', '02', '03', '04', '05', taglia, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                # Row 20: Empty row
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                # Row 21: Riempito da / Riempie
                [riempito_da, '01', '02', '03', '04', '05', riempie, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                # Row 22: Empty row
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                # Row 23: Descrizione
                [descrizione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                # Row 24: Osservazioni
                [osservazioni, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                # Row 25: Interpretazione
                [interpretazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                # Row 26: Datazione, periodo fase, attivita
                [datazione_content, '01', '02', '03', '04', '05', periodo_fase_content, '07', '08', '09', '10', '11', attivita_content, '13', '14', '15', '16', '17'],
                
                # Row 27: Elementi datanti
                [elementi_datanti, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                # Row 28: Dati quantitativi
                [dati_quantitativi, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                # Row 29: Campioni, flottazione, setacciatura
                [campionature, '01', '02', '03', '04', '05', flottazione, '07', '08', '09', '10', '11', setacciatura, '13', '14', '15', '16', '17'],
                
                # Row 30: Affidabilita
                [affidabilita, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                # Row 31: Direttore/responsabile scientifico
                [direttore, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                # Row 32: Data rilievo, responsabile compilazione
                [data_rilievo, '01', '02', '03', '04', '05', '06', '07', '08', responsabile, '10', '11', '12', '13', '14', '15', '16', '17'],
                
                # Row 33: Data rielaborazione, responsabile rielaborazione
                [data_rielaborazione, '01', '02', '03', '04', '05', '06', '07', '08', responsabile2, '10', '11', '12', '13', '14', '15', '16', '17'],
            ]
            
            # Table style following PyArchInit original exactly
            # table style
            table_style = [

                ('GRID', (0, 0), (-1, -1), 0.3, colors.black),
                # 0 row
                ('SPAN', (0, 0), (1, 1)),  # unita tipo
                ('VALIGN', (0, 0), (1, 1), 'MIDDLE'),

                ('SPAN', (2, 0), (10, 0)),  # label n. catalogo generale
                ('SPAN', (11, 0), (17, 0)),  # label n. catalogo internazionale
                ('VALIGN', (2, 0), (12,1), 'TOP'),

                # 1 row
                ('SPAN', (2, 1), (10, 1)),  # n. catalogo generale
                ('SPAN', (11, 1), (17, 1)),  # catalogo internazionale
                ('VALIGN', (2, 0), (17, 1), 'TOP'),

                # 2 row
                ('SPAN', (0, 2), (17, 2)),  # sito

                ('VALIGN', (0, 2), (17, 2), 'TOP'),

                # 3 row
                ('SPAN', (0, 3), (10, 3)),  # piante
                ('SPAN', (11, 3), (17, 3)),  # sezioni
                ('VALIGN', (0, 3), (17, 3), 'TOP'),

                # 4 row
                ('SPAN', (0, 4), (3, 4)),  # definizione
                ('SPAN', (4, 4), (6, 4)),  # definizione
                ('SPAN', (7, 4), (8, 4)),  # definizione
                ('SPAN', (9, 4), (10, 4)),  # definizione
                ('SPAN', (11, 4), (13, 4)),  # definizione
                ('SPAN', (14, 4), (15, 4)),  # definizione
                ('SPAN', (16, 4), (17, 4)),  # definizione
                ('VALIGN', (0, 4), (17, 4), 'TOP'),

                # 5 row
                ('SPAN', (0, 5), (1, 5)),  # definizione
                ('SPAN', (2,5), (3, 5)),  # definizione
                ('SPAN', (4, 5), (6, 5)),  # definizione
                ('SPAN', (7, 5), (10, 5)),  # definizione
                ('SPAN', (11, 5), (17, 5)),  # definizione
                ('VALIGN', (0, 5), (17, 5), 'TOP'),

                # 6 row
                ('SPAN', (0, 6), (17, 6)),  # modo di formazione
                ('VALIGN', (0, 6), (17, 6), 'TOP'),

                # 7 row
                ('SPAN', (0, 7), (17, 7)),  # label componenti
                ('VALIGN', (0, 7), (17, 7), 'TOP'),

                # 8 row
                ('SPAN', (0, 8), (17, 8)),  # consistenza
                ('VALIGN', (0, 8), (17, 8), 'TOP'),

                # 9-10 row

                ('SPAN', (0, 9), (8, 9)),  # consistenza
                ('SPAN', (9, 9), (17, 9)),  # consistenza
                ('SPAN', (0, 10), (0, 10)),  # consistenza
                ('SPAN', (1, 10), (8, 10)),  # consistenza
                ('SPAN', (9, 10), (17, 10)),  # consistenza
                ('VALIGN', (0, 9), (17, 10), 'TOP'),




                # 11 row
                ('SPAN', (0, 11), (5, 11)),  # stato di conservazione
                ('SPAN', (6, 11), (11, 11)),  # stato di conservazione
                ('SPAN', (12, 11), (17, 11)),  # stato di conservazione
                ('VALIGN', (0, 11), (17, 11), 'TOP'),

                # 12 row
                ('SPAN', (0, 12), (17, 12)),  # descrizione
                ('VALIGN', (0, 12), (17, 12), 'TOP'),

                # 13-22 row
                ('SPAN', (0, 13), (5, 14)),    # uguale a
                ('SPAN', (0, 15), (5, 16)),    # gli si appoggia
                ('SPAN', (0, 17), (5, 18)),    # coperto da
                ('SPAN', (0, 19), (5, 20)),    # tagliato da
                ('SPAN', (0, 21), (5, 22)),    # riempito da
                ('SPAN', (6, 13), (11, 14)),   # si lega a
                ('SPAN', (6, 15), (11, 16)),   # si appoggia a
                ('SPAN', (6, 17), (11, 18)),   # copre
                ('SPAN', (6, 19), (11, 20)),   # taglia
                ('SPAN', (6, 21), (11, 22)),   # riempie
                ('SPAN', (12, 13), (12, 22)),  # label sequenza stratigrafica
                ('SPAN', (13, 13), (17, 17)),  # posteriore a
                ('SPAN', (13, 18), (17, 22)),  # uguale a
                ('VALIGN', (0, 13), (17, 22), 'TOP'),

                # 23 row
                ('SPAN', (0, 23), (17, 23)),  # DESCRIZIONE
                ('VALIGN', (0, 23), (17, 23), 'TOP'),

                # 24 row
                ('SPAN', (0, 24), (17, 24)),  # OSSERVAZIONI
                ('VALIGN', (0, 24), (17, 24), 'TOP'),

                # 25 row

                ('SPAN', (0, 25), (17, 25)),  # INTERPRETAZIONI
                ('VALIGN', (0, 25), (17, 25), 'TOP'),

                #26 row

                ('SPAN', (0, 26), (5, 26)),  # datazione
                ('SPAN', (6, 26), (11, 26)),  # periodo o fase
                ('SPAN', (12, 26), (17, 26)),  # ATTIVITA
                ('VALIGN', (0, 26), (17, 26), 'TOP'),

                # #27 row

                ('SPAN', (0, 27), (17, 27)),  # elementi datanti
                ('VALIGN', (0, 27), (17, 27), 'TOP'),

                ('SPAN', (0, 28), (17, 28)),  # elementi datanti
                ('VALIGN', (0, 28), (17, 28), 'TOP'),

                #28 row
                ('SPAN', (0, 29), (5, 29)),  # campionature
                ('SPAN', (6, 29), (11, 29)),  # flottazione
                ('SPAN', (12, 29), (17, 29)),  # setacciatura
                ('VALIGN', (0, 29), (17, 29), 'TOP'),

                #29 row
                ('SPAN', (0, 30), (17, 30)),  # affidabilita stratigrafica

                ('VALIGN', (0, 30), (17, 30), 'TOP'),

                ('SPAN', (0, 31), (17, 31)),  # affidabilita stratigrafica
                ('VALIGN', (0, 31), (17, 31), 'TOP'),

                ('SPAN', (0, 32), (8, 32)),  # affidabilita stratigrafica
                ('SPAN', (9, 32), (17, 32)),  # affidabilita stratigrafica
                ('VALIGN', (0, 32), (17, 32), 'TOP'),

                ('SPAN', (0, 33), (8, 33)),  # affidabilita stratigrafica
                ('SPAN', (9, 33), (17, 33)),  # affidabilita stratigrafica
                ('VALIGN', (0, 33), (17, 33), 'TOP'),
            ]

            colWidths = (15,30,30,30,30,30,30,30,30,30,30,30,20,30,30,30,30,30)
            rowHeights = None
            
            us_table = Table(cell_schema, colWidths=colWidths, rowHeights=rowHeights, style=table_style)
            story.append(us_table)
        
        # Build document
        doc.build(story)
        return output_path
    
    def _generate_us_sheet(self, us_data, story, styNormal, styBold, styTitle, styVertical, colWidths, unita_tipo):
        """Generate standard US sheet"""
        def safe_str(value):
            """Safely convert value to string"""
            if value is None or str(value) == 'None':
                return ''
            return str(value)
            
        # Basic identification fields
        sito = Paragraph(f"<b>LOCALITÀ</b><br/>{safe_str(us_data.get('sito', ''))}", styBold)
        area = Paragraph(f"<b>AREA/EDIFICIO/STRUTTURA</b><br/>{safe_str(us_data.get('area', ''))}", styBold)
        us_num = Paragraph(f"<b>NUMERO/CODICE IDENTIFICATIVO DELL'UNITÀ STRATIGRAFICA</b><br/>{safe_str(us_data.get('us', ''))}", styBold)
    
    def _extract_stratigraphic_relationships(self, rapporti):
        """Extract and categorize stratigraphic relationships like PyArchInit original"""
        
        # Initialize all relationship types
        relationships = {
            'si_lega_a': '',
            'uguale_a': '',
            'copre': '',
            'coperto_da': '',
            'taglia': '',
            'tagliato_da': '',
            'riempie': '',
            'riempito_da': '',
            'si_appoggia': '',
            'gli_si_appoggia': ''
        }
        
        if not rapporti:
            return relationships
            
        try:
            # Handle different formats
            if isinstance(rapporti, str):
                rapporti_list = eval(rapporti)
            elif isinstance(rapporti, list):
                rapporti_list = rapporti
            else:
                return relationships
                
            for rapporto in rapporti_list:
                try:
                    # Handle string format like "['Copre', 'US_2']"
                    if isinstance(rapporto, str):
                        rapporto = eval(rapporto)
                    
                    if isinstance(rapporto, (list, tuple)) and len(rapporto) >= 2:
                        rel_type = rapporto[0].lower()
                        us_target = str(rapporto[1]).replace('US_', '')
                        
                        # Map relationship types
                        if rel_type in ['si lega a', 'si_lega_a']:
                            key = 'si_lega_a'
                        elif rel_type in ['uguale a', 'uguale_a']:
                            key = 'uguale_a'
                        elif rel_type == 'copre':
                            key = 'copre'
                        elif rel_type in ['coperto da', 'coperto_da']:
                            key = 'coperto_da'
                        elif rel_type == 'taglia':
                            key = 'taglia'
                        elif rel_type in ['tagliato da', 'tagliato_da']:
                            key = 'tagliato_da'
                        elif rel_type == 'riempie':
                            key = 'riempie'
                        elif rel_type in ['riempito da', 'riempito_da']:
                            key = 'riempito_da'
                        elif rel_type in ['si appoggia', 'si_appoggia']:
                            key = 'si_appoggia'
                        elif rel_type in ['gli si appoggia', 'gli_si_appoggia']:
                            key = 'gli_si_appoggia'
                        else:
                            continue  # Unknown relationship type
                        
                        # Add to the appropriate category
                        if relationships[key] == '':
                            relationships[key] = us_target
                        else:
                            relationships[key] += ', ' + us_target
                            
                except Exception as e:
                    continue  # Skip invalid relationships
                    
        except Exception as e:
            pass  # Return empty relationships if parsing fails
            
        return relationships
    
    def generate_inventario_pdf(self, site_name: str, inventario_list: List[Dict[str, Any]], 
                               output_path: str, logo_path: str = None) -> str:
        """Generate Inventario (Finds) PDF report using authentic PyArchInit template"""
        
        from .pyarchinit_finds_template import PyArchInitFindsTemplate
        
        # Use the authentic PyArchInit finds template (single_Finds_pdf_sheet style)
        template = PyArchInitFindsTemplate()
        return template.generate_finds_sheets(inventario_list, output_path, site_name, logo_path)
