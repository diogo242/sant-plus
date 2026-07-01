from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import jwt
from data_mock import PATIENTS_DB

SECRET_KEY = "sante-plus-secret-2026-hackathon"
ALGORITHM = "HS256"

router = APIRouter()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    patient: dict

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    if request.email not in PATIENTS_DB:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    patient = PATIENTS_DB[request.email]
    
    # Demo: password = "demo123"
    if request.password != "demo123":
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    expire = datetime.utcnow() + timedelta(minutes=30)
    token = jwt.encode({
        "email": request.email,
        "name": patient["name"],
        "exp": expire
    }, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"access_token": token, "token_type": "bearer", "patient": patient}

@router.get("/me")
def get_current_user(token: str = None):
    if not token:
        raise HTTPException(status_code=401, detail="Token requis")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        if email not in PATIENTS_DB:
            raise HTTPException(status_code=404, detail="Patient non trouvé")
        return PATIENTS_DB[email]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Token invalide")
