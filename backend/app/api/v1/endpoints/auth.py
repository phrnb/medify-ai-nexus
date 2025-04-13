
from datetime import timedelta
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import logging

from app.api.v1.deps import get_db, get_current_user, log_user_activity
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    generate_totp_secret,
    generate_totp_uri,
    generate_qr_code,
    verify_totp
)
from app.crud.crud_user import user as crud_user
from app.models.user import User
from app.models.activity_log import ActivityTypeEnum
from app.schemas.token import Token, RefreshToken, TwoFactorToken
from app.schemas.user import User as UserSchema

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/login", response_model=Token)
def login_access_token(
    request: Request,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud_user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        logger.warning(f"Login failed for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    elif not crud_user.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    
    # Update last login timestamp
    user.last_login = db.func.now()
    db.add(user)
    db.commit()
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=user,
        activity_type=ActivityTypeEnum.login,
        description=f"User logged in: {user.email}"
    )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(user.id)
    
    # If two-factor auth is enabled, return special token that requires 2FA verification
    if user.two_factor_enabled:
        access_token = create_access_token(
            user.id, expires_delta=access_token_expires, two_factor_verified=False
        )
        return Token(
            access_token=access_token,
            token_type="bearer",
            refresh_token=refresh_token,
            two_factor_required=True
        )
    
    # If no 2FA, return normal token
    access_token = create_access_token(
        user.id, expires_delta=access_token_expires, two_factor_verified=True
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
        two_factor_required=False
    )

@router.post("/refresh", response_model=Token)
def refresh_token(
    refresh_token_in: RefreshToken = Body(...),
    db: Session = Depends(get_db)
) -> Any:
    """
    Refresh access token
    """
    try:
        payload = jwt.decode(
            refresh_token_in.refresh_token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError) as e:
        logger.error(f"Refresh token validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = crud_user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # If 2FA is enabled, require verification
    if user.two_factor_enabled:
        access_token = create_access_token(
            user.id, expires_delta=access_token_expires, two_factor_verified=False
        )
        return Token(
            access_token=access_token,
            token_type="bearer",
            refresh_token=create_refresh_token(user.id),
            two_factor_required=True
        )
    
    # Otherwise, issue a standard token
    access_token = create_access_token(
        user.id, expires_delta=access_token_expires, two_factor_verified=True
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        refresh_token=create_refresh_token(user.id),
        two_factor_required=False
    )

@router.post("/2fa/verify", response_model=Token)
def verify_two_factor(
    request: Request,
    two_factor_token: TwoFactorToken = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Verify two-factor authentication code
    """
    if not current_user.two_factor_enabled or not current_user.two_factor_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Two-factor authentication not enabled for this user"
        )
    
    if not verify_totp(current_user.two_factor_secret, two_factor_token.code):
        logger.warning(f"Failed 2FA attempt for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid two-factor code"
        )
    
    # Log successful 2FA verification
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.login,
        description=f"User completed two-factor authentication: {current_user.email}"
    )
    
    # Generate new tokens with 2FA verified
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        current_user.id, expires_delta=access_token_expires, two_factor_verified=True
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        refresh_token=create_refresh_token(current_user.id),
        two_factor_required=False
    )

@router.post("/2fa/setup", response_model=dict)
def setup_two_factor(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Set up two-factor authentication for a user
    """
    # Generate a new secret
    secret = crud_user.generate_2fa_secret(db, user_id=current_user.id)
    
    # Generate the provisioning URI for the QR code
    totp_uri = generate_totp_uri(secret, current_user.email)
    
    # Generate QR code
    qr_code = generate_qr_code(totp_uri)
    
    return {
        "secret": secret,
        "qr_code": qr_code
    }

@router.post("/2fa/enable", response_model=UserSchema)
def enable_two_factor(
    request: Request,
    two_factor_token: TwoFactorToken = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Enable two-factor authentication after verification
    """
    if not current_user.two_factor_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Two-factor authentication not set up for this user"
        )
    
    # Verify the provided code
    if not verify_totp(current_user.two_factor_secret, two_factor_token.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid two-factor code"
        )
    
    # Enable 2FA for the user
    user = crud_user.enable_2fa(db, user_id=current_user.id)
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.update,
        description=f"User enabled two-factor authentication: {current_user.email}",
        resource_type="user",
        resource_id=current_user.id
    )
    
    return user

@router.post("/2fa/disable", response_model=UserSchema)
def disable_two_factor(
    request: Request,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Disable two-factor authentication
    Requires a token that has already been verified with 2FA
    """
    if not current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Two-factor authentication not enabled for this user"
        )
    
    # Disable 2FA for the user
    user = crud_user.disable_2fa(db, user_id=current_user.id)
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.update,
        description=f"User disabled two-factor authentication: {current_user.email}",
        resource_type="user",
        resource_id=current_user.id
    )
    
    return user

@router.post("/logout")
def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Logout a user (client should discard tokens)
    """
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.logout,
        description=f"User logged out: {current_user.email}"
    )
    
    return {"message": "Logout successful"}
