#!/usr/bin/env python3
"""
Flask Web Interface for PyArchInit-Mini
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_wtf import FlaskForm
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
from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
from pyarchinit_mini.harris_matrix.matrix_visualizer import MatrixVisualizer
from pyarchinit_mini.pdf_export.pdf_generator import PDFGenerator
from pyarchinit_mini.media_manager.media_handler import MediaHandler

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
    sito = SelectField('Sito', validators=[DataRequired()], coerce=str)
    area = StringField('Area')
    us = IntegerField('Numero US', validators=[DataRequired()])
    d_stratigrafica = StringField('Descrizione Stratigrafica')
    d_interpretativa = StringField('Descrizione Interpretativa')
    descrizione = TextAreaField('Descrizione Dettagliata')
    interpretazione = TextAreaField('Interpretazione')
    anno_scavo = IntegerField('Anno Scavo')
    schedatore = StringField('Schedatore')
    formazione = SelectField('Formazione', choices=[
        ('', '-- Seleziona --'),
        ('Natural', 'Naturale'),
        ('Artificial', 'Artificiale')
    ])

class InventarioForm(FlaskForm):
    sito = SelectField('Sito', validators=[DataRequired()], coerce=str)
    numero_inventario = IntegerField('Numero Inventario', validators=[DataRequired()])
    tipo_reperto = SelectField('Tipo Reperto', choices=[
        ('', '-- Seleziona --'),
        ('Ceramica', 'Ceramica'),
        ('Metallo', 'Metallo'),
        ('Pietra', 'Pietra'),
        ('Osso', 'Osso'),
        ('Vetro', 'Vetro')
    ])
    definizione = StringField('Definizione')
    descrizione = TextAreaField('Descrizione')
    area = StringField('Area')
    us = IntegerField('US')
    peso = StringField('Peso (g)')

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

# Flask App Setup
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['UPLOAD_FOLDER'] = 'uploads'
    
    # Initialize database
    database_url = os.getenv("DATABASE_URL", "sqlite:///./pyarchinit_mini.db")
    db_conn = DatabaseConnection.from_url(database_url)
    db_conn.create_tables()
    db_manager = DatabaseManager(db_conn)
    
    # Initialize services
    site_service = SiteService(db_manager)
    us_service = USService(db_manager)
    inventario_service = InventarioService(db_manager)
    matrix_generator = HarrisMatrixGenerator(db_manager)
    matrix_visualizer = MatrixVisualizer()
    pdf_generator = PDFGenerator()
    media_handler = MediaHandler()
    
    # Routes
    @app.route('/')
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
    
    # Sites routes
    @app.route('/sites')
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
                flash(f'Sito "{site_data["sito"]}" creato con successo!', 'success')
                return redirect(url_for('sites_list'))
                
            except Exception as e:
                flash(f'Errore nella creazione del sito: {str(e)}', 'error')
        
        return render_template('sites/form.html', form=form, title='Nuovo Sito')
    
    @app.route('/sites/<int:site_id>')
    def view_site(site_id):
        site = site_service.get_site_by_id(site_id)
        if not site:
            flash('Sito non trovato', 'error')
            return redirect(url_for('sites_list'))
        
        # Get related data
        site_name = site.sito
        us_list = us_service.get_us_by_site(site_name, size=50)
        inventory_list = inventario_service.get_inventario_by_site(site_name, size=50)
        
        return render_template('sites/detail.html', site=site, 
                             us_list=us_list, inventory_list=inventory_list)
    
    # US routes
    @app.route('/us')
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
    def create_us():
        form = USForm()
        
        # Populate site choices
        sites = site_service.get_all_sites(size=100)
        form.sito.choices = [('', '-- Seleziona Sito --')] + [(s.sito, s.sito) for s in sites]
        
        if form.validate_on_submit():
            try:
                us_data = {
                    'sito': form.sito.data,
                    'area': form.area.data,
                    'us': form.us.data,
                    'd_stratigrafica': form.d_stratigrafica.data,
                    'd_interpretativa': form.d_interpretativa.data,
                    'descrizione': form.descrizione.data,
                    'interpretazione': form.interpretazione.data,
                    'anno_scavo': form.anno_scavo.data,
                    'schedatore': form.schedatore.data,
                    'formazione': form.formazione.data
                }
                
                us = us_service.create_us(us_data)
                flash(f'US {us_data["us"]} creata con successo!', 'success')
                return redirect(url_for('us_list'))
                
            except Exception as e:
                flash(f'Errore nella creazione US: {str(e)}', 'error')
        
        return render_template('us/form.html', form=form, title='Nuova US')
    
    # Inventory routes
    @app.route('/inventario')
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
    def create_inventario():
        form = InventarioForm()
        
        # Populate site choices
        sites = site_service.get_all_sites(size=100)
        form.sito.choices = [('', '-- Seleziona Sito --')] + [(s.sito, s.sito) for s in sites]
        
        if form.validate_on_submit():
            try:
                inv_data = {
                    'sito': form.sito.data,
                    'numero_inventario': form.numero_inventario.data,
                    'tipo_reperto': form.tipo_reperto.data,
                    'definizione': form.definizione.data,
                    'descrizione': form.descrizione.data,
                    'area': form.area.data,
                    'us': form.us.data,
                    'peso': float(form.peso.data) if form.peso.data else None
                }
                
                item = inventario_service.create_inventario(inv_data)
                flash(f'Reperto {inv_data["numero_inventario"]} creato con successo!', 'success')
                return redirect(url_for('inventario_list'))
                
            except Exception as e:
                flash(f'Errore nella creazione reperto: {str(e)}', 'error')
        
        return render_template('inventario/form.html', form=form, title='Nuovo Reperto')
    
    # Harris Matrix routes
    @app.route('/harris_matrix/<site_name>')
    def harris_matrix(site_name):
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
                                 levels=levels)
            
        except Exception as e:
            flash(f'Errore generazione Harris Matrix: {str(e)}', 'error')
            return redirect(url_for('sites_list'))
    
    # Export routes
    @app.route('/export/site_pdf/<int:site_id>')
    def export_site_pdf(site_id):
        try:
            site = site_service.get_site_by_id(site_id)
            if not site:
                flash('Sito non trovato', 'error')
                return redirect(url_for('sites_list'))
            
            # Get related data
            site_name = site.sito
            us_list = [us.to_dict() for us in us_service.get_us_by_site(site_name, size=100)]
            inventory_list = [inv.to_dict() for inv in inventario_service.get_inventario_by_site(site_name, size=100)]
            
            # Generate PDF
            pdf_bytes = pdf_generator.generate_site_report(
                site.to_dict(),
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
    
    # Media routes
    @app.route('/media/upload', methods=['GET', 'POST'])
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
    
    # API endpoints for AJAX
    @app.route('/api/sites')
    def api_sites():
        sites = site_service.get_all_sites(size=100)
        return jsonify([{'id': s.id_sito, 'name': s.sito} for s in sites])
    
    return app

# Run app
def main():
    """
    Entry point for running the web interface via console script.
    """
    app = create_app()

    # Get configuration from environment or use defaults
    host = os.getenv("PYARCHINIT_WEB_HOST", "0.0.0.0")
    port = int(os.getenv("PYARCHINIT_WEB_PORT", "5000"))
    debug = os.getenv("PYARCHINIT_WEB_DEBUG", "true").lower() == "true"

    print(f"Starting PyArchInit-Mini Web Interface on {host}:{port}")
    print(f"Web Interface: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/")

    app.run(debug=debug, host=host, port=port)


if __name__ == '__main__':
    main()