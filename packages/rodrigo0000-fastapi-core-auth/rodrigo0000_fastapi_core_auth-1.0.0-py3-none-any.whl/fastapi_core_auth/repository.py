"""
Authentication repository - siguiendo el patrón exacto de Autogrid
"""

import re
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..core.repository import BaseRepository
from ..core.security import get_password_hash, verify_password
from ..models.user import User

class AuthRepository(BaseRepository[User]):
    """Authentication repository siguiendo el patrón de Autogrid"""
    
    def __init__(self):
        super().__init__(User)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return verify_password(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return get_password_hash(password)

    @staticmethod
    def validate_password_requirements(password: str) -> str | None:
        """
        Validate password strength requirements.
        Returns None if valid, otherwise returns an error message string.
        Requirements:
        - At least 8 characters
        - At least one lowercase letter
        - At least one uppercase letter
        - At least one digit
        - At least one special character
        """
        if not isinstance(password, str) or len(password) < 8:
            return "Password must be at least 8 characters long."
        if not re.search(r"[a-z]", password):
            return "Password must include at least one lowercase letter."
        if not re.search(r"[A-Z]", password):
            return "Password must include at least one uppercase letter."
        if not re.search(r"\d", password):
            return "Password must include at least one digit."
        if not re.search(r"[^A-Za-z0-9]", password):
            return "Password must include at least one special character."
        return None

    def authenticate_user(self, db: Session, username_or_email: str, password: str):
        # Allow authentication by username OR email
        user = db.query(User).filter(
            or_(User.username == username_or_email, User.email == username_or_email)
        ).first()
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def create_user(self, db: Session, username: str, email: str, password: str):
        # Verificar si el correo ya existe antes de crear el usuario
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            return None, "This email is already registered"
            
        # Verificar si el nombre de usuario ya existe
        existing_username = db.query(User).filter(User.username == username).first()
        if existing_username:
            return None, "This username is already in use"
            
        # Si no existe, crear el usuario
        hashed_password = self.get_password_hash(password)
        user = User(username=username, email=email, hashed_password=hashed_password)

        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user, None
        except Exception as e:
            db.rollback()
            return None, "Error Creating User: " + str(e)
