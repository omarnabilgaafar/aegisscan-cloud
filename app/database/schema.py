from app.database.db import get_connection


def ensure_column(cursor, table_name, column_name, ddl):
    columns = [row[1] for row in cursor.execute(f"PRAGMA table_info({table_name})").fetchall()]
    if column_name not in columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {ddl}")


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            plan TEXT NOT NULL DEFAULT 'Starter',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    ensure_column(cursor, 'users', 'role', "role TEXT DEFAULT 'user'")
    ensure_column(cursor, 'users', 'plan', "plan TEXT DEFAULT 'Starter'")
    ensure_column(cursor, 'users', 'organization_id', "organization_id INTEGER")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_url TEXT NOT NULL,
            total_findings INTEGER NOT NULL DEFAULT 0,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    ensure_column(cursor, 'scans', 'user_id', 'user_id INTEGER')
    ensure_column(cursor, 'scans', 'organization_id', 'organization_id INTEGER')

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vulnerabilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id INTEGER NOT NULL,
            vuln_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            url TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (scan_id) REFERENCES scans(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            organization_id INTEGER,
            api_key TEXT NOT NULL UNIQUE,
            label TEXT DEFAULT 'Default API Key',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("INSERT OR IGNORE INTO organizations (id, name, plan) VALUES (1, 'Demo Workspace', 'Professional')")
    cursor.execute("UPDATE users SET organization_id = COALESCE(organization_id, 1), role = COALESCE(role, 'user'), plan = COALESCE(plan, 'Professional')")

    conn.commit()
    conn.close()
