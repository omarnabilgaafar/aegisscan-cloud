from app.database.db import get_connection
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

ALLOWED_PLANS = {"Starter", "Professional", "Enterprise"}

def register_controller(username: str, email: str, password: str, organization_name: str, plan: str):
    if not username or not email or not password or not organization_name:
        return False, "All fields are required."
    if plan not in ALLOWED_PLANS:
        plan = "Starter"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return False, "Username or email already exists."

    cursor.execute("INSERT INTO organizations (name, plan) VALUES (?, ?)", (organization_name, plan))
    org_id = cursor.lastrowid

    password_hash = generate_password_hash(password)
    role = "admin" if username.lower() == "admin" else "user"
    cursor.execute(
        "INSERT INTO users (username, email, password_hash, role, plan, organization_id) VALUES (?, ?, ?, ?, ?, ?)",
        (username, email, password_hash, role, plan, org_id)
    )
    user_id = cursor.lastrowid

    api_key = f"ags_{secrets.token_hex(16)}"
    cursor.execute(
        "INSERT INTO api_keys (user_id, organization_id, api_key, label) VALUES (?, ?, ?, ?)",
        (user_id, org_id, api_key, "Default API Key")
    )
    conn.commit()
    conn.close()
    return True, "Registered successfully."


def login_controller(username: str, password: str):
    if not username or not password:
        return False, "Username and password are required."

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT u.*, o.name AS organization_name, o.plan AS organization_plan
        FROM users u
        LEFT JOIN organizations o ON o.id = u.organization_id
        WHERE u.username = ?
        """,
        (username,)
    )
    user = cursor.fetchone()
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return False, "Invalid credentials."

    return True, {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"] or "user",
        "plan": user["plan"] or user["organization_plan"] or "Starter",
        "organization_id": user["organization_id"],
        "organization_name": user["organization_name"] or "Personal",
    }


def logout_controller():
    return True
