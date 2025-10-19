# PyArchInit-Mini

**Lightweight Archaeological Data Management System**

PyArchInit-Mini is a standalone, modular version of PyArchInit focused on core archaeological data management functionality without GIS dependencies. It provides multiple interfaces and a clean, scalable API for managing archaeological sites, stratigraphic units, and material inventories.

## Features

### Core Data Management
- 🏛️ **Site Management**: Complete CRUD operations for archaeological sites
- 📋 **Stratigraphic Units (US)**: Manage stratigraphic contexts and excavation data  
- 📦 **Material Inventory**: Track and catalog archaeological finds
- 🗄️ **Multi-Database Support**: Works with both PostgreSQL and SQLite

### Advanced Archaeological Tools
- 🔗 **Harris Matrix**: Generate and visualize stratigraphic relationships
- 📄 **PDF Export**: Create comprehensive archaeological reports
- 🖼️ **Media Management**: Handle images, documents, and multimedia files
- 📊 **Statistics & Reports**: Comprehensive data analysis and reporting

### Multiple User Interfaces
- 🌐 **Web Interface**: Modern Flask-based web application with Bootstrap UI
- 🖥️ **Desktop GUI**: Complete Tkinter desktop application
- 💻 **CLI Interface**: Rich-based interactive command-line interface
- 🚀 **REST API**: FastAPI-based scalable API with automatic documentation

### Technical Features
- 📊 **Data Validation**: Comprehensive validation using Pydantic schemas
- 🔍 **Search & Filtering**: Advanced search and filtering capabilities
- 📖 **Auto Documentation**: Interactive API docs via Swagger/OpenAPI
- 🔄 **Session Management**: Proper database session handling and connection pooling

## Quick Start

### Installation

```bash
pip install pyarchinit-mini
```

### Interface Options

PyArchInit-Mini provides multiple ways to interact with your archaeological data:

#### 1. Web Interface (Flask)
Modern web application with responsive Bootstrap UI:

```bash
cd pyarchinit-mini
python web_interface/app.py
```

Visit `http://localhost:5000` to access the web interface.

#### 2. Desktop GUI (Tkinter)
Complete desktop application with rich interface:

```bash
cd pyarchinit-mini
python desktop_gui/gui_app.py
# OR use the quick launcher:
python run_gui.py
```

#### 3. CLI Interface (Rich)
Interactive command-line interface:

```bash
cd pyarchinit-mini
python cli_interface/cli_app.py
```

#### 4. REST API Server (FastAPI)
Scalable API server with automatic documentation:

```bash
cd pyarchinit-mini
python main.py
```

Visit `http://localhost:8000/docs` for interactive API documentation.

### Basic Usage

#### As a Python Library

```python
from pyarchinit_mini import DatabaseManager, SiteService
from pyarchinit_mini.database import DatabaseConnection

# Connect to database
db_conn = DatabaseConnection.sqlite("archaeological_data.db")
db_manager = DatabaseManager(db_conn)

# Use services
site_service = SiteService(db_manager)

# Create a new site
site_data = {
    "sito": "Pompei",
    "nazione": "Italia",
    "regione": "Campania", 
    "comune": "Pompei",
    "provincia": "NA",
    "descrizione": "Ancient Roman city"
}

site = site_service.create_site(site_data)
print(f"Created site: {site.display_name}")
```

#### Database Configuration

All interfaces support both SQLite and PostgreSQL. Configure via environment variable:

```bash
# SQLite (default)
export DATABASE_URL="sqlite:///./pyarchinit_mini.db"

# PostgreSQL
export DATABASE_URL="postgresql://user:password@localhost:5432/pyarchinit"
```

## API Endpoints

### Sites
- `GET /api/v1/sites/` - List sites with pagination and filtering
- `POST /api/v1/sites/` - Create new site
- `GET /api/v1/sites/{site_id}` - Get site by ID
- `PUT /api/v1/sites/{site_id}` - Update site
- `DELETE /api/v1/sites/{site_id}` - Delete site

### Stratigraphic Units (US)
- `GET /api/v1/us/` - List stratigraphic units
- `POST /api/v1/us/` - Create new US
- `GET /api/v1/us/{us_id}` - Get US by ID
- `PUT /api/v1/us/{us_id}` - Update US
- `DELETE /api/v1/us/{us_id}` - Delete US

### Material Inventory
- `GET /api/v1/inventario/` - List inventory items
- `POST /api/v1/inventario/` - Create new inventory item
- `GET /api/v1/inventario/{item_id}` - Get item by ID
- `PUT /api/v1/inventario/{item_id}` - Update item
- `DELETE /api/v1/inventario/{item_id}` - Delete item

## Special Features

### Harris Matrix Generation
PyArchInit-Mini includes advanced Harris Matrix functionality:

```python
from pyarchinit_mini.harris_matrix import HarrisMatrixGenerator, MatrixVisualizer

# Generate Harris Matrix for a site
matrix_generator = HarrisMatrixGenerator(db_manager)
graph = matrix_generator.generate_matrix("Pompei")
levels = matrix_generator.get_matrix_levels(graph)
stats = matrix_generator.get_matrix_statistics(graph)

# Visualize and export
visualizer = MatrixVisualizer()
exports = visualizer.export_to_formats(graph, levels, "pompei_matrix")
```

### PDF Report Generation
Create comprehensive archaeological reports:

```python
from pyarchinit_mini.pdf_export import PDFGenerator

pdf_generator = PDFGenerator()
site_data = site_service.get_site_by_id(1).to_dict()
us_data = [us.to_dict() for us in us_service.get_us_by_site("Pompei")]
inventory_data = [inv.to_dict() for inv in inventario_service.get_inventario_by_site("Pompei")]

pdf_bytes = pdf_generator.generate_site_report(site_data, us_data, inventory_data)

with open("site_report.pdf", "wb") as f:
    f.write(pdf_bytes)
```

### Media Management
Handle multimedia files with automatic organization:

```python
from pyarchinit_mini.media_manager import MediaHandler

media_handler = MediaHandler()
metadata = media_handler.store_file(
    "/path/to/photo.jpg",
    "site",
    1,  # site ID
    "Excavation photo of area A"
)
```

## Database Support

### SQLite (Default)
```python
from pyarchinit_mini.database import DatabaseConnection

db_conn = DatabaseConnection.sqlite("path/to/database.db")
```

### PostgreSQL
```python
from pyarchinit_mini.database import DatabaseConnection

db_conn = DatabaseConnection.postgresql(
    host="localhost",
    port=5432, 
    database="pyarchinit",
    username="user",
    password="password"
)
```

## Data Models

### Site
Core information about archaeological sites including location, description, and metadata.

### Stratigraphic Unit (US) 
Represents stratigraphic contexts with excavation data, relationships, measurements, and dating information.

### Material Inventory
Catalog of archaeological finds with classification, measurements, conservation data, and contextual information.

## Architecture

PyArchInit-Mini follows a clean, modular architecture:

- **Models**: SQLAlchemy entities defining database structure
- **Services**: Business logic layer with validation and operations
- **API**: FastAPI REST endpoints with Pydantic schemas
- **Database**: Connection management and query abstractions

## Development

### Setup Development Environment

```bash
git clone https://github.com/pyarchinit/pyarchinit-mini.git
cd pyarchinit-mini
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Quality

```bash
black pyarchinit_mini/
flake8 pyarchinit_mini/
mypy pyarchinit_mini/
```

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to the main repository.

## License

PyArchInit-Mini is licensed under the GNU General Public License v2.0. See [LICENSE](LICENSE) for details.

## Related Projects

- [PyArchInit](https://github.com/pyarchinit/pyarchinit3) - Full QGIS plugin version
- [PyArchInit Documentation](https://pyarchinit.github.io/pyarchinit_doc/)

## Support

- 📧 Email: enzo.ccc@gmail.com
- 🐛 Issue Tracker: [GitHub Issues](https://github.com/pyarchinit/pyarchinit-mini/issues)
- 📖 Documentation: [Read the Docs](https://pyarchinit-mini.readthedocs.io/)

---

Made with ❤️ by the PyArchInit Team