#!/usr/bin/env python3
"""
Flask Web Interface for PyArchInit-Mini
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from flask_login import login_required, current_user
from flask_socketio import SocketIO
from wtforms import StringField, TextAreaField, IntegerField, SelectField, FileField, BooleanField
from wtforms.validators import DataRequired, Optional
from werkzeug.utils import secure_filename
import tempfile
import base64

# PyArchInit-Mini imports
import sys
sys.path.append('..')
from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.services.site_service import SiteService
from pyarchinit_mini.services.us_service import USService
from pyarchinit_mini.services.inventario_service import InventarioService
from pyarchinit_mini.services.thesaurus_service import ThesaurusService
from pyarchinit_mini.services.user_service import UserService
from pyarchinit_mini.services.analytics_service import AnalyticsService
from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
from pyarchinit_mini.harris_matrix.matrix_visualizer import MatrixVisualizer
from pyarchinit_mini.harris_matrix.pyarchinit_visualizer import PyArchInitMatrixVisualizer
from pyarchinit_mini.utils.stratigraphic_validator import StratigraphicValidator
from pyarchinit_mini.pdf_export.pdf_generator import PDFGenerator
from pyarchinit_mini.media_manager.media_handler import MediaHandler
from pyarchinit_mini.graphml_converter import convert_dot_content_to_graphml

# Import authentication routes
from auth_routes import auth_bp, init_login_manager, write_permission_required

# Import WebSocket events
from socketio_events import (
    init_socketio_events,
    broadcast_site_created,
    broadcast_site_updated,
    broadcast_site_deleted,
    broadcast_us_created,
    broadcast_us_updated,
    broadcast_us_deleted,
    broadcast_inventario_created,
    broadcast_inventario_updated,
    broadcast_inventario_deleted
)

# Forms
class SiteForm(FlaskForm):
    sito = StringField('Nome Sito', validators=[DataRequired()])
    nazione = StringField('Nazione')
    regione = StringField('Regione')
    comune = StringField('Comune')
    provincia = StringField('Provincia')
    definizione_sito = StringField('Definizione Sito')
    descrizione = TextAreaField('Descrizione')

class USForm(FlaskForm):
    # TAB 1: Informazioni Base
    # Identificazione
    sito = SelectField('Sito', validators=[DataRequired()], coerce=str)
    area = StringField('Area')
    us = IntegerField('Numero US', validators=[DataRequired()])
    unita_tipo = SelectField('Tipo Unità', choices=[
        ('', '-- Seleziona --'),
        ('US', 'US'),
        ('USM', 'USM'),
        ('USV', 'USV'),
        ('USR', 'USR')
    ])

    # Dati di Scavo
    anno_scavo = IntegerField('Anno Scavo', validators=[Optional()])
    scavato = SelectField('Scavato', choices=[
        ('', '-- Seleziona --'),
        ('Sì', 'Sì'),
        ('No', 'No'),
        ('Parzialmente', 'Parzialmente')
    ])
    schedatore = StringField('Schedatore')
    metodo_di_scavo = SelectField('Metodo di Scavo', choices=[
        ('', '-- Seleziona --'),
        ('Manuale', 'Manuale'),
        ('Meccanico', 'Meccanico'),
        ('Misto', 'Misto')
    ])
    data_schedatura = StringField('Data Schedatura', description='Formato: AAAA-MM-GG')
    attivita = StringField('Attività')

    # Responsabili
    direttore_us = StringField('Direttore US')
    responsabile_us = StringField('Responsabile US')

    # Contesto
    settore = StringField('Settore')
    quad_par = StringField('Quadrato/Partizione')
    ambient = StringField('Ambiente')
    saggio = StringField('Saggio')

    # Catalogazione ICCD
    n_catalogo_generale = StringField('N. Catalogo Generale')
    n_catalogo_interno = StringField('N. Catalogo Interno')
    n_catalogo_internazionale = StringField('N. Catalogo Internazionale')
    soprintendenza = StringField('Soprintendenza')

    # TAB 2: Descrizioni
    d_stratigrafica = TextAreaField('Descrizione Stratigrafica')
    d_interpretativa = TextAreaField('Descrizione Interpretativa')
    descrizione = TextAreaField('Descrizione Dettagliata')
    interpretazione = TextAreaField('Interpretazione')
    osservazioni = TextAreaField('Osservazioni')

    # TAB 3: Caratteristiche Fisiche
    formazione = SelectField('Formazione', choices=[
        ('', '-- Seleziona --'),
        ('Naturale', 'Naturale'),
        ('Artificiale', 'Artificiale'),
        ('Mista', 'Mista')
    ])
    stato_di_conservazione = SelectField('Stato di Conservazione', choices=[
        ('', '-- Seleziona --'),
        ('Ottimo', 'Ottimo'),
        ('Buono', 'Buono'),
        ('Discreto', 'Discreto'),
        ('Cattivo', 'Cattivo')
    ])
    colore = StringField('Colore')
    consistenza = SelectField('Consistenza', choices=[
        ('', '-- Seleziona --'),
        ('Compatta', 'Compatta'),
        ('Semicompatta', 'Semicompatta'),
        ('Sciolta', 'Sciolta')
    ])
    struttura = StringField('Struttura')

    # Misure
    quota_relativa = StringField('Quota Relativa')
    quota_abs = StringField('Quota Assoluta')
    lunghezza_max = StringField('Lunghezza Max (cm)')
    larghezza_media = StringField('Larghezza Media (cm)')
    altezza_max = StringField('Altezza Max (cm)')
    altezza_min = StringField('Altezza Min (cm)')
    profondita_max = StringField('Profondità Max (cm)')
    profondita_min = StringField('Profondità Min (cm)')

    # TAB 4: Cronologia
    periodo_iniziale = SelectField('Periodo Iniziale', choices=[
        ('', '-- Seleziona --'),
        ('Paleolitico', 'Paleolitico'),
        ('Mesolitico', 'Mesolitico'),
        ('Neolitico', 'Neolitico'),
        ('Eneolitico', 'Eneolitico'),
        ('Bronzo Antico', 'Bronzo Antico'),
        ('Bronzo Medio', 'Bronzo Medio'),
        ('Bronzo Finale', 'Bronzo Finale'),
        ('Ferro I', 'Ferro I'),
        ('Ferro II', 'Ferro II'),
        ('Orientalizzante', 'Orientalizzante'),
        ('Arcaico', 'Arcaico'),
        ('Classico', 'Classico'),
        ('Ellenistico', 'Ellenistico'),
        ('Romano Repubblicano', 'Romano Repubblicano'),
        ('Romano Imperiale', 'Romano Imperiale'),
        ('Tardo Antico', 'Tardo Antico'),
        ('Altomedievale', 'Altomedievale'),
        ('Medievale', 'Medievale'),
        ('Postmedievale', 'Postmedievale'),
        ('Moderno', 'Moderno'),
        ('Contemporaneo', 'Contemporaneo')
    ])
    fase_iniziale = StringField('Fase Iniziale')
    periodo_finale = SelectField('Periodo Finale', choices=[
        ('', '-- Seleziona --'),
        ('Paleolitico', 'Paleolitico'),
        ('Mesolitico', 'Mesolitico'),
        ('Neolitico', 'Neolitico'),
        ('Eneolitico', 'Eneolitico'),
        ('Bronzo Antico', 'Bronzo Antico'),
        ('Bronzo Medio', 'Bronzo Medio'),
        ('Bronzo Finale', 'Bronzo Finale'),
        ('Ferro I', 'Ferro I'),
        ('Ferro II', 'Ferro II'),
        ('Orientalizzante', 'Orientalizzante'),
        ('Arcaico', 'Arcaico'),
        ('Classico', 'Classico'),
        ('Ellenistico', 'Ellenistico'),
        ('Romano Repubblicano', 'Romano Repubblicano'),
        ('Romano Imperiale', 'Romano Imperiale'),
        ('Tardo Antico', 'Tardo Antico'),
        ('Altomedievale', 'Altomedievale'),
        ('Medievale', 'Medievale'),
        ('Postmedievale', 'Postmedievale'),
        ('Moderno', 'Moderno'),
        ('Contemporaneo', 'Contemporaneo')
    ])
    fase_finale = StringField('Fase Finale')
    datazione = StringField('Datazione')
    affidabilita = SelectField('Affidabilità', choices=[
        ('', '-- Seleziona --'),
        ('Alta', 'Alta'),
        ('Media', 'Media'),
        ('Bassa', 'Bassa')
    ])

    # TAB 5: Relazioni Stratigrafiche
    rapporti = TextAreaField('Rapporti Stratigrafici',
                            description='Formato: copre 1002, taglia 1005, si appoggia a 1010')

    # TAB 6: Documentazione
    inclusi = TextAreaField('Inclusi')
    campioni = TextAreaField('Campioni')
    documentazione = TextAreaField('Documentazione')
    cont_per = TextAreaField('Contenitori/Contenuti')

    # Altri campi
    flottazione = SelectField('Flottazione', choices=[
        ('', '-- Seleziona --'),
        ('Sì', 'Sì'),
        ('No', 'No')
    ])
    setacciatura = SelectField('Setacciatura', choices=[
        ('', '-- Seleziona --'),
        ('Sì', 'Sì'),
        ('No', 'No')
    ])

class InventarioForm(FlaskForm):
    # TAB 1: Identificazione
    sito = SelectField('Sito', validators=[DataRequired()], coerce=str)
    numero_inventario = IntegerField('Numero Inventario', validators=[DataRequired()])
    n_reperto = IntegerField('N. Reperto', validators=[Optional()])
    schedatore = StringField('Schedatore')
    date_scheda = StringField('Data Scheda', description='Formato: AAAA-MM-GG')
    years = IntegerField('Anno', validators=[Optional()])

    # TAB 2: Classificazione
    tipo_reperto = SelectField('Tipo Reperto', choices=[])  # Populated from thesaurus
    criterio_schedatura = StringField('Criterio Schedatura')
    definizione = StringField('Definizione')
    tipo = StringField('Tipo')
    tipo_contenitore = StringField('Tipo Contenitore')
    struttura = StringField('Struttura')
    descrizione = TextAreaField('Descrizione')

    # TAB 3: Contesto
    area = StringField('Area')
    us = StringField('US')  # Text field as per model
    punto_rinv = StringField('Punto Rinvenimento')
    elementi_reperto = TextAreaField('Elementi Reperto')

    # TAB 4: Caratteristiche Fisiche
    stato_conservazione = SelectField('Stato di Conservazione', choices=[])  # From thesaurus
    lavato = SelectField('Lavato', choices=[
        ('', '-- Seleziona --'),
        ('Sì', 'Sì'),
        ('No', 'No')
    ])
    nr_cassa = StringField('N. Cassa')
    luogo_conservazione = StringField('Luogo di Conservazione')

    # TAB 5: Conservazione e Gestione
    repertato = SelectField('Repertato', choices=[
        ('', '-- Seleziona --'),
        ('Sì', 'Sì'),
        ('No', 'No')
    ])
    diagnostico = SelectField('Diagnostico', choices=[
        ('', '-- Seleziona --'),
        ('Sì', 'Sì'),
        ('No', 'No')
    ])

    # TAB 6: Caratteristiche Ceramiche
    corpo_ceramico = SelectField('Corpo Ceramico', choices=[])  # From thesaurus
    rivestimento = SelectField('Rivestimento', choices=[])  # From thesaurus
    diametro_orlo = StringField('Diametro Orlo (cm)')
    eve_orlo = StringField('EVE Orlo')

    # TAB 7: Misurazioni
    peso = StringField('Peso (g)')
    forme_minime = IntegerField('Forme Minime', validators=[Optional()])
    forme_massime = IntegerField('Forme Massime', validators=[Optional()])
    totale_frammenti = IntegerField('Totale Frammenti', validators=[Optional()])
    misurazioni = TextAreaField('Misurazioni')

    # TAB 8: Documentazione
    datazione_reperto = StringField('Datazione Reperto')
    rif_biblio = TextAreaField('Riferimenti Bibliografici')
    tecnologie = TextAreaField('Tecnologie')
    negativo_photo = StringField('Negativo Fotografico')
    diapositiva = StringField('Diapositiva')

class MediaUploadForm(FlaskForm):
    entity_type = SelectField('Tipo Entità', choices=[
        ('site', 'Sito'),
        ('us', 'US'),
        ('inventario', 'Inventario')
    ], validators=[DataRequired()])
    entity_id = IntegerField('ID Entità', validators=[DataRequired()])
    file = FileField('File', validators=[DataRequired()])
    description = TextAreaField('Descrizione')
    author = StringField('Autore/Fotografo')

class DatabaseUploadForm(FlaskForm):
    """Form for uploading SQLite database files"""
    database_file = FileField('Database SQLite (.db)', validators=[DataRequired()])
    database_name = StringField('Nome Database', validators=[DataRequired()],
                               description='Nome identificativo per questo database')
    description = TextAreaField('Descrizione',
                               description='Descrizione opzionale del database')

class DatabaseConnectionForm(FlaskForm):
    """Form for PostgreSQL database connections"""
    db_type = SelectField('Tipo Database', choices=[
        ('postgresql', 'PostgreSQL'),
        ('sqlite', 'SQLite (file locale)')
    ], validators=[DataRequired()])

    # PostgreSQL fields
    host = StringField('Host', description='Es: localhost, 192.168.1.100')
    port = IntegerField('Porta', description='Default: 5432 (PostgreSQL)')
    database = StringField('Nome Database', validators=[DataRequired()])
    username = StringField('Username')
    password = StringField('Password')

    # SQLite fields
    sqlite_path = StringField('Percorso File SQLite',
                             description='Es: /path/to/database.db')

    connection_name = StringField('Nome Connessione', validators=[DataRequired()],
                                 description='Nome identificativo per questa connessione')

class GraphMLExportForm(FlaskForm):
    """Form for GraphML export of Harris Matrix"""
    site = SelectField('Sito', validators=[DataRequired()], coerce=str)
    title = StringField('Titolo Diagramma', description='Intestazione opzionale per il diagramma')
    grouping = SelectField('Raggruppamento', choices=[
        ('period_area', 'Periodo + Area'),
        ('period', 'Solo Periodo'),
        ('area', 'Solo Area'),
        ('none', 'Nessun Raggruppamento')
    ], default='period_area')
    reverse_epochs = BooleanField('Inverti ordine periodi', default=False)

# Flask App Setup
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['DATABASE_FOLDER'] = 'databases'  # Folder for uploaded databases

    # Initialize CSRF protection
    csrf = CSRFProtect(app)

    # Create necessary folders
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DATABASE_FOLDER'], exist_ok=True)

    # Initialize database
    # Default to project root database, not current directory
    default_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pyarchinit_mini.db')
    default_db_url = f"sqlite:///{default_db_path}"
    database_url = os.getenv("DATABASE_URL", default_db_url)
    print(f"[FLASK] Current working directory: {os.getcwd()}")
    print(f"[FLASK] Using database: {database_url}")
    # If SQLite, show absolute path
    if database_url.startswith('sqlite:///'):
        db_path = database_url.replace('sqlite:///', '')
        if not db_path.startswith('/'):
            abs_path = os.path.abspath(db_path)
            print(f"[FLASK] SQLite absolute path: {abs_path}")
            print(f"[FLASK] Database exists: {os.path.exists(abs_path)}")
    db_conn = DatabaseConnection.from_url(database_url)
    db_conn.create_tables()
    db_manager = DatabaseManager(db_conn)
    print(f"[FLASK] Database connection initialized")

    # Store current database info in app config
    app.config['CURRENT_DATABASE_URL'] = database_url
    app.config['DATABASE_CONNECTIONS'] = {}  # Store named connections
    
    # Initialize services
    site_service = SiteService(db_manager)
    us_service = USService(db_manager)
    inventario_service = InventarioService(db_manager)
    thesaurus_service = ThesaurusService(db_manager)
    user_service = UserService(db_manager)
    analytics_service = AnalyticsService(db_manager)
    matrix_generator = HarrisMatrixGenerator(db_manager, us_service)  # Pass us_service for proper matrix generation
    matrix_visualizer = MatrixVisualizer()
    graphviz_visualizer = PyArchInitMatrixVisualizer()  # Graphviz visualizer (desktop GUI style)
    pdf_generator = PDFGenerator()
    media_handler = MediaHandler()

    # Store user service in app for authentication
    app.user_service = user_service

    # Initialize Flask-Login
    init_login_manager(app, user_service)

    # Register authentication blueprint
    app.register_blueprint(auth_bp)

    # Initialize Flask-SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")

    # Initialize WebSocket event handlers
    init_socketio_events(socketio)

    # Store socketio in app for access in routes
    app.socketio = socketio

    # Helper function to get thesaurus values
    def get_thesaurus_choices(field_name, table_name='inventario_materiali_table'):
        """Get thesaurus choices for a field"""
        try:
            values = thesaurus_service.get_field_values(table_name, field_name)
            return [('', '-- Seleziona --')] + [(v['value'], v['label']) for v in values]
        except Exception:
            # Return empty list if thesaurus not available
            return [('', '-- Seleziona --')]
    
    # Routes
    @app.route('/')
    @login_required
    def index():
        """Dashboard with statistics"""
        try:
            # Get basic statistics
            sites = site_service.get_all_sites(size=5)
            total_sites = site_service.count_sites()
            total_us = us_service.count_us()
            total_inventory = inventario_service.count_inventario()
            
            stats = {
                'total_sites': total_sites,
                'total_us': total_us,
                'total_inventory': total_inventory,
                'recent_sites': sites
            }
            
            return render_template('dashboard.html', stats=stats)
        except Exception as e:
            flash(f'Errore caricamento dashboard: {str(e)}', 'error')
            return render_template('dashboard.html', stats={})

    @app.route('/analytics')
    @login_required
    def analytics():
        """Analytics dashboard with charts"""
        try:
            # Get all analytics data
            analytics_data = analytics_service.get_complete_dashboard_data()

            return render_template('analytics/dashboard.html', data=analytics_data)
        except Exception as e:
            flash(f'Errore caricamento analytics: {str(e)}', 'error')
            return redirect(url_for('index'))

    # Sites routes
    @app.route('/sites')
    @login_required
    def sites_list():
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        
        if search:
            sites = site_service.search_sites(search, page=page, size=20)
        else:
            sites = site_service.get_all_sites(page=page, size=20)
        
        total = site_service.count_sites()
        
        return render_template('sites/list.html', sites=sites, total=total, 
                             page=page, search=search)
    
    @app.route('/sites/create', methods=['GET', 'POST'])
    @login_required
    @write_permission_required
    def create_site():
        form = SiteForm()
        
        if form.validate_on_submit():
            try:
                site_data = {
                    'sito': form.sito.data,
                    'nazione': form.nazione.data,
                    'regione': form.regione.data,
                    'comune': form.comune.data,
                    'provincia': form.provincia.data,
                    'definizione_sito': form.definizione_sito.data,
                    'descrizione': form.descrizione.data
                }
                
                site = site_service.create_site(site_data)

                # Try to get site ID, use None if instance is detached
                try:
                    site_id = site.id_sito
                except Exception:
                    site_id = None

                # Broadcast site creation
                broadcast_site_created(socketio, site_data['sito'], site_id)

                flash(f'Sito "{site_data["sito"]}" creato con successo!', 'success')
                return redirect(url_for('sites_list'))
                
            except Exception as e:
                flash(f'Errore nella creazione del sito: {str(e)}', 'error')
        
        return render_template('sites/form.html', form=form, title='Nuovo Sito')

    @app.route('/sites/<int:site_id>/edit', methods=['GET', 'POST'])
    @login_required
    @write_permission_required
    def edit_site(site_id):
        """Edit existing site"""
        form = SiteForm()

        # Get existing site
        site = site_service.get_site_dto_by_id(site_id)
        if not site:
            flash('Sito non trovato', 'error')
            return redirect(url_for('sites_list'))

        if form.validate_on_submit():
            try:
                update_data = {
                    'sito': form.sito.data,
                    'nazione': form.nazione.data,
                    'regione': form.regione.data,
                    'comune': form.comune.data,
                    'provincia': form.provincia.data,
                    'definizione_sito': form.definizione_sito.data,
                    'descrizione': form.descrizione.data
                }

                updated_site = site_service.update_site(site_id, update_data)

                flash(f'Sito "{update_data["sito"]}" aggiornato con successo!', 'success')
                return redirect(url_for('sites_list'))

            except Exception as e:
                flash(f'Errore nell\'aggiornamento del sito: {str(e)}', 'error')

        # Pre-populate form with existing data
        elif request.method == 'GET':
            form.sito.data = site.sito
            form.nazione.data = site.nazione
            form.regione.data = site.regione
            form.comune.data = site.comune
            form.provincia.data = site.provincia
            form.definizione_sito.data = site.definizione_sito
            form.descrizione.data = site.descrizione

        return render_template('sites/form.html', form=form, title='Modifica Sito', edit_mode=True)

    @app.route('/sites/<int:site_id>')
    @login_required
    def view_site(site_id):
        # Get site and related data within session scope
        with db_manager.connection.get_session() as session:
            from pyarchinit_mini.models.site import Site as SiteModel
            from pyarchinit_mini.models.us import US as USModel
            from pyarchinit_mini.models.inventario_materiali import InventarioMateriali as InvModel

            site = session.query(SiteModel).filter(SiteModel.id_sito == site_id).first()
            if not site:
                flash('Sito non trovato', 'error')
                return redirect(url_for('sites_list'))

            site_name = site.sito

            # Get related data and convert to dicts within session
            us_records = session.query(USModel).filter(USModel.sito == site_name).limit(50).all()
            us_list = [us.to_dict() for us in us_records]

            inv_records = session.query(InvModel).filter(InvModel.sito == site_name).limit(50).all()
            inventory_list = [inv.to_dict() for inv in inv_records]

            # Convert site to dict
            site_dict = site.to_dict()

        # Use dicts outside session
        return render_template('sites/detail.html', site=site_dict,
                             us_list=us_list, inventory_list=inventory_list)
    
    # US routes
    @app.route('/us')
    @login_required
    def us_list():
        page = request.args.get('page', 1, type=int)
        sito_filter = request.args.get('sito', '')
        
        filters = {}
        if sito_filter:
            filters['sito'] = sito_filter
        
        us_list = us_service.get_all_us(page=page, size=20, filters=filters)
        total = us_service.count_us(filters=filters)
        
        # Get sites for filter
        sites = site_service.get_all_sites(size=100)
        
        return render_template('us/list.html', us_list=us_list, sites=sites,
                             total=total, page=page, sito_filter=sito_filter)
    
    @app.route('/us/create', methods=['GET', 'POST'])
    @login_required
    @write_permission_required
    def create_us():
        form = USForm()
        
        # Populate site choices
        sites = site_service.get_all_sites(size=100)
        form.sito.choices = [('', '-- Seleziona Sito --')] + [(s.sito, s.sito) for s in sites]
        
        if form.validate_on_submit():
            try:
                # Helper function to convert numeric fields
                def to_float(value):
                    if value and str(value).strip():
                        try:
                            return float(value)
                        except (ValueError, TypeError):
                            return None
                    return None

                us_data = {
                    # TAB 1: Informazioni Base
                    'sito': form.sito.data,
                    'area': form.area.data,
                    'us': form.us.data,
                    'unita_tipo': form.unita_tipo.data,
                    'anno_scavo': form.anno_scavo.data,
                    'scavato': form.scavato.data,
                    'schedatore': form.schedatore.data,
                    'metodo_di_scavo': form.metodo_di_scavo.data,
                    'data_schedatura': form.data_schedatura.data,
                    'attivita': form.attivita.data,
                    'direttore_us': form.direttore_us.data,
                    'responsabile_us': form.responsabile_us.data,
                    'settore': form.settore.data,
                    'quad_par': form.quad_par.data,
                    'ambient': form.ambient.data,
                    'saggio': form.saggio.data,
                    'n_catalogo_generale': form.n_catalogo_generale.data,
                    'n_catalogo_interno': form.n_catalogo_interno.data,
                    'n_catalogo_internazionale': form.n_catalogo_internazionale.data,
                    'soprintendenza': form.soprintendenza.data,

                    # TAB 2: Descrizioni
                    'd_stratigrafica': form.d_stratigrafica.data,
                    'd_interpretativa': form.d_interpretativa.data,
                    'descrizione': form.descrizione.data,
                    'interpretazione': form.interpretazione.data,
                    'osservazioni': form.osservazioni.data,

                    # TAB 3: Caratteristiche Fisiche
                    'formazione': form.formazione.data,
                    'stato_di_conservazione': form.stato_di_conservazione.data,
                    'colore': form.colore.data,
                    'consistenza': form.consistenza.data,
                    'struttura': form.struttura.data,
                    'quota_relativa': to_float(form.quota_relativa.data),
                    'quota_abs': to_float(form.quota_abs.data),
                    'lunghezza_max': to_float(form.lunghezza_max.data),
                    'larghezza_media': to_float(form.larghezza_media.data),
                    'altezza_max': to_float(form.altezza_max.data),
                    'altezza_min': to_float(form.altezza_min.data),
                    'profondita_max': to_float(form.profondita_max.data),
                    'profondita_min': to_float(form.profondita_min.data),

                    # TAB 4: Cronologia
                    'periodo_iniziale': form.periodo_iniziale.data,
                    'fase_iniziale': form.fase_iniziale.data,
                    'periodo_finale': form.periodo_finale.data,
                    'fase_finale': form.fase_finale.data,
                    'datazione': form.datazione.data,
                    'affidabilita': form.affidabilita.data,

                    # TAB 5: Relazioni Stratigrafiche
                    'rapporti': form.rapporti.data,

                    # TAB 6: Documentazione
                    'inclusi': form.inclusi.data,
                    'campioni': form.campioni.data,
                    'documentazione': form.documentazione.data,
                    'cont_per': form.cont_per.data,

                    # Altri campi
                    'flottazione': form.flottazione.data,
                    'setacciatura': form.setacciatura.data,
                }

                us = us_service.create_us(us_data)

                # Broadcast US creation (use data from form, not from detached instance)
                broadcast_us_created(socketio, us_data['sito'], us_data['us'])

                flash(f'US {us_data["us"]} creata con successo!', 'success')
                return redirect(url_for('us_list'))

            except Exception as e:
                flash(f'Errore nella creazione US: {str(e)}', 'error')
        elif request.method == 'POST':
            # Form validation failed - show errors
            flash('Errore nella validazione del form. Controlla i campi obbligatori.', 'error')
            print(f"Form validation errors: {form.errors}")
        
        return render_template('us/form.html', form=form, title='Nuova US')

    @app.route('/us/<int:us_id>/edit', methods=['GET', 'POST'])
    @login_required
    @write_permission_required
    def edit_us(us_id):
        """Edit existing US"""
        form = USForm()

        # Populate site choices
        sites = site_service.get_all_sites(size=100)
        form.sito.choices = [('', '-- Seleziona Sito --')] + [(s.sito, s.sito) for s in sites]

        # Get existing US
        us = us_service.get_us_dto_by_id(us_id)
        if not us:
            flash('US non trovata', 'error')
            return redirect(url_for('us_list'))

        if form.validate_on_submit():
            try:
                # Helper function to convert numeric fields
                def to_float(value):
                    if value and str(value).strip():
                        try:
                            return float(value)
                        except (ValueError, TypeError):
                            return None
                    return None

                update_data = {
                    # TAB 1: Informazioni Base
                    'sito': form.sito.data,
                    'area': form.area.data,
                    'us': form.us.data,
                    'unita_tipo': form.unita_tipo.data,
                    'anno_scavo': form.anno_scavo.data,
                    'scavato': form.scavato.data,
                    'schedatore': form.schedatore.data,
                    'metodo_di_scavo': form.metodo_di_scavo.data,
                    'data_schedatura': form.data_schedatura.data,
                    'attivita': form.attivita.data,
                    'direttore_us': form.direttore_us.data,
                    'responsabile_us': form.responsabile_us.data,
                    'settore': form.settore.data,
                    'quad_par': form.quad_par.data,
                    'ambient': form.ambient.data,
                    'saggio': form.saggio.data,
                    'n_catalogo_generale': form.n_catalogo_generale.data,
                    'n_catalogo_interno': form.n_catalogo_interno.data,
                    'n_catalogo_internazionale': form.n_catalogo_internazionale.data,
                    'soprintendenza': form.soprintendenza.data,

                    # TAB 2: Descrizioni
                    'd_stratigrafica': form.d_stratigrafica.data,
                    'd_interpretativa': form.d_interpretativa.data,
                    'descrizione': form.descrizione.data,
                    'interpretazione': form.interpretazione.data,
                    'osservazioni': form.osservazioni.data,

                    # TAB 3: Caratteristiche Fisiche
                    'formazione': form.formazione.data,
                    'stato_di_conservazione': form.stato_di_conservazione.data,
                    'colore': form.colore.data,
                    'consistenza': form.consistenza.data,
                    'struttura': form.struttura.data,
                    'quota_relativa': to_float(form.quota_relativa.data),
                    'quota_abs': to_float(form.quota_abs.data),
                    'lunghezza_max': to_float(form.lunghezza_max.data),
                    'larghezza_media': to_float(form.larghezza_media.data),
                    'altezza_max': to_float(form.altezza_max.data),
                    'altezza_min': to_float(form.altezza_min.data),
                    'profondita_max': to_float(form.profondita_max.data),
                    'profondita_min': to_float(form.profondita_min.data),

                    # TAB 4: Cronologia
                    'periodo_iniziale': form.periodo_iniziale.data,
                    'fase_iniziale': form.fase_iniziale.data,
                    'periodo_finale': form.periodo_finale.data,
                    'fase_finale': form.fase_finale.data,
                    'datazione': form.datazione.data,
                    'affidabilita': form.affidabilita.data,

                    # TAB 5: Relazioni Stratigrafiche
                    'rapporti': form.rapporti.data,

                    # TAB 6: Documentazione
                    'inclusi': form.inclusi.data,
                    'campioni': form.campioni.data,
                    'documentazione': form.documentazione.data,
                    'cont_per': form.cont_per.data,

                    # Altri campi
                    'flottazione': form.flottazione.data,
                    'setacciatura': form.setacciatura.data,
                }

                us_service.update_us(us_id, update_data)

                flash(f'US {update_data["us"]} aggiornata con successo!', 'success')
                return redirect(url_for('us_list'))

            except Exception as e:
                flash(f'Errore nell\'aggiornamento US: {str(e)}', 'error')

        # Pre-populate form with existing data
        elif request.method == 'GET':
            form.sito.data = us.sito
            form.area.data = us.area
            form.us.data = us.us
            form.unita_tipo.data = us.unita_tipo
            form.anno_scavo.data = us.anno_scavo
            form.scavato.data = us.scavato
            form.schedatore.data = us.schedatore
            form.metodo_di_scavo.data = us.metodo_di_scavo
            form.data_schedatura.data = us.data_schedatura
            form.attivita.data = us.attivita
            form.direttore_us.data = us.direttore_us
            form.responsabile_us.data = us.responsabile_us
            form.settore.data = us.settore
            form.quad_par.data = us.quad_par
            form.ambient.data = us.ambient
            form.saggio.data = us.saggio
            form.n_catalogo_generale.data = us.n_catalogo_generale
            form.n_catalogo_interno.data = us.n_catalogo_interno
            form.n_catalogo_internazionale.data = us.n_catalogo_internazionale
            form.soprintendenza.data = us.soprintendenza
            form.d_stratigrafica.data = us.d_stratigrafica
            form.d_interpretativa.data = us.d_interpretativa
            form.descrizione.data = us.descrizione
            form.interpretazione.data = us.interpretazione
            form.osservazioni.data = us.osservazioni
            form.formazione.data = us.formazione
            form.stato_di_conservazione.data = us.stato_di_conservazione
            form.colore.data = us.colore
            form.consistenza.data = us.consistenza
            form.struttura.data = us.struttura
            form.quota_relativa.data = us.quota_relativa
            form.quota_abs.data = us.quota_abs
            form.lunghezza_max.data = us.lunghezza_max
            form.larghezza_media.data = us.larghezza_media
            form.altezza_max.data = us.altezza_max
            form.altezza_min.data = us.altezza_min
            form.profondita_max.data = us.profondita_max
            form.profondita_min.data = us.profondita_min
            form.periodo_iniziale.data = us.periodo_iniziale
            form.fase_iniziale.data = us.fase_iniziale
            form.periodo_finale.data = us.periodo_finale
            form.fase_finale.data = us.fase_finale
            form.datazione.data = us.datazione
            form.affidabilita.data = us.affidabilita
            form.rapporti.data = us.rapporti
            form.inclusi.data = us.inclusi
            form.campioni.data = us.campioni
            form.documentazione.data = us.documentazione
            form.cont_per.data = us.cont_per
            form.flottazione.data = us.flottazione
            form.setacciatura.data = us.setacciatura

        return render_template('us/form.html', form=form, title='Modifica US', edit_mode=True)

    # Inventory routes
    @app.route('/inventario')
    @login_required
    def inventario_list():
        page = request.args.get('page', 1, type=int)
        sito_filter = request.args.get('sito', '')
        tipo_filter = request.args.get('tipo', '')
        
        filters = {}
        if sito_filter:
            filters['sito'] = sito_filter
        if tipo_filter:
            filters['tipo_reperto'] = tipo_filter
        
        inventory_list = inventario_service.get_all_inventario(page=page, size=20, filters=filters)
        total = inventario_service.count_inventario(filters=filters)
        
        # Get options for filters
        sites = site_service.get_all_sites(size=100)
        
        return render_template('inventario/list.html', inventory_list=inventory_list,
                             sites=sites, total=total, page=page,
                             sito_filter=sito_filter, tipo_filter=tipo_filter)
    
    @app.route('/inventario/create', methods=['GET', 'POST'])
    @login_required
    @write_permission_required
    def create_inventario():
        form = InventarioForm()

        # Populate site choices
        sites = site_service.get_all_sites(size=100)
        form.sito.choices = [('', '-- Seleziona Sito --')] + [(s.sito, s.sito) for s in sites]

        # Populate thesaurus choices
        form.tipo_reperto.choices = get_thesaurus_choices('tipo_reperto')
        form.stato_conservazione.choices = get_thesaurus_choices('stato_conservazione')
        form.corpo_ceramico.choices = get_thesaurus_choices('corpo_ceramico')
        form.rivestimento.choices = get_thesaurus_choices('rivestimento')

        if form.validate_on_submit():
            try:
                # Helper function to convert numeric fields
                def to_float(value):
                    if value and str(value).strip():
                        try:
                            return float(value)
                        except (ValueError, TypeError):
                            return None
                    return None

                def to_int(value):
                    if value and str(value).strip():
                        try:
                            return int(value)
                        except (ValueError, TypeError):
                            return None
                    return None

                inv_data = {
                    # TAB 1: Identificazione
                    'sito': form.sito.data,
                    'numero_inventario': form.numero_inventario.data,
                    'n_reperto': form.n_reperto.data,
                    'schedatore': form.schedatore.data,
                    'date_scheda': form.date_scheda.data,
                    'years': form.years.data,

                    # TAB 2: Classificazione
                    'tipo_reperto': form.tipo_reperto.data,
                    'criterio_schedatura': form.criterio_schedatura.data,
                    'definizione': form.definizione.data,
                    'tipo': form.tipo.data,
                    'tipo_contenitore': form.tipo_contenitore.data,
                    'struttura': form.struttura.data,
                    'descrizione': form.descrizione.data,

                    # TAB 3: Contesto
                    'area': form.area.data,
                    'us': form.us.data,
                    'punto_rinv': form.punto_rinv.data,
                    'elementi_reperto': form.elementi_reperto.data,

                    # TAB 4: Caratteristiche Fisiche
                    'stato_conservazione': form.stato_conservazione.data,
                    'lavato': form.lavato.data,
                    'nr_cassa': form.nr_cassa.data,
                    'luogo_conservazione': form.luogo_conservazione.data,

                    # TAB 5: Conservazione e Gestione
                    'repertato': form.repertato.data,
                    'diagnostico': form.diagnostico.data,

                    # TAB 6: Caratteristiche Ceramiche
                    'corpo_ceramico': form.corpo_ceramico.data,
                    'rivestimento': form.rivestimento.data,
                    'diametro_orlo': to_float(form.diametro_orlo.data),
                    'eve_orlo': to_float(form.eve_orlo.data),

                    # TAB 7: Misurazioni
                    'peso': to_float(form.peso.data),
                    'forme_minime': form.forme_minime.data,
                    'forme_massime': form.forme_massime.data,
                    'totale_frammenti': form.totale_frammenti.data,
                    'misurazioni': form.misurazioni.data,

                    # TAB 8: Documentazione
                    'datazione_reperto': form.datazione_reperto.data,
                    'rif_biblio': form.rif_biblio.data,
                    'tecnologie': form.tecnologie.data,
                    'negativo_photo': form.negativo_photo.data,
                    'diapositiva': form.diapositiva.data,
                }

                item = inventario_service.create_inventario(inv_data)

                # Broadcast inventario creation (use data from form, not from detached instance)
                broadcast_inventario_created(socketio, inv_data['numero_inventario'], inv_data['sito'])

                flash(f'Reperto {inv_data["numero_inventario"]} creato con successo!', 'success')
                return redirect(url_for('inventario_list'))

            except Exception as e:
                flash(f'Errore nella creazione reperto: {str(e)}', 'error')
        elif request.method == 'POST':
            # Form validation failed - show errors
            flash('Errore nella validazione del form. Controlla i campi obbligatori.', 'error')
            print(f"Form validation errors: {form.errors}")

        return render_template('inventario/form.html', form=form, title='Nuovo Reperto')

    @app.route('/inventario/<int:inv_id>/edit', methods=['GET', 'POST'])
    @login_required
    @write_permission_required
    def edit_inventario(inv_id):
        """Edit existing inventario"""
        form = InventarioForm()

        # Populate site choices
        sites = site_service.get_all_sites(size=100)
        form.sito.choices = [('', '-- Seleziona Sito --')] + [(s.sito, s.sito) for s in sites]

        # Populate thesaurus choices
        form.tipo_reperto.choices = get_thesaurus_choices('tipo_reperto')
        form.stato_conservazione.choices = get_thesaurus_choices('stato_conservazione')
        form.corpo_ceramico.choices = get_thesaurus_choices('corpo_ceramico')
        form.rivestimento.choices = get_thesaurus_choices('rivestimento')

        # Get existing inventario using session to access all fields
        with db_manager.connection.get_session() as session:
            from pyarchinit_mini.models.inventario_materiali import InventarioMateriali as InvModel
            inv = session.query(InvModel).filter(InvModel.id_invmat == inv_id).first()

            if not inv:
                flash('Reperto non trovato', 'error')
                return redirect(url_for('inventario_list'))

            # Pre-populate form with existing data (inside session to avoid detached instance)
            if request.method == 'GET':
                form.sito.data = inv.sito
                form.numero_inventario.data = inv.numero_inventario
                form.n_reperto.data = inv.n_reperto
                form.schedatore.data = inv.schedatore
                form.date_scheda.data = inv.date_scheda
                form.years.data = inv.years
                form.tipo_reperto.data = inv.tipo_reperto
                form.criterio_schedatura.data = inv.criterio_schedatura
                form.definizione.data = inv.definizione
                form.tipo.data = inv.tipo
                form.tipo_contenitore.data = inv.tipo_contenitore
                form.struttura.data = inv.struttura
                form.descrizione.data = inv.descrizione
                form.area.data = inv.area
                form.us.data = inv.us
                form.punto_rinv.data = inv.punto_rinv
                form.elementi_reperto.data = inv.elementi_reperto
                form.stato_conservazione.data = inv.stato_conservazione
                form.lavato.data = inv.lavato
                form.nr_cassa.data = inv.nr_cassa
                form.luogo_conservazione.data = inv.luogo_conservazione
                form.repertato.data = inv.repertato
                form.diagnostico.data = inv.diagnostico
                form.corpo_ceramico.data = inv.corpo_ceramico
                form.rivestimento.data = inv.rivestimento
                form.diametro_orlo.data = inv.diametro_orlo
                form.eve_orlo.data = inv.eve_orlo
                form.peso.data = inv.peso
                form.forme_minime.data = inv.forme_minime
                form.forme_massime.data = inv.forme_massime
                form.totale_frammenti.data = inv.totale_frammenti
                form.misurazioni.data = inv.misurazioni
                form.datazione_reperto.data = inv.datazione_reperto
                form.rif_biblio.data = inv.rif_biblio
                form.tecnologie.data = inv.tecnologie
                form.negativo_photo.data = inv.negativo_photo
                form.diapositiva.data = inv.diapositiva

        if form.validate_on_submit():
            try:
                # Helper function to convert numeric fields
                def to_float(value):
                    if value and str(value).strip():
                        try:
                            return float(value)
                        except (ValueError, TypeError):
                            return None
                    return None

                def to_int(value):
                    if value and str(value).strip():
                        try:
                            return int(value)
                        except (ValueError, TypeError):
                            return None
                    return None

                update_data = {
                    # TAB 1: Identificazione
                    'sito': form.sito.data,
                    'numero_inventario': form.numero_inventario.data,
                    'n_reperto': form.n_reperto.data,
                    'schedatore': form.schedatore.data,
                    'date_scheda': form.date_scheda.data,
                    'years': form.years.data,

                    # TAB 2: Classificazione
                    'tipo_reperto': form.tipo_reperto.data,
                    'criterio_schedatura': form.criterio_schedatura.data,
                    'definizione': form.definizione.data,
                    'tipo': form.tipo.data,
                    'tipo_contenitore': form.tipo_contenitore.data,
                    'struttura': form.struttura.data,
                    'descrizione': form.descrizione.data,

                    # TAB 3: Contesto
                    'area': form.area.data,
                    'us': form.us.data,
                    'punto_rinv': form.punto_rinv.data,
                    'elementi_reperto': form.elementi_reperto.data,

                    # TAB 4: Caratteristiche Fisiche
                    'stato_conservazione': form.stato_conservazione.data,
                    'lavato': form.lavato.data,
                    'nr_cassa': form.nr_cassa.data,
                    'luogo_conservazione': form.luogo_conservazione.data,

                    # TAB 5: Conservazione e Gestione
                    'repertato': form.repertato.data,
                    'diagnostico': form.diagnostico.data,

                    # TAB 6: Caratteristiche Ceramiche
                    'corpo_ceramico': form.corpo_ceramico.data,
                    'rivestimento': form.rivestimento.data,
                    'diametro_orlo': to_float(form.diametro_orlo.data),
                    'eve_orlo': to_float(form.eve_orlo.data),

                    # TAB 7: Misurazioni
                    'peso': to_float(form.peso.data),
                    'forme_minime': form.forme_minime.data,
                    'forme_massime': form.forme_massime.data,
                    'totale_frammenti': form.totale_frammenti.data,
                    'misurazioni': form.misurazioni.data,

                    # TAB 8: Documentazione
                    'datazione_reperto': form.datazione_reperto.data,
                    'rif_biblio': form.rif_biblio.data,
                    'tecnologie': form.tecnologie.data,
                    'negativo_photo': form.negativo_photo.data,
                    'diapositiva': form.diapositiva.data,
                }

                inventario_service.update_inventario(inv_id, update_data)

                flash(f'Reperto {update_data["numero_inventario"]} aggiornato con successo!', 'success')
                return redirect(url_for('inventario_list'))

            except Exception as e:
                flash(f'Errore nell\'aggiornamento reperto: {str(e)}', 'error')

        return render_template('inventario/form.html', form=form, title='Modifica Reperto', edit_mode=True)

    # Harris Matrix routes
    @app.route('/harris_matrix/<site_name>')
    def harris_matrix(site_name):
        """Harris Matrix with matplotlib visualizer (default)"""
        try:
            # Generate matrix
            graph = matrix_generator.generate_matrix(site_name)
            levels = matrix_generator.get_matrix_levels(graph)
            stats = matrix_generator.get_matrix_statistics(graph)

            # Generate visualization
            matrix_image = matrix_visualizer.render_matplotlib(graph, levels)

            return render_template('harris_matrix/view.html',
                                 site_name=site_name,
                                 matrix_image=matrix_image,
                                 stats=stats,
                                 levels=levels,
                                 visualizer='matplotlib')

        except Exception as e:
            flash(f'Errore generazione Harris Matrix: {str(e)}', 'error')
            return redirect(url_for('sites_list'))

    @app.route('/harris_matrix/<site_name>/graphviz')
    def harris_matrix_graphviz(site_name):
        """Harris Matrix with Graphviz visualizer (desktop GUI style)"""
        try:
            # Get grouping parameter (period_area, period, area, none)
            grouping = request.args.get('grouping', 'period_area')

            # Generate matrix
            graph = matrix_generator.generate_matrix(site_name)
            levels = matrix_generator.get_matrix_levels(graph)
            stats = matrix_generator.get_matrix_statistics(graph)

            # Generate visualization with Graphviz
            output_path = graphviz_visualizer.create_matrix(
                graph,
                grouping=grouping,
                settings={
                    'show_legend': True,
                    'show_periods': grouping != 'none'
                }
            )

            # Read image and encode to base64
            with open(output_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')

            # Clean up temp file
            if os.path.exists(output_path):
                os.remove(output_path)

            return render_template('harris_matrix/view_graphviz.html',
                                 site_name=site_name,
                                 matrix_image=image_data,
                                 stats=stats,
                                 levels=levels,
                                 visualizer='graphviz',
                                 grouping=grouping)

        except Exception as e:
            import traceback
            traceback.print_exc()
            flash(f'Errore generazione Harris Matrix Graphviz: {str(e)}', 'error')
            return redirect(url_for('sites_list'))

    # GraphML Export routes
    @app.route('/harris_matrix/graphml_export', methods=['GET', 'POST'])
    @login_required
    def export_harris_graphml():
        """Export Harris Matrix to GraphML format (yEd compatible)"""
        form = GraphMLExportForm()

        # Populate site choices
        sites = site_service.get_all_sites()
        form.site.choices = [(s.sito, s.sito) for s in sites]

        if form.validate_on_submit():
            try:
                site_name = form.site.data
                title = form.title.data or site_name
                grouping = form.grouping.data
                reverse_epochs = form.reverse_epochs.data

                # Generate Harris Matrix graph (with transitive reduction already applied)
                graph = matrix_generator.generate_matrix(site_name)

                # Generate DOT manually with GraphML-compatible node ID format
                # GraphML converter requires: US_number_description_epoch
                # This allows it to extract epoch and create y:Row elements for period grouping

                # Get all relevant US
                us_rilevanti = set()
                for source, target in graph.edges():
                    us_rilevanti.add(source)
                    us_rilevanti.add(target)

                # Start DOT
                dot_lines = []
                dot_lines.append('digraph {')
                dot_lines.append('\trankdir=BT')

                # Extract unique periods for y:Row generation
                periodi_unici = set()
                for node in us_rilevanti:
                    if node in graph.nodes:
                        periodo = graph.nodes[node].get('period_initial', graph.nodes[node].get('periodo_iniziale', 'Sconosciuto'))
                        periodi_unici.add(periodo.replace(' ', '-'))  # Use dash

                # Add period label nodes (required by GraphML converter to create y:Row elements)
                for periodo in sorted(periodi_unici):
                    dot_lines.append(f'\t"Periodo : {periodo}" [shape=plaintext]')

                # EM_palette node styles mapping based on unita_tipo
                US_STYLES = {
                    'US': {  # Stratigraphic Unit (strato, riempimento, etc.)
                        'shape': 'box',
                        'fillcolor': '#FFFFFF',
                        'color': '#9B3333',  # red border
                        'penwidth': '4.0',
                        'style': 'filled'
                    },
                    'USM': {  # Unità Stratigrafica Muraria (masonry)
                        'shape': 'box',
                        'fillcolor': '#FFFFFF',
                        'color': '#9B3333',  # red border
                        'penwidth': '4.0',
                        'style': 'filled'
                    },
                    'USD': {  # Documentary US
                        'shape': 'box',
                        'fillcolor': '#FFFFFF',
                        'color': '#D86400',  # orange border
                        'penwidth': '4.0',
                        'style': 'rounded,filled'
                    },
                    'USV': {  # Virtual US negative
                        'shape': 'hexagon',
                        'fillcolor': '#000000',
                        'color': '#31792D',  # green border
                        'penwidth': '4.0',
                        'style': 'filled'
                    },
                    'USV/s': {  # Virtual US structural
                        'shape': 'trapezium',  # closest to parallelogram
                        'fillcolor': '#000000',
                        'color': '#248FE7',  # blue border
                        'penwidth': '4.0',
                        'style': 'filled'
                    },
                    'default': {  # Fallback for unknown types
                        'shape': 'box',
                        'fillcolor': '#CCCCFF',
                        'color': '#000000',
                        'penwidth': '2.0',
                        'style': 'filled'
                    }
                }

                # Create nodes with GraphML-compatible format + EM_palette styles
                # Node ID: US_1001_Description_Period
                # Node label: US1001_Period (period included for get_y() to work)
                for node in sorted(us_rilevanti):
                    if node not in graph.nodes:
                        continue

                    node_data = graph.nodes[node]
                    periodo = node_data.get('period_initial', node_data.get('periodo_iniziale', 'Sconosciuto'))
                    d_stratigrafica = node_data.get('d_stratigrafica', node_data.get('description', ''))
                    d_interpretativa = node_data.get('d_interpretativa', node_data.get('interpretation', ''))
                    unita_tipo = node_data.get('unita_tipo', 'US')  # Extract unit type

                    # Build node tooltip/description: d_stratigrafica + d_interpretativa
                    node_description_parts = []
                    if d_stratigrafica:
                        node_description_parts.append(d_stratigrafica)
                    if d_interpretativa:
                        node_description_parts.append(d_interpretativa)
                    node_description = ' - '.join(node_description_parts) if node_description_parts else ''

                    # Clean description and period (remove spaces and special chars)
                    desc_clean = d_stratigrafica.replace(' ', '_').replace(',', '').replace('"', '')
                    if len(desc_clean) > 30:
                        desc_clean = desc_clean[:30]

                    # Clean period: replace spaces with dash (not underscore)
                    # This allows rsplit('_', 1) to extract the full period name
                    periodo_clean = periodo.replace(' ', '-')  # Romano Imperiale → Romano-Imperiale

                    # Node ID format: US_numero_descrizione_periodo
                    # rsplit('_', 1) will extract "Romano-Imperiale" correctly
                    node_id = f"US_{node}_{desc_clean}_{periodo_clean}"

                    # Label: Include period for get_y() to work
                    # Format: US1001_Romano-Imperiale (so get_y can find the period in LabelText)
                    label = f"US{node}_{periodo_clean}"

                    # Get style for this node based on unita_tipo
                    style_dict = US_STYLES.get(unita_tipo, US_STYLES['default'])

                    # Build node attributes
                    attrs = [
                        f'label="{label}"',
                        f'fillcolor="{style_dict["fillcolor"]}"',
                        f'color="{style_dict["color"]}"',
                        f'shape={style_dict["shape"]}',
                        f'penwidth={style_dict["penwidth"]}',
                        f'style={style_dict["style"]}'
                    ]

                    # Add tooltip with node description (d_stratigrafica + d_interpretativa)
                    if node_description:
                        # Clean description for DOT format (escape quotes)
                        desc_escaped = node_description.replace('"', '\\"').replace('\n', '\\n')
                        attrs.append(f'tooltip="{desc_escaped}"')

                    # Add node with EM_palette styling
                    dot_lines.append(f'\t"{node_id}" [{", ".join(attrs)}]')

                # Add edges with EM_palette styling based on relationship type
                for source, target in graph.edges():
                    if source not in graph.nodes or target not in graph.nodes:
                        continue

                    edge_data = graph.get_edge_data(source, target)
                    rel_type = edge_data.get('relationship', edge_data.get('type', 'sopra'))

                    source_data = graph.nodes[source]
                    target_data = graph.nodes[target]

                    source_periodo = source_data.get('period_initial', source_data.get('periodo_iniziale', 'Sconosciuto'))
                    target_periodo = target_data.get('period_initial', target_data.get('periodo_iniziale', 'Sconosciuto'))

                    source_desc = source_data.get('d_stratigrafica', source_data.get('description', ''))
                    target_desc = target_data.get('d_stratigrafica', target_data.get('description', ''))

                    desc_source_clean = source_desc.replace(' ', '_').replace(',', '').replace('"', '')[:30]
                    desc_target_clean = target_desc.replace(' ', '_').replace(',', '').replace('"', '')[:30]

                    # Clean periods (use dash, not underscore)
                    source_periodo_clean = source_periodo.replace(' ', '-')
                    target_periodo_clean = target_periodo.replace(' ', '-')

                    source_id = f"US_{source}_{desc_source_clean}_{source_periodo_clean}"
                    target_id = f"US_{target}_{desc_target_clean}_{target_periodo_clean}"

                    # Determine edge attributes based on relationship type
                    # Following PyArchInit convention for EM_palette
                    rel_lower = rel_type.lower()
                    edge_attrs = []

                    # Contemporary relationships (uguale a, si lega a): NO arrow (arrowhead=none)
                    if 'uguale' in rel_lower or 'lega' in rel_lower or 'same' in rel_lower or 'connected' in rel_lower:
                        edge_attrs.append('dir=none')  # No arrowhead in either direction
                    # Negative relationships (taglia): dashed line with arrow
                    elif 'taglia' in rel_lower or 'tagli' in rel_lower or 'cut' in rel_lower:
                        edge_attrs.append('style=dashed')
                        edge_attrs.append('arrowhead=normal')
                    # Virtual or uncertain relationships: dashed line
                    elif 'virtuale' in rel_lower or 'dubbio' in rel_lower or 'virtual' in rel_lower or 'uncertain' in rel_lower:
                        edge_attrs.append('style=dashed')
                        edge_attrs.append('arrowhead=normal')
                    # Normal stratigraphic relationships (copre, sotto, etc.): solid line with arrow
                    else:
                        edge_attrs.append('arrowhead=normal')

                    # Build edge with styling (NO label - as per user request)
                    # Optionally add relationship type as tooltip
                    if rel_type:
                        edge_attrs.append(f'tooltip="{rel_type}"')

                    edge_attr_str = ', '.join(edge_attrs) if edge_attrs else ''
                    if edge_attr_str:
                        dot_lines.append(f'\t"{source_id}" -> "{target_id}" [{edge_attr_str}]')
                    else:
                        dot_lines.append(f'\t"{source_id}" -> "{target_id}"')

                dot_lines.append('}')
                dot_content = '\n'.join(dot_lines)

                # Convert to GraphML
                graphml_content = convert_dot_content_to_graphml(
                    dot_content,
                    title=title,
                    reverse_epochs=reverse_epochs
                )

                # Post-process GraphML to clean node labels (remove period from label)
                # Change "US1001_Medievale" to "US1001"
                if graphml_content:
                    import re
                    # Pattern: <y:NodeLabel...>US1234_Period-Name</y:NodeLabel>
                    # Replace with: <y:NodeLabel...>US1234</y:NodeLabel>
                    graphml_content = re.sub(
                        r'(>US\d+)_[^<]+(<\/y:NodeLabel>)',
                        r'\1\2',
                        graphml_content
                    )

                    # Apply EM_palette colors to nodes based on unita_tipo
                    # AND add node descriptions (d_stratigrafica + d_interpretativa)
                    try:
                        import xml.dom.minidom as minidom

                        # Build unita_tipo map and description map from graph
                        unita_tipo_map = {}
                        description_map = {}
                        for node in us_rilevanti:
                            if node in graph.nodes:
                                node_data = graph.nodes[node]
                                unita_tipo_map[node] = node_data.get('unita_tipo', 'US')

                                # Build description: d_stratigrafica + d_interpretativa
                                d_strat = node_data.get('d_stratigrafica', node_data.get('description', ''))
                                d_interp = node_data.get('d_interpretativa', node_data.get('interpretation', ''))
                                desc_parts = []
                                if d_strat:
                                    desc_parts.append(d_strat)
                                if d_interp:
                                    desc_parts.append(d_interp)
                                if desc_parts:
                                    description_map[node] = ' - '.join(desc_parts)

                        # Parse and modify GraphML
                        dom = minidom.parseString(graphml_content)
                        nodes_modified = 0
                        descriptions_added = 0

                        # Find all ShapeNode elements (US nodes)
                        for shape_node in dom.getElementsByTagName('y:ShapeNode'):
                            # Find the label
                            labels = shape_node.getElementsByTagName('y:NodeLabel')
                            if not labels or not labels[0].firstChild:
                                continue

                            label_text = labels[0].firstChild.nodeValue
                            match = re.match(r'US(\d+)', label_text)
                            if not match:
                                continue

                            us_number = int(match.group(1))
                            unita_tipo = unita_tipo_map.get(us_number, 'US')

                            # Get colors from US_STYLES
                            style = US_STYLES.get(unita_tipo, US_STYLES['default'])

                            # Update Fill color
                            fill_nodes = shape_node.getElementsByTagName('y:Fill')
                            if fill_nodes:
                                fill_nodes[0].setAttribute('color', style['fillcolor'])
                                nodes_modified += 1

                            # Update BorderStyle color and width
                            border_nodes = shape_node.getElementsByTagName('y:BorderStyle')
                            if border_nodes:
                                border_nodes[0].setAttribute('color', style['color'])
                                border_nodes[0].setAttribute('width', style['penwidth'])

                            # Add description (d_stratigrafica + d_interpretativa) to node
                            if us_number in description_map:
                                # Navigate to parent <node> element
                                # Structure: <node> -> <data key="d6"> -> <y:ShapeNode>
                                # Note: In the GraphML generated, d5 = description, d6 = nodegraphics
                                data_element = shape_node.parentNode
                                node_element = data_element.parentNode

                                # Check if <data key="d5"> already exists (description field)
                                existing_desc = None
                                for child in node_element.childNodes:
                                    if child.nodeType == child.ELEMENT_NODE and child.tagName == 'data':
                                        if child.getAttribute('key') == 'd5':
                                            existing_desc = child
                                            break

                                # Create or update description element
                                description_text = description_map[us_number]
                                if existing_desc:
                                    # Update existing (usually empty)
                                    if existing_desc.firstChild:
                                        existing_desc.firstChild.nodeValue = description_text
                                    else:
                                        # Create text node if missing
                                        text_node = dom.createTextNode(description_text)
                                        existing_desc.appendChild(text_node)
                                    descriptions_added += 1
                                else:
                                    # Create new <data key="d5"> element
                                    desc_element = dom.createElement('data')
                                    desc_element.setAttribute('key', 'd5')
                                    desc_element.setAttribute('xml:space', 'preserve')
                                    desc_text_node = dom.createTextNode(description_text)
                                    desc_element.appendChild(desc_text_node)
                                    # Insert before <data key="d6"> (graphics data)
                                    node_element.insertBefore(desc_element, data_element)
                                    descriptions_added += 1

                        graphml_content = dom.toxml()
                        flash(f'Stili EM_palette applicati a {nodes_modified} nodi, {descriptions_added} descrizioni aggiunte', 'success')
                    except Exception as style_error:
                        # Non-fatal: continue even if styling fails
                        flash(f'Avviso: impossibile applicare stili EM_palette: {str(style_error)}', 'warning')

                if graphml_content is None:
                    flash('Errore durante la conversione a GraphML', 'error')
                    return render_template('harris_matrix/graphml_export.html', form=form)

                # Create temporary file for download
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.graphml', delete=False) as f:
                    f.write(graphml_content)
                    temp_path = f.name

                # Send file
                filename = f"{site_name}_harris_matrix.graphml"
                response = send_file(
                    temp_path,
                    mimetype='application/xml',
                    as_attachment=True,
                    download_name=filename
                )

                # Clean up temp file after sending
                @response.call_on_close
                def cleanup():
                    try:
                        os.remove(temp_path)
                    except:
                        pass

                return response

            except Exception as e:
                import traceback
                traceback.print_exc()
                flash(f'Errore durante l\'export GraphML: {str(e)}', 'error')
                return render_template('harris_matrix/graphml_export.html', form=form)

        return render_template('harris_matrix/graphml_export.html', form=form)

    # Stratigraphic Validation routes
    @app.route('/validate/<site_name>')
    def validate_stratigraphic(site_name):
        """Validate stratigraphic relationships for a site"""
        try:
            # Get all US for the site
            filters = {'sito': site_name}
            us_list = us_service.get_all_us(size=1000, filters=filters)

            # Initialize validator
            validator = StratigraphicValidator()

            # Add all units to validator
            for us in us_list:
                us_num = getattr(us, 'us', None)
                if us_num:
                    validator.add_unit(us_num, {
                        'sito': getattr(us, 'sito', ''),
                        'area': getattr(us, 'area', ''),
                        'd_stratigrafica': getattr(us, 'd_stratigrafica', ''),
                        'rapporti': getattr(us, 'rapporti', '')
                    })

                    # Parse and add relationships
                    rapporti = getattr(us, 'rapporti', '')
                    if rapporti:
                        relationships = validator.parse_relationships(us_num, rapporti)
                        for rel_type, target_us in relationships:
                            validator.add_relationship(us_num, target_us, rel_type)

            # Convert US list to dict format for validation
            us_list_dicts = []
            for us in us_list:
                us_dict = {
                    'sito': getattr(us, 'sito', ''),
                    'area': getattr(us, 'area', ''),
                    'us': getattr(us, 'us', None),
                    'rapporti': getattr(us, 'rapporti', '')
                }
                us_list_dicts.append(us_dict)

            # Get validation report
            report = validator.get_validation_report(us_list_dicts)

            # Get statistics
            stats = {
                'total_us': len(us_list),
                'total_relationships': report.get('relationships_found', 0),
                'total_errors': report.get('error_count', 0),
                'total_cycles': 0,  # Feature not implemented in validator
                'missing_reciprocals': 0,  # Feature not implemented in validator
                'is_valid': report.get('valid', False)
            }

            # Return simplified report (cycles and missing_reciprocals not available)
            return render_template('validation/report.html',
                                 site_name=site_name,
                                 stats=stats,
                                 errors=report.get('errors', []),
                                 cycles=[],  # Feature not implemented
                                 missing_reciprocals=[])  # Feature not implemented

        except Exception as e:
            import traceback
            traceback.print_exc()
            flash(f'Errore validazione: {str(e)}', 'error')
            return redirect(url_for('sites_list'))

    @app.route('/validate/<site_name>/fix', methods=['POST'])
    def fix_stratigraphic(site_name):
        """Apply automatic fixes to stratigraphic relationships"""
        try:
            fix_type = request.form.get('fix_type', 'reciprocals')

            # Get all US for the site
            filters = {'sito': site_name}
            us_list_objects = us_service.get_all_us(size=1000, filters=filters)

            # Convert to dict for validator
            us_list = []
            for us in us_list_objects:
                us_dict = {
                    'sito': getattr(us, 'sito', ''),
                    'area': getattr(us, 'area', ''),
                    'us': getattr(us, 'us', None),
                    'rapporti': getattr(us, 'rapporti', '')
                }
                us_list.append(us_dict)

            # Initialize validator
            validator = StratigraphicValidator()

            if fix_type == 'reciprocals':
                # Generate fixes for missing reciprocals
                fixes = validator.generate_relationship_fixes(us_list)

                # Apply updates to existing US
                updates_count = 0
                for update in fixes.get('updates', []):
                    us_num = update['us']
                    new_rapporti = update['rapporti']

                    # Update US in database
                    us_service.update_us(
                        {'sito': site_name, 'us': us_num},
                        {'rapporti': new_rapporti}
                    )
                    updates_count += 1

                # Create new US if needed
                creates_count = len(fixes.get('creates', []))

                flash(f'Fix applicati: {updates_count} US aggiornate, {creates_count} US da creare manualmente', 'success')

            return redirect(url_for('validate_stratigraphic', site_name=site_name))

        except Exception as e:
            import traceback
            traceback.print_exc()
            flash(f'Errore applicazione fix: {str(e)}', 'error')
            return redirect(url_for('validate_stratigraphic', site_name=site_name))

    # Export routes
    @app.route('/export/site_pdf/<int:site_id>')
    def export_site_pdf(site_id):
        try:
            # Get site data and convert to dict within session scope
            with db_manager.connection.get_session() as session:
                from pyarchinit_mini.models.site import Site as SiteModel
                from pyarchinit_mini.models.us import US as USModel
                from pyarchinit_mini.models.inventario_materiali import InventarioMateriali as InvModel

                site = session.query(SiteModel).filter(SiteModel.id_sito == site_id).first()
                if not site:
                    flash('Sito non trovato', 'error')
                    return redirect(url_for('sites_list'))

                site_name = site.sito
                site_dict = site.to_dict()

                # Get related data and convert to dict within session
                us_records = session.query(USModel).filter(USModel.sito == site_name).limit(100).all()
                us_list = [us.to_dict() for us in us_records]

                inv_records = session.query(InvModel).filter(InvModel.sito == site_name).limit(100).all()
                inventory_list = [inv.to_dict() for inv in inv_records]

            # Generate PDF (outside session)
            pdf_bytes = pdf_generator.generate_site_report(
                site_dict,
                us_list,
                inventory_list
            )

            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(pdf_bytes)
                tmp_path = tmp.name

            return send_file(tmp_path, as_attachment=True,
                           download_name=f"relazione_{site_name}.pdf",
                           mimetype='application/pdf')

        except Exception as e:
            flash(f'Errore export PDF: {str(e)}', 'error')
            return redirect(url_for('view_site', site_id=site_id))

    @app.route('/export/site_pdf_with_matrix/<site_name>')
    def export_site_pdf_with_matrix(site_name):
        """Export site PDF with integrated Harris Matrix"""
        try:
            # Generate Harris Matrix image
            graph = matrix_generator.generate_matrix(site_name)
            stats = matrix_generator.get_matrix_statistics(graph)

            # Create temporary file for matrix image
            matrix_img_path = graphviz_visualizer.create_matrix(
                graph,
                grouping='period_area',
                settings={'show_legend': True, 'show_periods': True}
            )

            # Generate PDF with matrix
            pdf_bytes = pdf_generator.generate_harris_matrix_report(
                site_name,
                matrix_img_path,
                stats
            )

            # Cleanup temp image
            if os.path.exists(matrix_img_path):
                os.remove(matrix_img_path)

            # Create temporary PDF file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(pdf_bytes)
                tmp_path = tmp.name

            return send_file(tmp_path, as_attachment=True,
                           download_name=f"harris_matrix_{site_name}.pdf",
                           mimetype='application/pdf')

        except Exception as e:
            flash(f'Errore export PDF Harris Matrix: {str(e)}', 'error')
            return redirect(url_for('harris_matrix', site_name=site_name))

    @app.route('/export/us_pdf')
    def export_us_pdf():
        """Export US list PDF"""
        try:
            site_name = request.args.get('sito')

            # Get US data within session
            with db_manager.connection.get_session() as session:
                from pyarchinit_mini.models.us import US as USModel

                query = session.query(USModel)
                if site_name:
                    query = query.filter(USModel.sito == site_name)

                us_records = query.limit(500).all()
                us_list = [us.to_dict() for us in us_records]

            if not us_list:
                flash('Nessuna US trovata', 'warning')
                return redirect(url_for('us_list'))

            # Generate PDF
            site_name_clean = site_name if site_name else 'Tutti_i_siti'

            # Create temporary file for PDF output
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                output_path = tmp.name

            # Generate PDF to file
            pdf_generator.generate_us_pdf(site_name_clean, us_list, output_path)

            return send_file(output_path, as_attachment=True,
                           download_name=f"us_{site_name_clean}.pdf",
                           mimetype='application/pdf')

        except Exception as e:
            flash(f'Errore export PDF US: {str(e)}', 'error')
            return redirect(url_for('us_list'))

    @app.route('/export/us_single_pdf/<sito>/<int:us_number>')
    def export_us_single_pdf(sito, us_number):
        """Export single US PDF"""
        try:
            # Get US data within session
            with db_manager.connection.get_session() as session:
                from pyarchinit_mini.models.us import US as USModel

                us = session.query(USModel).filter(
                    USModel.sito == sito,
                    USModel.us == us_number
                ).first()

                if not us:
                    flash('US non trovata', 'error')
                    return redirect(url_for('us_list'))

                us_dict = us.to_dict()

            # Create temporary file for PDF output
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                output_path = tmp.name

            # Generate PDF with single US
            pdf_generator.generate_us_pdf(sito, [us_dict], output_path)

            return send_file(output_path, as_attachment=True,
                           download_name=f"us_{sito}_{us_number}.pdf",
                           mimetype='application/pdf')

        except Exception as e:
            flash(f'Errore export PDF US: {str(e)}', 'error')
            return redirect(url_for('us_list'))

    @app.route('/export/inventario_pdf')
    def export_inventario_pdf():
        """Export Inventario list PDF"""
        try:
            site_name = request.args.get('sito')

            # Get inventario data within session
            with db_manager.connection.get_session() as session:
                from pyarchinit_mini.models.inventario_materiali import InventarioMateriali as InvModel

                query = session.query(InvModel)
                if site_name:
                    query = query.filter(InvModel.sito == site_name)

                inv_records = query.limit(500).all()
                inventory_list = [inv.to_dict() for inv in inv_records]

            if not inventory_list:
                flash('Nessun reperto trovato', 'warning')
                return redirect(url_for('inventario_list'))

            # Generate PDF
            site_name_clean = site_name if site_name else 'Tutti_i_siti'

            # Create temporary file for PDF output
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                output_path = tmp.name

            # Generate PDF to file
            pdf_generator.generate_inventario_pdf(site_name_clean, inventory_list, output_path)

            return send_file(output_path, as_attachment=True,
                           download_name=f"inventario_{site_name_clean}.pdf",
                           mimetype='application/pdf')

        except Exception as e:
            flash(f'Errore export PDF Inventario: {str(e)}', 'error')
            return redirect(url_for('inventario_list'))

    @app.route('/export/inventario_single_pdf/<int:inv_id>')
    def export_inventario_single_pdf(inv_id):
        """Export single Inventario PDF"""
        try:
            # Get inventario data within session
            with db_manager.connection.get_session() as session:
                from pyarchinit_mini.models.inventario_materiali import InventarioMateriali as InvModel

                inv = session.query(InvModel).filter(InvModel.id_invmat == inv_id).first()

                if not inv:
                    flash('Reperto non trovato', 'error')
                    return redirect(url_for('inventario_list'))

                inv_dict = inv.to_dict()
                site_name = inv_dict.get('sito', 'Unknown')

            # Create temporary file for PDF output
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                output_path = tmp.name

            # Generate PDF with single item
            pdf_generator.generate_inventario_pdf(site_name, [inv_dict], output_path)

            return send_file(output_path, as_attachment=True,
                           download_name=f"inventario_{inv_id}.pdf",
                           mimetype='application/pdf')

        except Exception as e:
            flash(f'Errore export PDF Inventario: {str(e)}', 'error')
            return redirect(url_for('inventario_list'))

    # Media routes
    @app.route('/media/upload', methods=['GET', 'POST'])
    @login_required
    @write_permission_required
    def upload_media():
        form = MediaUploadForm()
        
        if form.validate_on_submit():
            try:
                uploaded_file = form.file.data
                if uploaded_file and uploaded_file.filename:
                    # Save uploaded file temporarily
                    filename = secure_filename(uploaded_file.filename)
                    temp_path = os.path.join(tempfile.gettempdir(), filename)
                    uploaded_file.save(temp_path)
                    
                    # Store using media handler
                    metadata = media_handler.store_file(
                        temp_path,
                        form.entity_type.data,
                        form.entity_id.data,
                        form.description.data,
                        "",  # tags
                        form.author.data
                    )
                    
                    # Clean up temp file
                    os.remove(temp_path)
                    
                    flash('File caricato con successo!', 'success')
                    return redirect(url_for('upload_media'))
                    
            except Exception as e:
                flash(f'Errore caricamento file: {str(e)}', 'error')
        
        return render_template('media/upload.html', form=form)

    # Database Administration Routes
    @app.route('/admin/database')
    @login_required
    def admin_database():
        """Database administration page"""
        # Get current database info
        current_url = app.config.get('CURRENT_DATABASE_URL', database_url)

        # Parse current connection info
        db_info = {
            'url': current_url,
            'type': 'SQLite' if current_url.startswith('sqlite') else 'PostgreSQL',
            'is_default': current_url == database_url
        }

        # Get statistics
        try:
            total_sites = site_service.count_sites()
            total_us = us_service.count_us()
            total_inventory = inventario_service.count_inventario()
        except Exception:
            total_sites = total_us = total_inventory = 0

        stats = {
            'sites': total_sites,
            'us': total_us,
            'inventory': total_inventory
        }

        # Get saved connections
        connections = app.config.get('DATABASE_CONNECTIONS', {})

        return render_template('admin/database.html',
                             db_info=db_info,
                             stats=stats,
                             connections=connections)

    @app.route('/admin/database/upload', methods=['GET', 'POST'])
    def upload_database():
        """Upload SQLite database file"""
        form = DatabaseUploadForm()

        if form.validate_on_submit():
            try:
                uploaded_file = form.database_file.data
                db_name = form.database_name.data
                description = form.description.data

                # Secure filename
                filename = secure_filename(uploaded_file.filename)
                if not filename.endswith('.db'):
                    filename += '.db'

                # Save to databases folder
                db_path = os.path.join(app.config['DATABASE_FOLDER'], filename)
                uploaded_file.save(db_path)

                # Validate it's a valid SQLite database
                try:
                    test_conn = DatabaseConnection.from_url(f'sqlite:///{db_path}')
                    # Try to query tables to validate
                    with test_conn.get_session() as session:
                        session.execute('SELECT name FROM sqlite_master WHERE type="table"')
                except Exception as e:
                    os.remove(db_path)
                    flash(f'File non valido: {str(e)}', 'error')
                    return render_template('admin/database_upload.html', form=form)

                # Store connection info
                connections = app.config.get('DATABASE_CONNECTIONS', {})
                connections[db_name] = {
                    'type': 'sqlite',
                    'path': db_path,
                    'url': f'sqlite:///{db_path}',
                    'description': description,
                    'uploaded': True
                }
                app.config['DATABASE_CONNECTIONS'] = connections

                flash(f'Database "{db_name}" caricato con successo!', 'success')
                return redirect(url_for('admin_database'))

            except Exception as e:
                flash(f'Errore caricamento database: {str(e)}', 'error')

        return render_template('admin/database_upload.html', form=form)

    @app.route('/admin/database/connect', methods=['GET', 'POST'])
    def connect_database():
        """Connect to external database (PostgreSQL or local SQLite)"""
        form = DatabaseConnectionForm()

        if form.validate_on_submit():
            try:
                conn_name = form.connection_name.data
                db_type = form.db_type.data

                # Build connection URL
                if db_type == 'postgresql':
                    host = form.host.data or 'localhost'
                    port = form.port.data or 5432
                    database = form.database.data
                    username = form.username.data
                    password = form.password.data

                    if username and password:
                        connection_url = f'postgresql://{username}:{password}@{host}:{port}/{database}'
                    else:
                        connection_url = f'postgresql://{host}:{port}/{database}'

                else:  # SQLite
                    sqlite_path = form.sqlite_path.data
                    if not os.path.exists(sqlite_path):
                        flash(f'File non trovato: {sqlite_path}', 'error')
                        return render_template('admin/database_connect.html', form=form)
                    connection_url = f'sqlite:///{sqlite_path}'

                # Test connection
                try:
                    test_conn = DatabaseConnection.from_url(connection_url)
                    with test_conn.get_session() as session:
                        # Try a simple query
                        session.execute('SELECT 1')
                except Exception as e:
                    flash(f'Errore connessione: {str(e)}', 'error')
                    return render_template('admin/database_connect.html', form=form)

                # Store connection
                connections = app.config.get('DATABASE_CONNECTIONS', {})
                connections[conn_name] = {
                    'type': db_type,
                    'url': connection_url,
                    'uploaded': False
                }
                app.config['DATABASE_CONNECTIONS'] = connections

                flash(f'Connessione "{conn_name}" aggiunta con successo!', 'success')
                return redirect(url_for('admin_database'))

            except Exception as e:
                flash(f'Errore: {str(e)}', 'error')

        return render_template('admin/database_connect.html', form=form)

    @app.route('/admin/database/info')
    def database_info():
        """Get detailed information about current database"""
        try:
            # Get table list
            with db_conn.get_session() as session:
                if app.config['CURRENT_DATABASE_URL'].startswith('sqlite'):
                    result = session.execute('SELECT name FROM sqlite_master WHERE type="table" ORDER BY name')
                    tables = [row[0] for row in result]
                else:
                    result = session.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename")
                    tables = [row[0] for row in result]

            # Get row counts for main tables
            table_counts = {}
            for table in ['site_table', 'us_table', 'inventario_materiali_table']:
                try:
                    with db_conn.get_session() as session:
                        result = session.execute(f'SELECT COUNT(*) FROM {table}')
                        table_counts[table] = result.scalar()
                except Exception:
                    table_counts[table] = 0

            return render_template('admin/database_info.html',
                                 tables=tables,
                                 table_counts=table_counts,
                                 current_url=app.config['CURRENT_DATABASE_URL'])

        except Exception as e:
            flash(f'Errore recupero info database: {str(e)}', 'error')
            return redirect(url_for('admin_database'))

    # API endpoints for AJAX
    @app.route('/api/sites')
    def api_sites():
        sites = site_service.get_all_sites(size=100)
        return jsonify([{'id': s.id_sito, 'name': s.sito} for s in sites])

    # ===== Export/Import Routes =====
    from pyarchinit_mini.services.export_import_service import ExportImportService
    export_import_service = ExportImportService(db_manager)

    @app.route('/export')
    @login_required
    def export_page():
        """Export/Import management page"""
        return render_template('export/export_import.html')

    # Excel Export Routes
    @app.route('/export/sites/excel')
    @login_required
    def export_sites_excel():
        """Export sites to Excel"""
        try:
            output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx').name
            export_import_service.export_sites_to_excel(output_path)
            return send_file(output_path, as_attachment=True,
                           download_name='sites_export.xlsx',
                           mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        except Exception as e:
            flash(f'Errore export Excel: {str(e)}', 'error')
            return redirect(url_for('export_page'))

    @app.route('/export/us/excel')
    def export_us_excel():
        """Export US to Excel"""
        try:
            site_name = request.args.get('sito')
            output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx').name
            export_import_service.export_us_to_excel(output_path, site_name)
            filename = f'us_{site_name}.xlsx' if site_name else 'us_export.xlsx'
            return send_file(output_path, as_attachment=True,
                           download_name=filename,
                           mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        except Exception as e:
            flash(f'Errore export Excel: {str(e)}', 'error')
            return redirect(url_for('export_page'))

    @app.route('/export/inventario/excel')
    def export_inventario_excel():
        """Export Inventario to Excel"""
        try:
            site_name = request.args.get('sito')
            output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx').name
            export_import_service.export_inventario_to_excel(output_path, site_name)
            filename = f'inventario_{site_name}.xlsx' if site_name else 'inventario_export.xlsx'
            return send_file(output_path, as_attachment=True,
                           download_name=filename,
                           mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        except Exception as e:
            flash(f'Errore export Excel: {str(e)}', 'error')
            return redirect(url_for('export_page'))

    # CSV Export Routes
    @app.route('/export/sites/csv')
    def export_sites_csv():
        """Export sites to CSV"""
        try:
            output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.csv').name
            export_import_service.export_sites_to_csv(output_path)
            return send_file(output_path, as_attachment=True,
                           download_name='sites_export.csv',
                           mimetype='text/csv')
        except Exception as e:
            flash(f'Errore export CSV: {str(e)}', 'error')
            return redirect(url_for('export_page'))

    @app.route('/export/us/csv')
    def export_us_csv():
        """Export US to CSV"""
        try:
            site_name = request.args.get('sito')
            output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.csv').name
            export_import_service.export_us_to_csv(output_path, site_name)
            filename = f'us_{site_name}.csv' if site_name else 'us_export.csv'
            return send_file(output_path, as_attachment=True,
                           download_name=filename,
                           mimetype='text/csv')
        except Exception as e:
            flash(f'Errore export CSV: {str(e)}', 'error')
            return redirect(url_for('export_page'))

    @app.route('/export/inventario/csv')
    def export_inventario_csv():
        """Export Inventario to CSV"""
        try:
            site_name = request.args.get('sito')
            output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.csv').name
            export_import_service.export_inventario_to_csv(output_path, site_name)
            filename = f'inventario_{site_name}.csv' if site_name else 'inventario_export.csv'
            return send_file(output_path, as_attachment=True,
                           download_name=filename,
                           mimetype='text/csv')
        except Exception as e:
            flash(f'Errore export CSV: {str(e)}', 'error')
            return redirect(url_for('export_page'))

    # CSV Import Routes
    @app.route('/import/sites/csv', methods=['POST'])
    def import_sites_csv():
        """Import sites from CSV"""
        try:
            if 'file' not in request.files:
                flash('Nessun file selezionato', 'error')
                return redirect(url_for('export_page'))

            file = request.files['file']
            if file.filename == '':
                flash('Nessun file selezionato', 'error')
                return redirect(url_for('export_page'))

            if not file.filename.endswith('.csv'):
                flash('Il file deve essere in formato CSV', 'error')
                return redirect(url_for('export_page'))

            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
                file.save(tmp.name)
                tmp_path = tmp.name

            # Import data
            skip_duplicates = request.form.get('skip_duplicates', 'true').lower() == 'true'
            result = export_import_service.batch_import_sites_from_csv(tmp_path, skip_duplicates)

            # Clean up
            os.unlink(tmp_path)

            flash(f'Import completato: {result["imported"]} importati, '
                  f'{result["skipped"]} saltati, {len(result["errors"])} errori', 'success')

            if result['errors']:
                for err in result['errors'][:5]:  # Show first 5 errors
                    flash(f'Errore: {err["error"]}', 'warning')

            return redirect(url_for('export_page'))

        except Exception as e:
            flash(f'Errore import CSV: {str(e)}', 'error')
            return redirect(url_for('export_page'))

    @app.route('/import/us/csv', methods=['POST'])
    def import_us_csv():
        """Import US from CSV"""
        try:
            if 'file' not in request.files:
                flash('Nessun file selezionato', 'error')
                return redirect(url_for('export_page'))

            file = request.files['file']
            if file.filename == '':
                flash('Nessun file selezionato', 'error')
                return redirect(url_for('export_page'))

            if not file.filename.endswith('.csv'):
                flash('Il file deve essere in formato CSV', 'error')
                return redirect(url_for('export_page'))

            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
                file.save(tmp.name)
                tmp_path = tmp.name

            # Import data
            skip_duplicates = request.form.get('skip_duplicates', 'true').lower() == 'true'
            result = export_import_service.batch_import_us_from_csv(tmp_path, skip_duplicates)

            # Clean up
            os.unlink(tmp_path)

            flash(f'Import completato: {result["imported"]} importati, '
                  f'{result["skipped"]} saltati, {len(result["errors"])} errori', 'success')

            if result['errors']:
                for err in result['errors'][:5]:
                    flash(f'Errore: {err["error"]}', 'warning')

            return redirect(url_for('export_page'))

        except Exception as e:
            flash(f'Errore import CSV: {str(e)}', 'error')
            return redirect(url_for('export_page'))

    @app.route('/import/inventario/csv', methods=['POST'])
    def import_inventario_csv():
        """Import Inventario from CSV"""
        try:
            if 'file' not in request.files:
                flash('Nessun file selezionato', 'error')
                return redirect(url_for('export_page'))

            file = request.files['file']
            if file.filename == '':
                flash('Nessun file selezionato', 'error')
                return redirect(url_for('export_page'))

            if not file.filename.endswith('.csv'):
                flash('Il file deve essere in formato CSV', 'error')
                return redirect(url_for('export_page'))

            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
                file.save(tmp.name)
                tmp_path = tmp.name

            # Import data
            skip_duplicates = request.form.get('skip_duplicates', 'true').lower() == 'true'
            result = export_import_service.batch_import_inventario_from_csv(tmp_path, skip_duplicates)

            # Clean up
            os.unlink(tmp_path)

            flash(f'Import completato: {result["imported"]} importati, '
                  f'{result["skipped"]} saltati, {len(result["errors"])} errori', 'success')

            if result['errors']:
                for err in result['errors'][:5]:
                    flash(f'Errore: {err["error"]}', 'warning')

            return redirect(url_for('export_page'))

        except Exception as e:
            flash(f'Errore import CSV: {str(e)}', 'error')
            return redirect(url_for('export_page'))

    return app, socketio

# Run app
def main():
    """
    Entry point for running the web interface via console script.
    """
    app, socketio = create_app()

    # Get configuration from environment or use defaults
    host = os.getenv("PYARCHINIT_WEB_HOST", "0.0.0.0")
    port = int(os.getenv("PYARCHINIT_WEB_PORT", "5001"))  # Changed from 5000 to 5001 to avoid macOS AirPlay
    debug = os.getenv("PYARCHINIT_WEB_DEBUG", "true").lower() == "true"

    print(f"Starting PyArchInit-Mini Web Interface on {host}:{port}")
    print(f"Web Interface: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/")
    print(f"WebSocket support enabled for real-time collaboration")

    # Note: For production use, deploy with gunicorn + eventlet/gevent
    # Example: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5001 app:app
    socketio.run(app, debug=debug, host=host, port=port, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    main()