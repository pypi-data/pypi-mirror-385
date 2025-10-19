# PyArchInit-Mini

[![PyPI version](https://badge.fury.io/py/pyarchinit-mini.svg)](https://badge.fury.io/py/pyarchinit-mini)
[![Python 3.8-3.14](https://img.shields.io/badge/python-3.8--3.14-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![Status](https://img.shields.io/badge/status-stable-green.svg)](https://pypi.org/project/pyarchinit-mini/)

**Lightweight Archaeological Data Management System - 100% Desktop GUI Parity**

PyArchInit-Mini is a standalone, modular version of PyArchInit focused on core archaeological data management functionality without GIS dependencies. It provides multiple interfaces (Web, Desktop GUI, CLI, REST API) with a clean, scalable architecture for managing archaeological sites, stratigraphic units, and material inventories.

---

## ✨ Features

### 🏛️ Core Data Management
- **Site Management**: Complete CRUD operations for archaeological sites
- **Stratigraphic Units (US)**: 49 fields organized in 6 tabs, matching desktop GUI
- **Material Inventory**: 37 fields in 8 tabs with ICCD thesaurus support
- **Multi-Database**: SQLite and PostgreSQL with upload/connect capabilities

### 🔬 Advanced Archaeological Tools
- **Harris Matrix**: Graphviz visualizer with 4 grouping modes (period_area, period, area, none)
- **Stratigraphic Validation**: Paradox detection, cycle detection, auto-fix reciprocal relationships
- **PDF Export**: Desktop-style reports (Sites, US, Inventario, Harris Matrix embedded)
- **Media Management**: Images, documents, videos with metadata
- **Thesaurus ICCD**: 4 controlled vocabularies for standardized data entry

### 🖥️ Multiple User Interfaces
- **Web Interface (Flask)**: Modern Bootstrap 5 UI, responsive design
- **Desktop GUI (Tkinter)**: Complete native application
- **CLI Interface**: Rich-based interactive command-line
- **REST API (FastAPI)**: Scalable API with automatic OpenAPI docs

### 📊 Data Export/Import (NEW in v1.0.7)
- **Excel Export**: Export Sites, US, Inventario to .xlsx format
- **CSV Export**: Export to CSV with optional site filtering
- **Batch Import**: Import data from CSV with validation and statistics
- **Multi-Interface**: Available in Web UI, Desktop GUI, and CLI
- **Duplicate Handling**: Skip duplicates option to preserve existing data

### 🚀 Technical Features
- **Production Ready**: v1.0.7 with 100% Desktop GUI feature parity
- **Python 3.8-3.14**: Full support for latest Python versions including 3.12, 3.13, 3.14
- **Data Validation**: Comprehensive Pydantic schemas
- **Session Management**: Proper database connection pooling
- **Auto Documentation**: Interactive Swagger/OpenAPI docs
- **Cross-Platform**: Windows, Linux, macOS support
- **Tests Included**: Full test suite included in distribution

---

## 📦 Installation

### Basic Installation (API Only)
```bash
pip install pyarchinit-mini
```

### With CLI Interface
```bash
pip install 'pyarchinit-mini[cli]'
```

### With Web Interface
```bash
pip install 'pyarchinit-mini[web]'
```

### With Desktop GUI
```bash
pip install 'pyarchinit-mini[gui]'
```

### With Harris Matrix Visualization
```bash
pip install 'pyarchinit-mini[harris]'
```

### With Advanced PDF Export
```bash
pip install 'pyarchinit-mini[pdf]'
```

### With Excel/CSV Export and Import
```bash
pip install 'pyarchinit-mini[export]'
```

### Complete Installation (Recommended)
```bash
pip install 'pyarchinit-mini[all]'
```

### Development Installation
```bash
pip install 'pyarchinit-mini[dev]'
```

> **Note for zsh users**: Quote the package name to avoid globbing issues: `'pyarchinit-mini[all]'`

---

## 🚀 Quick Start

### 1. Initial Setup
After installation, run the setup command to create the configuration directory:

```bash
pyarchinit-mini-setup
```

This creates the following structure in your home directory:

```
~/.pyarchinit_mini/
├── data/              # Database SQLite files
├── media/             # Images, videos, documents
│   ├── images/
│   ├── videos/
│   ├── documents/
│   └── thumbnails/
├── export/            # Generated PDF exports
├── backup/            # Automatic database backups
├── config/            # Configuration files
│   └── config.yaml
└── logs/              # Application logs
```

### 2. Usage

#### Start the Web Interface
```bash
pyarchinit-web
# Open http://localhost:5001 in your browser
```

#### Start the Desktop GUI
```bash
pyarchinit-gui
```

#### Start the REST API Server
```bash
pyarchinit-api
# API docs available at http://localhost:8000/docs
```

#### Start the CLI Interface
```bash
pyarchinit-cli
```

---

## 📚 Dependencies Structure

### Core (Always Installed)
- **FastAPI + Uvicorn**: REST API framework
- **SQLAlchemy**: ORM and database abstraction
- **psycopg2-binary**: PostgreSQL driver
- **Pydantic**: Data validation
- **NetworkX**: Harris Matrix generation
- **ReportLab**: PDF generation
- **Pillow**: Image processing

### Optional Extras

| Extra | Components | Installation |
|-------|-----------|--------------|
| `cli` | Click, Rich, Inquirer | `pip install 'pyarchinit-mini[cli]'` |
| `web` | Flask, WTForms, Jinja2 | `pip install 'pyarchinit-mini[web]'` |
| `gui` | (Tkinter is in stdlib) | `pip install 'pyarchinit-mini[gui]'` |
| `harris` | Matplotlib, Graphviz | `pip install 'pyarchinit-mini[harris]'` |
| `pdf` | WeasyPrint | `pip install 'pyarchinit-mini[pdf]'` |
| `media` | python-magic, moviepy | `pip install 'pyarchinit-mini[media]'` |
| `export` | pandas, openpyxl | `pip install 'pyarchinit-mini[export]'` |
| `all` | All of the above | `pip install 'pyarchinit-mini[all]'` |
| `dev` | pytest, black, mypy, flake8 | `pip install 'pyarchinit-mini[dev]'` |

---

## ⚙️ Configuration

### Database Configuration

Edit `~/.pyarchinit_mini/config/config.yaml`:

```yaml
database:
  # SQLite (default)
  url: "sqlite:///~/.pyarchinit_mini/data/pyarchinit_mini.db"

  # Or PostgreSQL
  # url: "postgresql://user:password@localhost:5432/pyarchinit"

api:
  host: "0.0.0.0"
  port: 8000
  reload: true

web:
  host: "0.0.0.0"
  port: 5001
  debug: true

media:
  base_dir: "~/.pyarchinit_mini/media"
  max_upload_size: 104857600  # 100MB

export:
  base_dir: "~/.pyarchinit_mini/export"
  pdf_dpi: 300

backup:
  enabled: true
  frequency: "daily"
  keep_count: 7
```

### Environment Variables

Alternatively, use environment variables:

```bash
export DATABASE_URL="postgresql://user:pass@localhost:5432/pyarchinit"
export PYARCHINIT_WEB_PORT=5001
export PYARCHINIT_API_PORT=8000
```

---

## 🎯 Key Features in Detail

### Web Interface
- **Complete Forms**: US (49 fields/6 tabs), Inventario (37 fields/8 tabs)
- **Thesaurus Integration**: ICCD-compliant controlled vocabularies
- **Harris Matrix Viewer**: Interactive Graphviz visualization with 4 grouping modes
- **Validation Tools**: Stratigraphic paradox/cycle detection with auto-fix
- **Database Management**: Upload SQLite files, connect to PostgreSQL
- **PDF Export**: One-click export for Sites, US, Inventario with Harris Matrix

### Desktop GUI
- **Native Tkinter Application**: Full-featured desktop interface
- **Identical to Web**: Same 49-field US and 37-field Inventario forms
- **Offline Capable**: Works without internet connection
- **Cross-Platform**: Windows, Linux, macOS

### REST API
- **FastAPI Framework**: Modern, fast, async-capable
- **Auto Documentation**: Swagger UI at `/docs`, ReDoc at `/redoc`
- **Validation**: Automatic request/response validation
- **Scalable**: Production-ready with Uvicorn

### Harris Matrix
- **Graphviz Engine**: Professional orthogonal layout
- **4 Grouping Modes**:
  - `period_area`: Group by period and area
  - `period`: Group by period only
  - `area`: Group by area only
  - `none`: No grouping
- **High Resolution**: 300 DPI export for publications
- **PDF Integration**: Embedded in site reports

### Stratigraphic Validation
- **Paradox Detection**: Find logical impossibilities in stratigraphic relationships
- **Cycle Detection**: Identify circular dependencies
- **Reciprocal Check**: Verify bidirectional relationships
- **Auto-Fix**: One-click correction for missing reciprocals

### Export/Import (v1.0.7)
- **Web Interface**: Navigate to Export/Import page for visual interface
- **Desktop GUI**: Menu → Strumenti → Export/Import Dati
- **CLI Commands**:
  ```bash
  # Export to Excel/CSV
  pyarchinit-export-import export-sites -f excel -o sites.xlsx
  pyarchinit-export-import export-us -f csv -s "SiteName" -o us.csv
  pyarchinit-export-import export-inventario -f excel -o inventario.xlsx

  # Import from CSV
  pyarchinit-export-import import-sites sites.csv
  pyarchinit-export-import import-us --skip-duplicates us.csv
  pyarchinit-export-import import-inventario --no-skip-duplicates inv.csv
  ```
- **Features**:
  - Optional site filtering for US and Inventario exports
  - Skip duplicates option (default: enabled)
  - Import statistics (imported, skipped, errors)
  - Comprehensive error reporting

---

## 💾 Database Management

### Why `~/.pyarchinit_mini`?
- **Persistence**: Data survives virtualenv removal
- **Easy Backup**: Single directory to backup
- **Multi-Project**: Same database accessible from different virtualenvs
- **Standard Convention**: Follows Unix/Linux conventions

### Database Options

#### SQLite (Default)
```bash
# Automatic setup
pyarchinit-mini-setup
```

Database created at: `~/.pyarchinit_mini/data/pyarchinit_mini.db`

#### PostgreSQL
```yaml
# config.yaml
database:
  url: "postgresql://user:password@localhost:5432/pyarchinit"
```

#### Upload Existing Database
Use the web interface:
1. Navigate to **Database** → **Upload Database**
2. Select your `.db` file from PyArchInit Desktop
3. Database is validated and copied to `~/.pyarchinit_mini/databases/`

---

## 🧪 Development

### Run from Source
```bash
git clone https://github.com/pyarchinit/pyarchinit-mini.git
cd pyarchinit-mini
pip install -e '.[dev]'
```

### Run Tests
```bash
pytest
pytest --cov=pyarchinit_mini
```

### Code Quality
```bash
black pyarchinit_mini/
isort pyarchinit_mini/
flake8 pyarchinit_mini/
mypy pyarchinit_mini/
```

---

## 📖 Documentation

- **API Docs**: http://localhost:8000/docs (after starting API server)
- **User Guide**: See `docs/` directory
- **CHANGELOG**: See `CHANGELOG.md`
- **Quick Start**: See `QUICK_START.md`

---

## 🐛 Troubleshooting

### Command Not Found After Installation
```bash
# Verify installation
pip show pyarchinit-mini

# On Linux/Mac, ensure pip bin directory is in PATH
export PATH="$HOME/.local/bin:$PATH"

# On Windows, commands are in:
# C:\Users\<username>\AppData\Local\Programs\Python\PythonXX\Scripts\
```

### Database Not Found
```bash
# Re-run setup
pyarchinit-mini-setup

# Or manually specify database URL
export DATABASE_URL="sqlite:///path/to/your/database.db"
```

### Tkinter Not Available (Linux)
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora/RHEL
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk
```

### Graphviz Not Found
```bash
# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz

# Windows
# Download from https://graphviz.org/download/
```

### Port Already in Use
```bash
# Change web interface port
export PYARCHINIT_WEB_PORT=5002
pyarchinit-web

# Change API port
export PYARCHINIT_API_PORT=8001
pyarchinit-api
```

---

## 🗺️ Roadmap

### Recently Completed (v1.0.7)
- [x] **Export to Excel/CSV** - Sites, US, Inventario export
- [x] **Batch import from CSV** - With validation and duplicate handling
- [x] **Multi-interface export/import** - Web UI, Desktop GUI, and CLI

### Upcoming Features
- [ ] Multi-user authentication and permissions
- [ ] Real-time collaboration (WebSocket)
- [ ] Chart analytics dashboard
- [ ] Mobile-responsive improvements
- [ ] Docker containerization
- [ ] Cloud deployment guides

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
git clone https://github.com/pyarchinit/pyarchinit-mini.git
cd pyarchinit-mini
pip install -e '.[dev]'
pre-commit install  # Optional: install pre-commit hooks
```

---

## 📄 License

This project is licensed under the GNU General Public License v2.0 - see the [LICENSE](LICENSE) file for details.

---

## 💬 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/pyarchinit/pyarchinit-mini/issues)
- **Email**: enzo.ccc@gmail.com
- **PyPI**: [pypi.org/project/pyarchinit-mini](https://pypi.org/project/pyarchinit-mini/)

---

## 🙏 Acknowledgments

- **PyArchInit Team**: Original desktop application developers
- **Archaeological Community**: Feedback and feature requests
- **Open Source Contributors**: Libraries and tools that make this possible

---

## 📊 Project Status

**Version**: 1.0.7
**Status**: Production/Stable
**Python**: 3.8 - 3.14
**Last Updated**: 2025-01-19

✅ **100% Desktop GUI Feature Parity Achieved**
✅ **Full Python 3.14 Support**
✅ **Tests Included in Distribution**
✅ **Excel/CSV Export/Import** (NEW in v1.0.7)

---

**Made with ❤️ for the Archaeological Community**