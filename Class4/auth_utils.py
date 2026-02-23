"""
Simple authentication for multi-tenant simulation.
For Azure production, replace with Azure AD B2C / Entra ID.
"""
import json
import os
from pathlib import Path
from passlib.hash import bcrypt

DATA_DIR = Path(__file__).parent / "data"
USERS_FILE = DATA_DIR / "users.json"
ADMIN_EMAIL = "admin@cloudstrategy.local"


def _ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)


def _load_users() -> dict:
    _ensure_data_dir()
    if USERS_FILE.exists():
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {"users": [], "admins": [ADMIN_EMAIL]}


def _save_users(data: dict):
    _ensure_data_dir()
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _bootstrap_admin():
    """Create default admin user if none exist."""
    data = _load_users()
    if not data["users"]:
        default_pw = "admin123"
        data["users"].append({
            "email": ADMIN_EMAIL,
            "password_hash": bcrypt.hash(default_pw),
        })
        _save_users(data)


def register_user(email: str, password: str) -> tuple[bool, str]:
    """Register a new user. Returns (success, message)."""
    _bootstrap_admin()
    data = _load_users()
    emails = [u["email"] for u in data["users"]]
    if email in emails:
        return False, "Email already registered"
    data["users"].append({
        "email": email,
        "password_hash": bcrypt.hash(password),
    })
    _save_users(data)
    return True, "Account created successfully"


def verify_user(email: str, password: str) -> tuple[bool, bool]:
    """Verify credentials. Returns (success, is_admin)."""
    _bootstrap_admin()
    data = _load_users()
    for u in data["users"]:
        if u["email"] == email and bcrypt.verify(password, u["password_hash"]):
            return True, email in data.get("admins", [ADMIN_EMAIL])
    return False, False


def is_admin(email: str) -> bool:
    data = _load_users()
    return email in data.get("admins", [ADMIN_EMAIL])


def list_users() -> list[dict]:
    """List all users (admin only)."""
    data = _load_users()
    return [
        {"email": u["email"], "is_admin": u["email"] in data.get("admins", [])}
        for u in data["users"]
    ]


def delete_user(email: str) -> tuple[bool, str]:
    """Delete user by email (admin only)."""
    data = _load_users()
    if email in data.get("admins", []):
        return False, "Cannot delete admin user"
    data["users"] = [u for u in data["users"] if u["email"] != email]
    _save_users(data)
    return True, "User deleted"


def add_admin(email: str) -> tuple[bool, str]:
    """Add admin (admin only)."""
    data = _load_users()
    emails = [u["email"] for u in data["users"]]
    if email not in emails:
        return False, "User does not exist"
    if "admins" not in data:
        data["admins"] = [ADMIN_EMAIL]
    if email not in data["admins"]:
        data["admins"].append(email)
    _save_users(data)
    return True, "Admin added"
