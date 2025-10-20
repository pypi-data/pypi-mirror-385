"""
Setup authentication system

This script:
1. Creates the users table
2. Creates default admin user if no users exist
"""

import sys
from pathlib import Path
from sqlalchemy import text

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pyarchinit_mini.database import DatabaseConnection, DatabaseManager
from pyarchinit_mini.services.user_service import UserService


def create_users_table(connection):
    """Create users table if it doesn't exist"""
    # Check if table already exists
    result = connection.execute(text(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
    )).fetchone()

    if result:
        print("Users table already exists, skipping creation")
        return

    # Create users table
    connection.execute(text("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(100) NOT NULL UNIQUE,
            full_name VARCHAR(100),
            hashed_password VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'viewer',
            is_active BOOLEAN NOT NULL DEFAULT 1,
            is_superuser BOOLEAN NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            last_login TIMESTAMP
        )
    """))

    # Create indexes
    connection.execute(text("CREATE INDEX ix_users_username ON users (username)"))
    connection.execute(text("CREATE INDEX ix_users_email ON users (email)"))

    print("Users table created successfully")


def setup_authentication(database_url: str = None):
    """
    Setup authentication system

    Args:
        database_url: Database URL (default: SQLite in current directory)
    """
    # Use default database if not specified
    if not database_url:
        database_url = "sqlite:///./pyarchinit_mini.db"

    print(f"Setting up authentication for database: {database_url}")

    # Create database connection
    db_conn = DatabaseConnection(database_url)
    db_manager = DatabaseManager(db_conn)

    # Run migration
    print("\n1. Creating users table...")
    with db_conn.engine.connect() as conn:
        create_users_table(conn)
        conn.commit()

    # Create default admin
    print("\n2. Creating default admin user...")
    user_service = UserService(db_manager)
    admin = user_service.create_default_admin()

    if admin:
        print("✓ Default admin user created")
        print(f"  Username: admin")
        print(f"  Password: admin")
        print(f"  Email: admin@pyarchinit.local")
        print("\n⚠️  IMPORTANT: Change the admin password immediately!")
    else:
        print("✓ Users already exist, skipping admin creation")

    print("\n✓ Authentication setup complete!")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Setup authentication system")
    parser.add_argument(
        "--database-url",
        "-d",
        help="Database URL (default: sqlite:///./pyarchinit_mini.db)"
    )

    args = parser.parse_args()

    setup_authentication(args.database_url)


if __name__ == "__main__":
    main()
