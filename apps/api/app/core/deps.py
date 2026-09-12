from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models import User
from app.models.enums import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def _unauthorized(message: str = "Not authenticated") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"error": {"code": "UNAUTHENTICATED", "message": message}},
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    if token is None:
        raise _unauthorized()
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise _unauthorized("Invalid or expired token")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if user is None:
        raise _unauthorized("User no longer exists")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "Admin access required"}},
        )
    return user


def require_self_or_admin(target_user_id: int, user: User = Depends(get_current_user)) -> User:
    if user.id != target_user_id and user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "You may not access another user's data"}},
        )
    return user
