"""
Authentication router - siguiendo el patrón exacto de Autogrid
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import create_access_token, get_current_user
from .repository import AuthRepository
from .schemas import LoginRequest, RegisterRequest, UserResponse, AuthResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=AuthResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    repo = AuthRepository()
    
    # Validate password requirements
    pwd_error = repo.validate_password_requirements(request.password)
    if pwd_error:
        raise HTTPException(status_code=400, detail=pwd_error)
    
    # Crear usuario con el nuevo método que verifica email y username
    user, error_message = repo.create_user(db, request.username, request.email, request.password)
    
    # Si hay un error, lanzar una excepción HTTP con el mensaje
    if error_message:
        raise HTTPException(status_code=400, detail=error_message)

    # Create access token
    token = create_access_token({"sub": user.username, "id": user.id})
    
    return AuthResponse(user=UserResponse.from_orm(user), token=token)

@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    repo = AuthRepository()
    identifier = request.username or request.email
    if not identifier:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email is required")
    
    user = repo.authenticate_user(db, identifier, request.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    
    token = create_access_token({"sub": user.username, "id": user.id})
    return AuthResponse(user=UserResponse.from_orm(user), token=token)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = AuthRepository()
    user = db.query(repo.model).filter(repo.model.id == current_user["id"]).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(user)

@router.post("/refresh")
def refresh_token(current_user: dict = Depends(get_current_user)):
    """Refresh access token"""
    token = create_access_token({"sub": current_user["username"], "id": current_user["id"]})
    return {"access_token": token, "token_type": "bearer"}
