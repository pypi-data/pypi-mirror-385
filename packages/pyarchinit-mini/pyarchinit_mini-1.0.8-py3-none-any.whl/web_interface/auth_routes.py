"""
Authentication routes for Flask web interface
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from functools import wraps

from pyarchinit_mini.services.user_service import UserService
from pyarchinit_mini.models.user import UserRole


# Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# User class for Flask-Login
class User(UserMixin):
    """User class for Flask-Login"""

    def __init__(self, user_dict):
        self.id = user_dict["id"]
        self.username = user_dict["username"]
        self.email = user_dict["email"]
        self.full_name = user_dict["full_name"]
        self.role = user_dict["role"]
        self.is_active_user = user_dict["is_active"]
        self.is_superuser = user_dict["is_superuser"]

    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return self.is_active_user

    def has_role(self, role):
        """Check if user has specific role"""
        return self.role == role

    def can_create(self):
        """Check if user can create records"""
        return self.role in [UserRole.ADMIN.value, UserRole.OPERATOR.value]

    def can_edit(self):
        """Check if user can edit records"""
        return self.role in [UserRole.ADMIN.value, UserRole.OPERATOR.value]

    def can_delete(self):
        """Check if user can delete records"""
        return self.role in [UserRole.ADMIN.value, UserRole.OPERATOR.value]

    def can_manage_users(self):
        """Check if user can manage other users"""
        return self.role == UserRole.ADMIN.value or self.is_superuser


# Permission decorators
def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.can_manage_users():
            flash('Accesso negato. Permessi amministratore richiesti.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def write_permission_required(f):
    """Decorator to require write permission (operator or admin)"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.can_create():
            flash('Accesso negato. Permessi di scrittura richiesti.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def init_login_manager(app, user_service):
    """
    Initialize Flask-Login

    Args:
        app: Flask app
        user_service: UserService instance
    """
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Devi effettuare il login per accedere a questa pagina."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID"""
        user_dict = user_service.get_user_by_id(int(user_id))
        if user_dict:
            return User(user_dict)
        return None

    return login_manager


# Routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', 'off') == 'on'

        # Debug logging
        print(f"[LOGIN] Username: {username}, Remember: {remember}")

        # Get user service from app context
        from flask import current_app
        user_service = current_app.user_service

        # Debug: Check if user exists first
        print(f"[DEBUG] Looking up user: {username}")
        user_check = user_service.get_user_by_username(username)
        print(f"[DEBUG] User found: {user_check is not None}")
        if user_check:
            print(f"[DEBUG] User data: username={user_check.get('username')}, role={user_check.get('role')}, active={user_check.get('is_active')}")
            print(f"[DEBUG] Has hashed_password: {'hashed_password' in user_check}")

        # Authenticate
        user_dict = user_service.authenticate_user(username, password)
        print(f"[LOGIN] Authentication result: {user_dict is not None}")

        if user_dict:
            user = User(user_dict)
            login_user(user, remember=remember)
            print(f"[LOGIN] User logged in: {user.username}")
            flash(f'Benvenuto, {user.username}!', 'success')

            # Redirect to next page or index
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            print(f"[LOGIN] Authentication failed for username: {username}")
            flash('Username o password non corretti.', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    flash('Logout effettuato con successo.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/users')
@admin_required
def users_list():
    """User management page (admin only)"""
    from flask import current_app
    user_service = current_app.user_service

    users = user_service.get_all_users()
    return render_template('auth/users.html', users=users, current_user=current_user)


@auth_bp.route('/users/create', methods=['POST'])
@admin_required
def create_user():
    """Create new user (admin only)"""
    from flask import current_app
    user_service = current_app.user_service

    try:
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        role = request.form.get('role', 'viewer')

        user = user_service.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            role=UserRole(role)
        )

        flash(f'Utente {username} creato con successo!', 'success')
    except ValueError as e:
        flash(f'Errore: {str(e)}', 'error')
    except Exception as e:
        flash(f'Errore durante la creazione utente: {str(e)}', 'error')

    return redirect(url_for('auth.users_list'))


@auth_bp.route('/users/<int:user_id>/edit', methods=['POST'])
@admin_required
def edit_user(user_id):
    """Edit user (admin only)"""
    from flask import current_app
    user_service = current_app.user_service

    try:
        updates = {}

        if request.form.get('email'):
            updates['email'] = request.form.get('email')
        if request.form.get('full_name'):
            updates['full_name'] = request.form.get('full_name')
        if request.form.get('role'):
            updates['role'] = UserRole(request.form.get('role'))
        if request.form.get('password'):
            updates['password'] = request.form.get('password')

        updates['is_active'] = request.form.get('is_active') == '1'

        user = user_service.update_user(user_id, **updates)

        if user:
            flash('Utente aggiornato con successo!', 'success')
        else:
            flash('Utente non trovato.', 'error')

    except Exception as e:
        flash(f'Errore durante l\'aggiornamento: {str(e)}', 'error')

    return redirect(url_for('auth.users_list'))


@auth_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete user (admin only)"""
    from flask import current_app
    user_service = current_app.user_service

    # Prevent deleting yourself
    if user_id == current_user.id:
        flash('Non puoi eliminare il tuo account!', 'error')
        return redirect(url_for('auth.users_list'))

    try:
        deleted = user_service.delete_user(user_id)

        if deleted:
            flash('Utente eliminato con successo!', 'success')
        else:
            flash('Utente non trovato.', 'error')

    except Exception as e:
        flash(f'Errore durante l\'eliminazione: {str(e)}', 'error')

    return redirect(url_for('auth.users_list'))
