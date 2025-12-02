"""
Autenticación JWT compatible con Laravel
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verificar token JWT generado por Laravel
    
    Args:
        credentials: Credenciales HTTP Bearer
        
    Returns:
        dict: Payload del token decodificado
        
    Raises:
        HTTPException: Si el token es inválido o expirado
    """
    token = credentials.credentials
    
    try:
        # Decodificar token con la misma secret que Laravel
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_aud,
            issuer=settings.jwt_iss
        )
        
        logger.info(f"Token válido para usuario: {payload.get('sub')}")
        return payload
        
    except JWTError as e:
        logger.error(f"Error al validar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(token_data: dict = Depends(verify_token)) -> dict:
    """
    Obtener datos del usuario actual desde el token
    
    Args:
        token_data: Payload del token verificado
        
    Returns:
        dict: Información del usuario
    """
    return {
        "user_id": token_data.get("sub"),
        "email": token_data.get("email"),
        "role": token_data.get("role")
    }


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Verificar que el usuario sea admin
    
    Args:
        current_user: Usuario actual
        
    Returns:
        dict: Usuario si es admin
        
    Raises:
        HTTPException: Si no es admin
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de administrador"
        )
    return current_user
