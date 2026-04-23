from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token
from pydantic import BaseModel

auth_router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str

@auth_router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Mock temporário de autenticação. 
    Permite rodar a documentação exigindo token.
    Aceita qualquer usuário com senha 'admin'.
    """
    if form_data.password != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha incorreta. Use 'admin'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(subject=form_data.username)
    return {"access_token": access_token, "token_type": "bearer"}
