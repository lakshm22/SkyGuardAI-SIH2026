import os
import secrets
from fastapi import Header, HTTPException

ADMIN_USERNAME = os.getenv('SKYGUARD_ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('SKYGUARD_ADMIN_PASSWORD', 'SkyGuard@123')
_tokens: set[str] = set()

def login(username: str, password: str):
    if not secrets.compare_digest(username, ADMIN_USERNAME) or not secrets.compare_digest(password, ADMIN_PASSWORD):
        raise HTTPException(status_code=401, detail='Invalid admin credentials')
    token = secrets.token_urlsafe(32)
    _tokens.add(token)
    return token

def require_admin(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Admin authentication required')
    token = authorization.split(' ', 1)[1]
    if token not in _tokens:
        raise HTTPException(status_code=401, detail='Invalid or expired admin token')
    return True
