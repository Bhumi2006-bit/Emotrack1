"""Small authentication helpers shared by protected API routes.

This project keeps its simple local token format, but the user id is read only
from the Authorization header.  Clients can no longer select another user's
id with a query parameter or request body.
"""
from fastapi import Header, HTTPException
from database.models import get_user_by_id

TOKEN_PREFIX = "Bearer emotrack_token_"

def get_current_user_id(authorization: str | None = Header(default=None)) -> int:
    if not authorization or not authorization.startswith(TOKEN_PREFIX):
        raise HTTPException(status_code=401, detail="Please sign in to continue.")
    try:
        user_id = int(authorization[len(TOKEN_PREFIX):])
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid session token.")
    if not get_user_by_id(user_id):
        raise HTTPException(status_code=401, detail="Session user no longer exists.")
    return user_id
