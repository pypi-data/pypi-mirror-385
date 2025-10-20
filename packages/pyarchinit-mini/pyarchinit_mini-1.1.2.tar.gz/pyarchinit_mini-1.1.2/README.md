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

### 📊 Data Export/Import
- **Excel Export**: Export Sites, US, Inventario to .xlsx format
- **CSV Export**: Export to CSV with optional site filtering
- **Batch Import**: Import data from CSV with validation and statistics
- **Multi-Interface**: Available in Web UI, Desktop GUI, and CLI
- **Duplicate Handling**: Skip duplicates option to preserve existing data

### 🔐 Multi-User Authentication (NEW in v1.0.8)
- **Role-Based Access Control**: 3 user roles (Admin, Operator, Viewer)
- **JWT Authentication**: Secure API access with JSON Web Tokens
- **Session Management**: Flask-Login for Web interface
- **Password Security**: Bcrypt hashing for secure password storage
- **User Management**: Admin interface for creating/editing/deleting users
- **Permissions**: Granular permissions (create, read, update, delete, manage_users)
- **Protected Routes**: All web routes require authentication

### 🌐 Real-Time Collaboration (NEW in v1.0.9)
- **WebSocket Support**: Flask-SocketIO for bidirectional real-time communication
- **Live Notifications**: Toast notifications for all CRUD operations (Sites, US, Inventario)
- **Online User Presence**: See who's currently connected to the system
- **Activity Tracking**: Real-time updates when users create, edit, or delete data
- **User Join/Leave Events**: Notifications when team members connect or disconnect
- **Instant Data Sync**: All team members see changes immediately without refreshing
- **Multi-Tab Support**: Works across multiple browser tabs and windows

### 📊 Analytics Dashboard (NEW in v1.1.0)
- **Interactive Charts**: 8 different chart types for comprehensive data visualization
- **Overview Statistics**: Total counts for sites, US, inventory items, regions, and provinces
- **Geographic Analysis**: Sites distribution by region and province (pie and bar charts)
- **Chronological Analysis**: US distribution by chronological period
- **Typological Analysis**: US and inventory items grouped by type (doughnut and bar charts)
- **Conservation Analysis**: Inventory items by conservation state with color-coded pie chart
- **Site-Level Aggregations**: Top 10 sites by US count and inventory count
- **Multi-Interface Support**: Available in both Web UI (Chart.js) and Desktop GUI (matplotlib)
- **Real-Time Data**: Charts update automatically with current database state

### 🚀 Technical Features
- **Production Ready**: v1.1.2 with Mobile/Tablet Optimization + Full Edit Functionality + Analytics Dashboard
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

### With Authentication (Multi-User)
```bash
pip install 'pyarchinit-mini[auth]'
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

### 3. Accessing the Analytics Dashboard

The Analytics Dashboard provides comprehensive data visualization with 8 different chart types.

#### Web Interface
1. Start the web interface: `pyarchinit-web`
2. Navigate to **Analytics** in the top menu
3. View interactive Chart.js charts with:
   - Sites by region (pie chart)
   - Sites by province (bar chart - top 10)
   - US by chronological period (horizontal bar chart)
   - US by type (doughnut chart)
   - Inventory by type (bar chart - top 10)
   - Inventory by conservation state (pie chart)
   - US by site (bar chart - top 10)
   - Inventory by site (bar chart - top 10)

#### Desktop GUI
1. Start the desktop application: `pyarchinit-gui`
2. Go to **Tools → Analytics Dashboard**
3. View matplotlib charts with the same 8 visualizations
4. Use the zoom/pan toolbar for detailed analysis
5. Scroll through all charts in a single window

**Charts Update Automatically**: All charts reflect the current state of your database in real-time.

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
| `web` | Flask, WTForms, Jinja2, Flask-SocketIO | `pip install 'pyarchinit-mini[web]'` |
| `gui` | (Tkinter is in stdlib) | `pip install 'pyarchinit-mini[gui]'` |
| `harris` | Matplotlib, Graphviz | `pip install 'pyarchinit-mini[harris]'` |
| `pdf` | WeasyPrint | `pip install 'pyarchinit-mini[pdf]'` |
| `media` | python-magic, moviepy | `pip install 'pyarchinit-mini[media]'` |
| `export` | pandas, openpyxl | `pip install 'pyarchinit-mini[export]'` |
| `auth` | passlib, bcrypt, python-jose, flask-login | `pip install 'pyarchinit-mini[auth]'` |
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

### Export/Import
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

### Multi-User Authentication (v1.0.8)

Complete authentication system with role-based access control for Web and API interfaces.

#### User Roles

| Role | Permissions | Description |
|------|-------------|-------------|
| **Admin** | Full access + user management | Can create/edit/delete data and manage users |
| **Operator** | Create, Read, Update, Delete data | Can modify archaeological data but not users |
| **Viewer** | Read-only access | Can view data but cannot modify |

#### Setup Authentication

1. **Install with authentication support**:
   ```bash
   pip install 'pyarchinit-mini[auth]'
   # or
   pip install 'pyarchinit-mini[all]'
   ```

2. **Create users table and default admin**:
   ```bash
   python -m pyarchinit_mini.scripts.setup_auth
   ```

   This creates:
   - Users table in database
   - Default admin user (username: `admin`, password: `admin`)

3. **Change default password** (IMPORTANT):
   ```bash
   # Login to web interface at http://localhost:5001/auth/login
   # Navigate to Users → Edit admin user → Change password
   ```

#### Web Interface Authentication

- **Login page**: `http://localhost:5001/auth/login`
- **Default credentials**: username=`admin`, password=`admin`
- **User management**: Admin users can create/edit/delete users via the Users menu
- **Protected routes**: All web pages require authentication
- **Session management**: Uses Flask-Login with secure session cookies

#### API Authentication

- **JWT tokens**: Use `POST /api/auth/login` to get access token
- **Token usage**: Include in `Authorization: Bearer <token>` header
- **Token expiration**: 30 minutes (configurable)

Example:
```bash
# Get token
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=admin&password=admin"

# Use token
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/sites
```

#### User Management

Admins can manage users via:
- **Web Interface**: Users menu (admin only)
- **API Endpoints**:
  - `POST /api/auth/register` - Create user (admin only)
  - `GET /api/auth/users` - List all users (admin only)
  - `PUT /api/auth/users/{id}` - Update user (admin only)
  - `DELETE /api/auth/users/{id}` - Delete user (admin only)

#### Permissions

| Permission | Admin | Operator | Viewer |
|------------|-------|----------|--------|
| View data | ✓ | ✓ | ✓ |
| Create data | ✓ | ✓ | ✗ |
| Edit data | ✓ | ✓ | ✗ |
| Delete data | ✓ | ✓ | ✗ |
| Manage users | ✓ | ✗ | ✗ |
| Export data | ✓ | ✓ | ✓ |
| Import data | ✓ | ✓ | ✗ |

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

### Recently Completed (v1.1.2)
- [x] **Mobile & Tablet Optimization** - Complete responsive design for phones and tablets
- [x] **Touch-Friendly Interface** - 44px minimum button height (iOS/Android guidelines)
- [x] **Mobile Card View** - Tables converted to cards on mobile (< 768px)
- [x] **Responsive Breakpoints** - Mobile (<768px), Tablet (768-991px), Desktop (≥992px)
- [x] **iOS/Android Optimized** - 16px font prevents auto-zoom, optimized touch targets
- [x] **Print Styles** - Clean print layout for reports

### Completed in v1.1.1
- [x] **Full Edit Functionality** - Complete edit support for Sites, US, and Inventario in Web interface
- [x] **37 Inventario Fields Editable** - All 37 fields across 8 tabs fully editable
- [x] **49 US Fields Editable** - All 49 fields across 6 tabs fully editable
- [x] **Form Pre-population** - Forms automatically filled with existing data for editing
- [x] **Session Management Fix** - Resolved SQLAlchemy detached instance errors

### Completed in v1.1.0
- [x] **Analytics Dashboard** - Interactive charts and data visualization
- [x] **8 Chart Types** - Pie, bar, horizontal bar, and doughnut charts
- [x] **Geographic Analysis** - Sites distribution by region and province
- [x] **Chronological Analysis** - US distribution by period
- [x] **Typological Analysis** - US and inventory items by type
- [x] **Conservation Analysis** - Inventory items by conservation state
- [x] **Multi-Interface Charts** - Web UI (Chart.js) and Desktop GUI (matplotlib)

### Completed in v1.0.9
- [x] **Real-time collaboration** - WebSocket support with Flask-SocketIO
- [x] **Live notifications** - Toast notifications for all CRUD operations
- [x] **Online user presence** - See who's currently connected
- [x] **Activity tracking** - Real-time updates when users create/edit/delete data
- [x] **User join/leave events** - Team collaboration awareness

### Completed in v1.0.8
- [x] **Multi-user authentication** - Role-based access control (Admin, Operator, Viewer)
- [x] **JWT authentication** - Secure API access with JSON Web Tokens
- [x] **User management** - Admin interface for creating/editing/deleting users
- [x] **Protected routes** - All web routes require authentication
- [x] **Password security** - Bcrypt hashing for secure password storage

### Completed in v1.0.7
- [x] **Export to Excel/CSV** - Sites, US, Inventario export
- [x] **Batch import from CSV** - With validation and duplicate handling
- [x] **Multi-interface export/import** - Web UI, Desktop GUI, and CLI

### Upcoming Features
- [ ] Docker containerization
- [ ] Cloud deployment guides
- [ ] Advanced search and filtering
- [ ] Offline mode support

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

**Version**: 1.1.2
**Status**: Production/Stable
**Python**: 3.8 - 3.14
**Last Updated**: 2025-10-19

✅ **100% Desktop GUI Feature Parity Achieved**
✅ **Full Python 3.14 Support**
✅ **Tests Included in Distribution**
✅ **Mobile & Tablet Optimized** (NEW in v1.1.2 - Responsive design complete)
✅ **Full Edit Functionality** (v1.1.1 - Web interface CRUD complete)
✅ **Analytics Dashboard** (v1.1.0)
✅ **Real-Time Collaboration** (v1.0.9)
✅ **Multi-User Authentication** (v1.0.8)
✅ **Excel/CSV Export/Import** (v1.0.7)

---

**Made with ❤️ for the Archaeological Community**