from fastapi import Request, HTTPException, status
from core.state import get_global_state

async def verify_api_key(request: Request):
    state = get_global_state()
    expected_key = getattr(state.config, "api_key", None)
    
    # If no key is set in config, allow access
    if not expected_key:
        return
        
    error_detail = {
        "error": {
            "message": "Unauthorized",
            "type": "authentication_error"
        }
    }
        
    auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_detail
        )
        
    scheme, _, token = auth_header.partition(" ")
    if scheme.lower() != "bearer" or token.strip() != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_detail
        )
