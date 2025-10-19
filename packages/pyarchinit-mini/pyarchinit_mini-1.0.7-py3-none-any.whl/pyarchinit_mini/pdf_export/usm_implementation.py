def _generate_usm_sheet(self, us_data, story, styNormal, styNormal2, styBold, styTitle, styVertical, colWidths, unita_tipo):
    """Generate USM (Unità Stratigrafiche Murarie) sheet"""
    def safe_str(value):
        """Safely convert value to string"""
        if value is None or str(value) == 'None':
            return ''
        return str(value)
    
    # Extract stratigraphic relationships
    relationship_data = self._extract_stratigraphic_relationships(us_data.get('rapporti', []))
    
    # Basic labels and fields
    label_ente_responsabile = Paragraph("<b>ENTE RESPONSABILE</b><br/>" + safe_str(us_data.get('cod_ente_schedatore', '')), styBold)
    sop = Paragraph("<b>SOPRINTENDENZA MIBACT COMPETENTE PER TUTELA</b><br/>" + safe_str(us_data.get('soprintendenza', 'SABAP-RA')), styBold)
    
    # Location fields
    sito = Paragraph("<b>LOCALITÀ</b><br/>" + safe_str(us_data.get('sito', '')), styBold)
    
    # Check if struttura exists for area field
    struttura = safe_str(us_data.get('struttura', ''))
    if struttura != '':
        area = Paragraph("<b>AREA/EDIFICIO/STRUTTURA</b><br/>" + safe_str(us_data.get('area', '')) + '/' + struttura, styBold)
    else:
        area = Paragraph("<b>AREA/EDIFICIO/STRUTTURA</b><br/>" + safe_str(us_data.get('area', '')), styBold)
    
    saggio = Paragraph("<b>SAGGIO</b><br/>" + safe_str(us_data.get('saggio', '')), styNormal)
    ambiente = Paragraph("<b>AMBIENTE</b><br/>" + safe_str(us_data.get('ambient', '')), styNormal)
    posizione = Paragraph("<b>POS. NELL'AMBIENTE</b><br/>" + safe_str(us_data.get('posizione', '')), styNormal)
    settore = Paragraph("<b>SETTORE/I</b><br/>" + safe_str(us_data.get('settore', '')), styNormal)
    quadrato = Paragraph("<b>QUADRATO/I</b><br/>" + safe_str(us_data.get('quad_par', '')), styNormal)
    
    # Quote with min/max
    quote_min = safe_str(us_data.get('quota_min', ''))
    quote_max = safe_str(us_data.get('quota_max', ''))
    quote = Paragraph("<b>QUOTE</b><br/>min: " + quote_min + "<br/>max: " + quote_max, styNormal)
    
    label_unita_stratigrafica = Paragraph("<b>NUMERO/CODICE IDENTIFICATIVO DELL'UNITÀ STRATIGRAFICA</b><br/>" + str(us_data.get('us', '')), styNormal)
    label_sas = Paragraph("<b>NUMERO/CODICE IDENTIFICATIVO DEL SAGGIO STRATIGRAFICO/DELL'EDIFICIO/DELLA STRUTTURA/DELLA DEPOSIZIONE FUNERARIA DI RIFERIMENTO</b><br/>", styNormal)
    
    # Documentation fields
    piante = Paragraph("<b>PIANTE</b><br/>" + safe_str(us_data.get('piante_iccd', '')), styNormal)
    sezioni = Paragraph("<b>SEZIONI</b><br/>" + safe_str(us_data.get('sezioni_iccd', '')), styNormal)
    prospetti = Paragraph("<b>PROSPETTI</b><br/>" + safe_str(us_data.get('prospetti_iccd', '')), styNormal)
    foto = Paragraph("<b>FOTOGRAFIE</b><br/>" + safe_str(us_data.get('foto_iccd', '')), styNormal)
    
    # USM-specific fields
    t_muraria = Paragraph("<b>TIPOLOGIA DELL'OPERA</b><br/>" + safe_str(us_data.get('tipologia_opera', '')), styNormal)
    t_costruttiva = Paragraph("<b>TECNICA COSTRUTTIVA</b><br/>" + safe_str(us_data.get('tecnica_muraria_usm', '')), styNormal)
    sezione_muraria = Paragraph("<b>SEZIONE MURARIA</b><br/>" + safe_str(us_data.get('sezione_muraria', '')), styNormal)
    modulo = Paragraph("<b>MODULO</b><br/>" + safe_str(us_data.get('modulo_usm', '')), styNormal)
    
    # Measurements field with conditional formatting
    lunghezza_usm = safe_str(us_data.get('lunghezza_usm', ''))
    altezza_usm = safe_str(us_data.get('altezza_usm', ''))
    
    if bool(lunghezza_usm) and bool(altezza_usm):
        misure = Paragraph("<b>MISURE</b><br/>Lun. " + lunghezza_usm + " x Alt. " + altezza_usm + "m", styNormal)
    elif bool(lunghezza_usm) and not bool(altezza_usm):
        misure = Paragraph("<b>MISURE</b><br/>Lun. " + lunghezza_usm + "m", styNormal)
    elif bool(altezza_usm) and not bool(lunghezza_usm):
        misure = Paragraph("<b>MISURE</b><br/>Alt. " + altezza_usm + "m", styNormal)
    else:
        misure = Paragraph("<b>MISURE</b><br/>", styNormal)
    
    superficie_analizzata = Paragraph("<b>SUPERFICIE ANALIZZATA</b><br/>" + safe_str(us_data.get('superficie_analizzata', '')), styNormal)
    
    # Definition and position
    d_stratigrafica = Paragraph("<b>DEFINIZIONE E POSIZIONE</b><br/>" + safe_str(us_data.get('d_stratigrafica', '')) + "<br/>" + safe_str(us_data.get('d_interpretativa', '')), styNormal)
    
    criteri_distinzione = Paragraph("<b>CRITERI DI DISTINZIONE</b><br/>" + safe_str(us_data.get('criteri_distinzione', '')), styNormal)
    
    # Materials and usage fields
    provenienza_materiali = Paragraph("<b>PROVENIENZA MATERIALI</b><br/>" + safe_str(us_data.get('provenienza_materiali_usm', '')), styNormal2)
    uso_primario = Paragraph("<b>USO PRIMARIO</b><br/>" + safe_str(us_data.get('uso_primario_usm', '')), styNormal2)
    reimpiego = Paragraph("<b>REIMPIEGO</b><br/>" + safe_str(us_data.get('reimp', '')), styNormal2)
    orientamento = Paragraph("<b>ORIENTAMENTO</b><br/>" + safe_str(us_data.get('orientamento', '')), styNormal)
    
    stato_conservazione = Paragraph("<b>STATO DI CONSERVAZIONE</b><br/>" + safe_str(us_data.get('stato_di_conservazione', '')), styNormal)
    
    # Bricks section
    label_laterizi = Paragraph("<b>LATERIZI<br/></b>", styVertical)
    materiali = Paragraph("<b>MATERIALI</b><br/>", styNormal2)
    lavorazione = Paragraph("<b>LAVORAZIONE</b><br/>", styNormal2)
    consistenza = Paragraph("<b>CONSISTENZA</b><br/>", styNormal2)
    forma = Paragraph("<b>FORMA</b><br/>", styNormal2)
    colore = Paragraph("<b>COLORE</b><br/>", styNormal2)
    impasto = Paragraph("<b>IMPASTO</b><br/>", styNormal2)
    posa_opera = Paragraph("<b>POSA IN OPERA</b><br/>", styNormal2)
    
    # Bricks data
    materiali_1 = Paragraph(safe_str(us_data.get('materiali_lat', '')), styNormal)
    lavorazione_1 = Paragraph(safe_str(us_data.get('lavorazione_lat', '')), styNormal)
    consistenza_1 = Paragraph(safe_str(us_data.get('consistenza_lat', '')), styNormal)
    forma_1 = Paragraph(safe_str(us_data.get('forma_lat', '')), styNormal)
    colore_1 = Paragraph(safe_str(us_data.get('colore_lat', '')), styNormal)
    impasto_1 = Paragraph(safe_str(us_data.get('impasto_lat', '')), styNormal)
    posa_opera_1 = Paragraph(safe_str(us_data.get('posa_opera', '')), styNormal)
    
    # Stone elements section
    label_pietra = Paragraph("<b>ELEMENTI<br/>LITICI</b>", styVertical)
    p_1 = Paragraph(safe_str(us_data.get('materiale_p', '')), styNormal)
    p_2 = Paragraph(safe_str(us_data.get('lavorazione', '')), styNormal)
    p_3 = Paragraph(safe_str(us_data.get('consistenza_p', '')), styNormal)
    p_4 = Paragraph(safe_str(us_data.get('forma_p', '')), styNormal)
    p_5 = Paragraph(safe_str(us_data.get('colore_p', '')), styNormal)
    taglio = Paragraph("<b>TAGLIO</b><br/>" + safe_str(us_data.get('taglio_p', '')), styNormal)
    p_7 = Paragraph(safe_str(us_data.get('posa_opera_p', '')), styNormal)
    
    # Materials notes
    note_materiali = Paragraph("<b>NOTE SPECIFICHE SUI MATERIALI</b><br/><br/><br/><br/><br/><br/>", styNormal)
    
    # Mortar section
    n = Paragraph('', styNormal)
    tipo = Paragraph("<b>TIPO</b><br/>", styNormal)
    consistenza_l = Paragraph("<b>CONSISTENZA</b><br/>", styNormal)
    colore_l = Paragraph("<b>COLORE</b><br/>", styNormal)
    inerti = Paragraph("<b>INERTI</b><br/>", styNormal)
    spessore = Paragraph("<b>SPESSORE</b><br/>", styNormal)
    rifinitura = Paragraph("<b>RIFINITURA</b><br/>", styNormal)
    
    label_legante = Paragraph("<b>LEGANTE<br/></b>", styVertical)
    tipo_1 = Paragraph(safe_str(us_data.get('tipo_legante_usm', '')), styNormal)
    consistenza_2 = Paragraph(safe_str(us_data.get('cons_legante', '')), styNormal)
    
    # Special handling for colore and inerti USM
    colore_usm = safe_str(us_data.get('colore_usm', ''))
    inerti_usm = safe_str(us_data.get('inerti_usm', ''))
    
    colore_3 = Paragraph(colore_usm, styNormal)
    inerti_4 = Paragraph(inerti_usm, styNormal)
    spessore_5 = Paragraph(safe_str(us_data.get('spessore_usm', '')), styNormal)
    rifinitura_6 = Paragraph(safe_str(us_data.get('rifinitura_usm', '')), styNormal)
    
    note_legante = Paragraph("<b>NOTE SPECIFICHE DEL LEGANTE</b><br/>", styNormal)
    
    # Stratigraphic relationships
    si_lega_a = Paragraph("<b>SI LEGA A</b><br/>" + relationship_data['si_lega_a'], styNormal)
    uguale_a = Paragraph("<b>UGUALE A</b><br/>" + relationship_data['uguale_a'], styNormal)
    copre = Paragraph("<b>COPRE</b><br/>" + relationship_data['copre'], styNormal)
    coperto_da = Paragraph("<b>COPERTO DA</b><br/>" + relationship_data['coperto_da'], styNormal)
    riempie = Paragraph("<b>RIEMPIE</b><br/>" + relationship_data['riempie'], styNormal)
    riempito_da = Paragraph("<b>RIEMPITO DA</b><br/>" + relationship_data['riempito_da'], styNormal)
    taglia = Paragraph("<b>TAGLIA</b><br/>" + relationship_data['taglia'], styNormal)
    tagliato_da = Paragraph("<b>TAGLIATO DA</b><br/>" + relationship_data['tagliato_da'], styNormal)
    si_appoggia_a = Paragraph("<b>SI APPOGGIA A</b><br/>" + relationship_data['si_appoggia'], styNormal)
    gli_si_appoggia = Paragraph("<b>GLI SI APPOGGIA</b><br/>" + relationship_data['gli_si_appoggia'], styNormal)
    
    label_sequenza_stratigrafica = Paragraph("<b>S<br/>E<br/>Q<br/>U<br/>E<br/>N<br/>Z<br/>A<br/><br/>S<br/>T<br/>R<br/>A<br/>T<br/>I<br/>G<br/>R<br/>A<br/>F<br/>I<br/>C<br/>A</b>", styVertical)
    
    # Aggregate relationships for posteriore/anteriore
    posteriore_a = Paragraph("<b>POSTERIORE A</b><br/>" + relationship_data['copre'] + "<br/>" + 
                           relationship_data['riempie'] + "<br/>" + relationship_data['taglia'] + 
                           "<br/>" + relationship_data['si_appoggia'], styNormal)
    anteriore_a = Paragraph("<b>ANTERIORE A</b><br/>" + relationship_data['coperto_da'] + "<br/>" + 
                          relationship_data['riempito_da'] + "<br/>" + relationship_data['tagliato_da'] + 
                          "<br/>" + relationship_data['gli_si_appoggia'], styNormal)
    
    # Description fields
    descrizione = Paragraph("<b>DESCRIZIONE</b><br/>" + safe_str(us_data.get('descrizione', '')), styNormal)
    osservazioni = Paragraph("<b>OSSERVAZIONI</b><br/>" + safe_str(us_data.get('osservazioni', '')), styNormal)
    interpretazione = Paragraph("<b>INTERPRETAZIONE</b><br/>" + safe_str(us_data.get('interpretazione', '')), styNormal)
    
    # Sampling fields
    campioni_malta = Paragraph("<b>CAMPIONATURE MALTA</b><br/>" + safe_str(us_data.get('campioni_malta_usm', '')), styNormal)
    campioni_mattone = Paragraph("<b>CAMPIONATURE LATERIZI</b><br/>" + safe_str(us_data.get('campioni_mattone_usm', '')), styNormal)
    campioni_pietra = Paragraph("<b>CAMPIONATURE ELEMENTI LITICI</b><br/>" + safe_str(us_data.get('campioni_pietra_usm', '')), styNormal)
    
    elementi_datanti = Paragraph("<b>ELEMENTI DATANTI</b><br/>" + safe_str(us_data.get('elem_datanti', '')), styNormal)
    
    # Dating and phases
    datazione_ipotesi = Paragraph("<b>DATAZIONE</b><br/>" + safe_str(us_data.get('datazione', '')), styNormal)
    
    periodo_iniziale = safe_str(us_data.get('periodo_iniziale', ''))
    fase_iniziale = safe_str(us_data.get('fase_iniziale', ''))
    periodo_finale = safe_str(us_data.get('periodo_finale', ''))
    fase_finale = safe_str(us_data.get('fase_finale', ''))
    
    periodo_o_fase = Paragraph("<b>PERIODO O FASE</b><br/>Periodo iniziale: " + periodo_iniziale + 
                             "<br/>Fase iniziale: " + fase_iniziale + "<br/>Periodo finale: " + 
                             periodo_finale + "<br/>Fase finale: " + fase_finale, styNormal)
    
    # Activity and responsibility fields
    attivita = Paragraph("<b>ATTIVITÀ</b><br/>" + safe_str(us_data.get('attivita', '')), styNormal)
    affidabilita = Paragraph("<b>AFFIDABILITÀ STRATIGRAFICA</b><br/>" + safe_str(us_data.get('affidabilita', '')), styNormal)
    direttore = Paragraph("<b>RESPONSABILE SCIENTIFICO DELLE INDAGINI</b><br/>" + safe_str(us_data.get('direttore_us', '')), styNormal)
    responsabile2 = Paragraph("<b>RESPONSABILE COMPILAZIONE SUL CAMPO</b><br/>" + safe_str(us_data.get('schedatore', '')), styNormal)
    responsabile = Paragraph("<b>RESPONSABILE RIELABORAZIONE</b><br/>" + safe_str(us_data.get('responsabile_us', '')), styNormal)
    data_rilievo = Paragraph("<b>DATA RILEVAMENTO SUL CAMPO</b><br/>" + safe_str(us_data.get('data_rilevazione', '')), styNormal)
    data_rielaborazione = Paragraph("<b>DATA RIELABORAZIONE</b><br/>" + safe_str(us_data.get('data_rielaborazione', '')), styNormal)
    
    # Create USM cell_schema
    cell_schema = [
        # Row 0-1: Headers
        [unita_tipo, '01', label_ente_responsabile, '03', '04', '05', '06', '07', '08', '09', '10', label_unita_stratigrafica, '12', '13', '14', '15', '16', '17'],
        ['00', '01', sop, '03', '04', '05', '06', '07', '08', '09', '10', label_sas, '12', '13', '14', '15', '16', '17'],
        
        # Row 2: Site
        [sito, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
        
        # Row 3: Area and saggio
        [area, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', saggio, '12', '13', '14', '15', '16', '17'],
        
        # Row 4: Location details
        [ambiente, '01', '02', '03', posizione, '04', '06', settore, '08', quadrato, '10', quote, '12', '13', '14', '15', '16', '17'],
        
        # Row 5: Documentation
        [piante, '01', '02', '03', prospetti, '05', '06', sezioni, '08', '09', '10', foto, '12', '13', '14', '15', '16', '17'],
        
        # Row 6-8: USM specific fields
        [t_muraria, '01', '02', '03', '04', '05', '06', t_costruttiva, '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
        [sezione_muraria, '01', '02', '03', '04', '05', '06', modulo, '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
        [misure, '01', '02', '03', '04', '05', '06', superficie_analizzata, '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
        
        # Row 9-10: Definition and criteria
        [d_stratigrafica, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
        [criteri_distinzione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
        
        # Row 11-13: Materials and conservation
        [provenienza_materiali, '01', '02', '03', '04', '05', '06', orientamento, '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
        [uso_primario, '01', '02', '03', reimpiego, '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
        [stato_conservazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
        
        # Row 14-16: Brick and stone materials
        [materiali, '01', '02', lavorazione, '04', consistenza, '06', '07', forma, '09', colore, '11', impasto, '13', '14', posa_opera, '16', '17'],
        [label_laterizi, materiali_1, '02', lavorazione_1, '04', consistenza_1, '06', '07', forma_1, '09', colore_1, '11', impasto_1, '13', '14', posa_opera_1, '16', '17'],
        [label_pietra, p_1, '02', p_2, '04', p_3, '06', '07', p_4, '09', p_5, '11', taglio, '13', '14', p_7, '16', '17'],
        
        # Row 17: Materials notes
        [note_materiali, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
        
        # Row 18-20: Mortar section
        [n, tipo, '02', '03', consistenza_l, '05', '06', inerti, '08', '09', colore_l, '11', spessore, '13', '14', rifinitura, '16', '17'],
        [label_legante, tipo_1, '02', '03', consistenza_2, '05', '06', inerti_4, '08', '09', colore_3, '11', spessore_5, '13', '14', rifinitura_6, '16', '17'],
        [note_legante, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
        
        # Row 21-30: Stratigraphic relationships
        [uguale_a, '01', '02', '03', '04', '05', si_lega_a, '07', '08', '09', '10', '11', label_sequenza_stratigrafica, posteriore_a, '14', '15', '16', '17'],
        ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
        [gli_si_appoggia, '01', '02', '03', '04', '05', si_appoggia_a, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
        ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
        [coperto_da, '01', '02', '03', '04', '05', copre, '07', '08', '09', '10', '11', '12', anteriore_a, '14', '15', '16', '17'],
        ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
        [tagliato_da, '01', '02', '03', '04', '05', taglia, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
        ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
        [riempito_da, '01', '02', '03', '04', '05', riempie, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
        ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
        
        # Row 31-33: Description fields
        [descrizione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
        [osservazioni, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
        [interpretazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
        
        # Row 34-36: Dating and samples
        [datazione_ipotesi, '01', '02', '03', '04', '05', periodo_o_fase, '07', '08', '09', '10', '11', attivita, '13', '14', '15', '16', '17'],
        [elementi_datanti, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
        [campioni_pietra, '01', '02', '03', '04', '05', campioni_mattone, '07', '08', '09', '10', '11', campioni_malta, '13', '14', '15', '16', '17'],
        
        # Row 37-40: Responsibility fields
        [affidabilita, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
        [direttore, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
        [data_rilievo, '01', '02', '03', '04', '05', '06', '07', '08', responsabile, '10', '11', '12', '13', '14', '15', '16', '17'],
        [data_rielaborazione, '01', '02', '03', '04', '05', '06', '07', '08', responsabile2, '10', '11', '12', '13', '14', '15', '16', '17'],
    ]
    
    # Apply the USM table style (using the one from your table_style)
    table_style = [
        ('GRID', (0, 0), (-1, -1), 0.3, colors.black),
        # 0 row
        ('SPAN', (0, 0), (1, 1)),  # unita tipo
        ('VALIGN', (0, 0), (1, 1), 'MIDDLE'),
        
        ('SPAN', (2, 0), (10, 0)),  # label ente responsabile
        ('SPAN', (11, 0), (17, 0)),  # label unita stratigrafica
        ('VALIGN', (2, 0), (12, 1), 'TOP'),
        
        # 1 row
        ('SPAN', (2, 1), (10, 1)),  # soprintendenza
        ('SPAN', (11, 1), (17, 1)),  # label_sas
        ('VALIGN', (2, 0), (17, 1), 'TOP'),
        
        # 2 row
        ('SPAN', (0, 2), (17, 2)),  # sito
        ('VALIGN', (0, 2), (17, 2), 'TOP'),
        
        # 3 row
        ('SPAN', (0, 3), (10, 3)),  # area
        ('SPAN', (11, 3), (17, 3)),  # saggio
        ('VALIGN', (0, 3), (17, 3), 'TOP'),
        
        # 4 row
        ('SPAN', (0, 4), (3, 4)),  # ambiente
        ('SPAN', (4, 4), (6, 4)),  # posizione
        ('SPAN', (7, 4), (9, 4)),  # settore
        ('SPAN', (10, 4), (10, 4)),  # quadrato
        ('SPAN', (11, 4), (17, 4)),  # quote
        ('VALIGN', (0, 4), (17, 4), 'TOP'),
        
        # 5 row documentation
        ('SPAN', (0, 5), (3, 5)),  # piante
        ('SPAN', (4, 5), (6, 5)),  # prospetti
        ('SPAN', (7, 5), (10, 5)),  # sezioni
        ('SPAN', (11, 5), (17, 5)),  # foto
        ('VALIGN', (0, 5), (17, 5), 'TOP'),
        
        # 6 row - USM specific
        ('SPAN', (0, 6), (6, 6)),  # t_muraria
        ('SPAN', (7, 6), (17, 6)),  # t_costruttiva
        ('VALIGN', (0, 6), (17, 6), 'TOP'),
        
        # 7 row
        ('SPAN', (0, 7), (6, 7)),  # sezione_muraria
        ('SPAN', (7, 7), (17, 7)),  # modulo
        ('VALIGN', (0, 7), (17, 7), 'TOP'),
        
        # 8 row
        ('SPAN', (0, 8), (6, 8)),  # misure
        ('SPAN', (7, 8), (17, 8)),  # superficie_analizzata
        ('VALIGN', (0, 8), (17, 8), 'TOP'),
        
        # 9 row
        ('SPAN', (0, 9), (17, 9)),  # d_stratigrafica
        ('VALIGN', (0, 9), (17, 9), 'TOP'),
        
        # 10 row
        ('SPAN', (0, 10), (17, 10)),  # criteri_distinzione
        ('VALIGN', (0, 10), (17, 10), 'TOP'),
        
        # 11 row
        ('SPAN', (0, 11), (6, 11)),  # provenienza_materiali
        ('SPAN', (7, 11), (17, 11)),  # orientamento
        ('VALIGN', (0, 11), (17, 11), 'TOP'),
        
        # 12 row
        ('SPAN', (0, 12), (3, 12)),  # uso_primario
        ('SPAN', (4, 12), (6, 12)),  # reimpiego
        ('VALIGN', (0, 12), (17, 12), 'TOP'),
        
        # 13 row
        ('SPAN', (0, 13), (17, 13)),  # stato_conservazione
        ('VALIGN', (0, 13), (17, 13), 'TOP'),
        
        # 14 row - materials headers
        ('SPAN', (0, 14), (2, 14)),  # materiali
        ('SPAN', (3, 14), (4, 14)),  # lavorazione
        ('SPAN', (5, 14), (7, 14)),  # consistenza
        ('SPAN', (8, 14), (9, 14)),  # forma
        ('SPAN', (10, 14), (11, 14)),  # colore
        ('SPAN', (12, 14), (14, 14)),  # impasto
        ('SPAN', (15, 14), (17, 14)),  # posa_opera
        ('VALIGN', (0, 14), (17, 14), 'TOP'),
        
        # 15-16 rows - brick and stone data
        ('SPAN', (0, 15), (0, 15)),  # label_laterizi
        ('SPAN', (1, 15), (2, 15)),  # materiali_1
        ('SPAN', (3, 15), (4, 15)),  # lavorazione_1
        ('SPAN', (5, 15), (7, 15)),  # consistenza_1
        ('SPAN', (8, 15), (9, 15)),  # forma_1
        ('SPAN', (10, 15), (11, 15)),  # colore_1
        ('SPAN', (12, 15), (14, 15)),  # impasto_1
        ('SPAN', (15, 15), (17, 15)),  # posa_opera_1
        ('VALIGN', (0, 15), (17, 15), 'TOP'),
        
        ('SPAN', (0, 16), (0, 16)),  # label_pietra
        ('SPAN', (1, 16), (2, 16)),  # p_1
        ('SPAN', (3, 16), (4, 16)),  # p_2
        ('SPAN', (5, 16), (7, 16)),  # p_3
        ('SPAN', (8, 16), (9, 16)),  # p_4
        ('SPAN', (10, 16), (11, 16)),  # p_5
        ('SPAN', (12, 16), (14, 16)),  # taglio
        ('SPAN', (15, 16), (17, 16)),  # p_7
        ('VALIGN', (0, 16), (17, 16), 'TOP'),
        
        # 17 row
        ('SPAN', (0, 17), (17, 17)),  # note_materiali
        ('VALIGN', (0, 17), (17, 17), 'TOP'),
        
        # 18 row - mortar headers
        ('SPAN', (0, 18), (0, 18)),  # n
        ('SPAN', (1, 18), (3, 18)),  # tipo
        ('SPAN', (4, 18), (6, 18)),  # consistenza_l
        ('SPAN', (7, 18), (9, 18)),  # inerti
        ('SPAN', (10, 18), (11, 18)),  # colore_l
        ('SPAN', (12, 18), (14, 18)),  # spessore
        ('SPAN', (15, 18), (17, 18)),  # rifinitura
        ('VALIGN', (0, 18), (17, 18), 'TOP'),
        
        # 19 row - mortar data
        ('SPAN', (0, 19), (0, 19)),  # label_legante
        ('SPAN', (1, 19), (3, 19)),  # tipo_1
        ('SPAN', (4, 19), (6, 19)),  # consistenza_2
        ('SPAN', (7, 19), (9, 19)),  # inerti_4
        ('SPAN', (10, 19), (11, 19)),  # colore_3
        ('SPAN', (12, 19), (14, 19)),  # spessore_5
        ('SPAN', (15, 19), (17, 19)),  # rifinitura_6
        ('VALIGN', (0, 19), (17, 19), 'TOP'),
        
        # 20 row
        ('SPAN', (0, 20), (17, 20)),  # note_legante
        ('VALIGN', (0, 20), (17, 20), 'TOP'),
        
        # 21-30 rows - stratigraphic relationships
        ('SPAN', (0, 21), (5, 22)),    # uguale a
        ('SPAN', (0, 23), (5, 24)),    # gli si appoggia
        ('SPAN', (0, 25), (5, 26)),    # coperto da
        ('SPAN', (0, 27), (5, 28)),    # tagliato da
        ('SPAN', (0, 29), (5, 30)),    # riempito da
        ('SPAN', (6, 21), (11, 22)),   # si lega a
        ('SPAN', (6, 23), (11, 24)),   # si appoggia a
        ('SPAN', (6, 25), (11, 26)),   # copre
        ('SPAN', (6, 27), (11, 28)),   # taglia
        ('SPAN', (6, 29), (11, 30)),   # riempie
        ('SPAN', (12, 21), (12, 30)),  # label sequenza stratigrafica
        ('SPAN', (13, 21), (17, 25)),  # posteriore a
        ('SPAN', (13, 26), (17, 30)),  # anteriore a
        ('VALIGN', (0, 21), (17, 30), 'TOP'),
        
        # 31-33 rows - descriptions
        ('SPAN', (0, 31), (17, 31)),  # descrizione
        ('VALIGN', (0, 31), (17, 31), 'TOP'),
        
        ('SPAN', (0, 32), (17, 32)),  # osservazioni
        ('VALIGN', (0, 32), (17, 32), 'TOP'),
        
        ('SPAN', (0, 33), (17, 33)),  # interpretazione
        ('VALIGN', (0, 33), (17, 33), 'TOP'),
        
        # 34 row - dating
        ('SPAN', (0, 34), (5, 34)),  # datazione_ipotesi
        ('SPAN', (6, 34), (11, 34)),  # periodo_o_fase
        ('SPAN', (12, 34), (17, 34)),  # attivita
        ('VALIGN', (0, 34), (17, 34), 'TOP'),
        
        # 35 row
        ('SPAN', (0, 35), (17, 35)),  # elementi_datanti
        ('VALIGN', (0, 35), (17, 35), 'TOP'),
        
        # 36 row - samples
        ('SPAN', (0, 36), (5, 36)),  # campioni_pietra
        ('SPAN', (6, 36), (11, 36)),  # campioni_mattone
        ('SPAN', (12, 36), (17, 36)),  # campioni_malta
        ('VALIGN', (0, 36), (17, 36), 'TOP'),
        
        # 37 row
        ('SPAN', (0, 37), (17, 37)),  # affidabilita
        ('VALIGN', (0, 37), (17, 37), 'TOP'),
        
        # 38 row
        ('SPAN', (0, 38), (17, 38)),  # direttore
        ('VALIGN', (0, 38), (17, 38), 'TOP'),
        
        # 39 row
        ('SPAN', (0, 39), (8, 39)),  # data_rilievo
        ('SPAN', (9, 39), (17, 39)),  # responsabile
        ('VALIGN', (0, 39), (17, 39), 'TOP'),
        
        # 40 row
        ('SPAN', (0, 40), (8, 40)),  # data_rielaborazione
        ('SPAN', (9, 40), (17, 40)),  # responsabile2
        ('VALIGN', (0, 40), (17, 40), 'TOP'),
    ]
    
    rowHeights = None
    
    usm_table = Table(cell_schema, colWidths=colWidths, rowHeights=rowHeights, style=table_style)
    story.append(usm_table)