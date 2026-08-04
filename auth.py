import hashlib
import os
import re
from typing import Tuple, Optional
import database

def hash_password(password: str) -> str:
    """
    Hashes a password securely using PBKDF2-HMAC-SHA256 with a random salt.
    Format: salt_hex:hash_hex
    """
    salt = os.urandom(16)
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return f"{salt.hex()}:{pw_hash.hex()}"

def verify_password(stored_password_hash: str, provided_password: str) -> bool:
    """
    Verifies a password against the stored secure hash.
    """
    try:
        salt_hex, hash_hex = stored_password_hash.split(':')
        salt = bytes.fromhex(salt_hex)
        pw_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
        return pw_hash.hex() == hash_hex
    except Exception:
        return False

def is_valid_email(email: str) -> bool:
    """
    Validates email format using basic regex.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def is_valid_username(username: str) -> bool:
    """
    Validates that a username is alphanumeric and between 3 to 20 characters.
    """
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return bool(re.match(pattern, username))

def register_user(username: str, email: str, password: str) -> Tuple[bool, str]:
    """
    Registers a new user after validation.
    Returns: (Success Boolean, Message String)
    """
    username = username.strip()
    email = email.strip()
    
    if not username or not email or not password:
        return False, "All fields are required."
        
    if not is_valid_username(username):
        return False, "Username must be 3-20 characters long and contain only letters, numbers, or underscores."
        
    if not is_valid_email(email):
        return False, "Please enter a valid email address."
        
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
        
    # Check if user already exists
    existing_user = database.get_user(username)
    if existing_user:
        return False, f"Username '{username}' is already taken."
        
    # Hash password and create user
    password_hash = hash_password(password)
    success = database.create_user(username, email, password_hash)
    if success:
        return True, "Registration successful! You can now log in."
    else:
        return False, "Registration failed due to a database error."

def login_user(username: str, password: str) -> Tuple[Optional[dict], str]:
    """
    Logs in a user by verifying their credentials.
    Returns: (User Dict if successful, Message String)
    """
    username = username.strip()
    if not username or not password:
        return None, "Please fill in all fields."
        
    user = database.get_user(username)
    if not user:
        return None, "Invalid username or password."
        
    if verify_password(user["password_hash"], password):
        # Return user without password hash for safety
        user_data = {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"]
        }
        return user_data, "Login successful!"
    else:
        return None, "Invalid username or password."

def change_user_password(user_id: int, username: str, old_password: str, new_password: str) -> Tuple[bool, str]:
    """
    Changes a user's password after verifying their old password.
    Returns: (Success Boolean, Message String)
    """
    if not old_password or not new_password:
        return False, "Please fill in all fields."
        
    if len(new_password) < 6:
        return False, "New password must be at least 6 characters long."
        
    # Verify current credentials
    user = database.get_user(username)
    if not user or not verify_password(user["password_hash"], old_password):
        return False, "Incorrect current password."
        
    # Update password
    new_hash = hash_password(new_password)
    success = database.update_user_password(user_id, new_hash)
    if success:
        return True, "Password updated successfully!"
    else:
        return False, "Failed to update password."
