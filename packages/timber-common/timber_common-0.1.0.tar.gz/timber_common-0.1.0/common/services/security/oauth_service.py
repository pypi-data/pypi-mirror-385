# timber/common/services/security/oauth_service.py
"""
Core OAuth 2.0 Authorization Server and Resource Protector Service.

This service is framework-agnostic. It implements Authlib's grant types,
token validation, and persistence callbacks using the common service layer
(model_registry and db_service).
"""
# FIX: Use requested import style for generic Authlib components
from authlib.oauth2.rfc6749 import AuthorizationServer 
from authlib.oauth2.rfc6749 import ResourceProtector
from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc6749.resource_protector import TokenValidator
from authlib.oauth2.rfc7636 import CodeChallenge
from datetime import datetime, timedelta, timezone 
from typing import Optional, Dict, Any, List
import uuid
import logging

from common.models.registry import model_registry
from common.services.db_service import db_service

logger = logging.getLogger(__name__)

# --- Helper to get models from registry ---
def _get_model(name: str):
    """Retrieves a model class from the application's registry."""
    model = model_registry.get_model(name)
    if not model:
        logger.error(f"OAuth Model '{name}' not found in registry.")
    return model

# --- Custom Subclass for Core Authlib Integration ---
class ModularAuthorizationServer(AuthorizationServer):
    """
    Subclassing the generic Authlib AuthorizationServer to implement the 
    mandatory query_client and save_token methods using the persistence layer.
    """
    
    def query_client(self, client_id: str):
        """Implements the mandatory client query for Authlib."""
        OAuth2Client = _get_model('OAuth2Client')
        if not OAuth2Client:
            return None
        
        with db_service.session_scope() as session:
            client = session.query(OAuth2Client).filter_by(client_id=client_id).first()
            if client:
                session.expunge(client)
            return client

    def save_token(self, token_data: Dict[str, Any], request: Any):
        """Implements the mandatory token saving for Authlib."""
        OAuth2Token = _get_model('OAuth2Token')
        if not OAuth2Token:
            return

        user_id = getattr(request, 'user', None) and request.user.id or "client_only"

        try:
            # FIX: Manually calculate and supply issued_at/expires_at
            issued_at = datetime.now(timezone.utc)
            expires_in = token_data['expires_in']
            expires_at = issued_at + timedelta(seconds=expires_in)
            
            with db_service.session_scope() as session:
                token = OAuth2Token(
                    user_id=user_id,
                    client_id=request.client.client_id,
                    token_type=token_data['token_type'],
                    access_token=token_data['access_token'],
                    refresh_token=token_data.get('refresh_token'),
                    scope=token_data['scope'],
                    expires_in=expires_in,
                    issued_at=issued_at,
                    expires_at=expires_at 
                )
                session.add(token)
        except Exception as e:
            logger.error(f"Failed to save OAuth token: {e}")


# --- Token Validator for Resource Protection ---
class MyTokenValidator(TokenValidator):
    
    def _to_aware_utc(self, dt: datetime) -> datetime:
        """Helper to force offset-naive datetimes to be timezone-aware UTC."""
        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    def _is_token_expired(self, token: Any) -> bool:
        """Utility to check expiry based on DB columns, since method is missing."""
        if not hasattr(token, 'expires_at') or token.expires_at is None:
            return False 
            
        # FIX 2: Ensure comparison is between two timezone-aware datetimes
        token_expiry_aware = self._to_aware_utc(token.expires_at)
        return datetime.now(timezone.utc) > token_expiry_aware

    def authenticate_token(self, token_string: str):
        """Authenticates an access token from the database."""
        OAuth2Token = _get_model('OAuth2Token')
        if not OAuth2Token: return None
            
        with db_service.session_scope() as session:
            token = session.query(OAuth2Token).filter_by(access_token=token_string).first()
            
            if token and not self._is_token_expired(token):
                session.expunge(token) 
                return token
            return None

    def request_invalid(self, request: Any):
        return False 

    def token_expired(self, token: Any):
        """Checks if the token has expired. Relies on model's logic."""
        # FIX 2: Use internal method to check expiry
        return self._is_token_expired(token)

    def scope_insufficient(self, token: Any, scope: str):
        if not scope: return False
        token_scopes = set(token.scope.split())
        required_scopes = set(scope.split())
        return not token_scopes.issuperset(required_scopes)

# --- OAuth Grant Type Implementations ---

class MyAuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    
    def _to_aware_utc(self, dt: datetime) -> datetime:
        """Helper to force offset-naive datetimes to be timezone-aware UTC."""
        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    def _is_code_expired(self, auth_code: Any) -> bool:
        """Utility to check Auth Code expiry based on DB columns."""
        if not hasattr(auth_code, 'expires_at') or auth_code.expires_at is None:
            return True 
            
        # FIX 2: Ensure comparison is between two timezone-aware datetimes
        code_expiry_aware = self._to_aware_utc(auth_code.expires_at)
        return datetime.now(timezone.utc) > code_expiry_aware

    def save_authorization_code(self, code: str, request: Any):
        """Saves the authorization code and associated request data."""
        OAuth2AuthorizationCode = _get_model('OAuth2AuthorizationCode')
        if not OAuth2AuthorizationCode:
            raise Exception("Authorization Code Model not available.")
            
        issued_at = datetime.now(timezone.utc)
        expires_at = issued_at + timedelta(minutes=5) # Auth Code standard expiry
        
        with db_service.session_scope() as session:
            auth_code = OAuth2AuthorizationCode(
                user_id=request.user.id,
                client_id=request.client.client_id, 
                code=code,
                redirect_uri=request.redirect_uri,
                scope=request.scope,
                issued_at=issued_at,
                expires_at=expires_at 
            )
            session.add(auth_code)
            
            # FIX: Expunge object before returning it to the test/Authlib for later use
            session.flush()
            session.expunge(auth_code)
            
            return auth_code

    def query_authorization_code(self, code: str, client: Any):
        """Retrieves an authorization code from the database."""
        OAuth2AuthorizationCode = _get_model('OAuth2AuthorizationCode')
        if not OAuth2AuthorizationCode: return None
            
        with db_service.session_scope() as session:
            auth_code = session.query(OAuth2AuthorizationCode).filter_by(
                code=code, client_id=client.client_id).first() 
                
            if auth_code and not self._is_code_expired(auth_code):
                session.expunge(auth_code) 
                return auth_code
            return None

    def delete_authorization_code(self, authorization_code: Any):
        # ... (remains the same) ...
        OAuth2AuthorizationCode = _get_model('OAuth2AuthorizationCode')
        if not OAuth2AuthorizationCode: return
        with db_service.session_scope() as session:
            session.delete(session.merge(authorization_code))

    def authenticate_user(self, authorization_code: Any):
        # ... (remains the same) ...
        User = _get_model('User')
        if not User: return None
        with db_service.session_scope() as session:
            user = session.query(User).get(authorization_code.user_id)
            if user: session.expunge(user) 
            return user

class MyRefreshTokenGrant(grants.RefreshTokenGrant):
    
    def _is_refresh_token_active(self, token: Any) -> bool:
        """Utility to check refresh token validity (simple, based on access token expiry)."""
        # FIX: Access the token validator via the server object
        validator = self.server.resource_protector.get_token_validator(token.token_type)
        return not validator._is_token_expired(token)

    def authenticate_refresh_token(self, refresh_token: str):
        """Authenticates the refresh token from the database."""
        OAuth2Token = _get_model('OAuth2Token')
        if not OAuth2Token: return None
            
        with db_service.session_scope() as session:
            token = session.query(OAuth2Token).filter_by(refresh_token=refresh_token).first()
            
            # FIX: Use internal method
            if token and self._is_refresh_token_active(token): 
                session.expunge(token) 
                return token
            return None

    def create_access_token(self, token: Any, client: Any, request: Any):
        # ... (remains the same) ...
        OAuth2Token = _get_model('OAuth2Token')
        if not OAuth2Token: return None
            
        with db_service.session_scope() as session:
            old_token = session.merge(token)
            session.delete(old_token)
            
            issued_at = datetime.now(timezone.utc)
            expires_at = issued_at + timedelta(seconds=3600)
            
            new_token = OAuth2Token(
                user_id=token.user_id,
                client_id=client.client_id,
                token_type=token.token_type,
                scope=request.scope,
                access_token=str(uuid.uuid4()), 
                refresh_token=str(uuid.uuid4()), 
                expires_in=3600,
                issued_at=issued_at,
                expires_at=expires_at
            )
            session.add(new_token)
            session.expunge(new_token) 
            return new_token

class MyClientCredentialsGrant(grants.ClientCredentialsGrant):
    def authenticate_client(self, client: Any):
        return client 

    def create_access_token(self, client: Any, request: Any):
        OAuth2Token = _get_model('OAuth2Token')
        if not OAuth2Token: return None
            
        with db_service.session_scope() as session:
            issued_at = datetime.now(timezone.utc)
            expires_at = issued_at + timedelta(seconds=3600)
            
            new_token = OAuth2Token(
                user_id="client_only", 
                client_id=client.client_id,
                token_type='bearer',
                scope=request.scope,
                access_token=str(uuid.uuid4()),
                expires_in=3600,
                issued_at=issued_at,
                expires_at=expires_at
            )
            session.add(new_token)
            session.expunge(new_token) 
            return new_token

# --- Core Service Objects ---

authorization = ModularAuthorizationServer()
resource_protector = ResourceProtector() 

# --- Initialization Function (Simplified for library use) ---

def init_oauth_service():
    """
    Initializes the core OAuth server logic.
    """
    logger.info("Initializing core OAuth service objects (Framework-Agnostic).")
    
    # Register Grant Types
    authorization.register_grant(MyAuthorizationCodeGrant, [CodeChallenge(required=False)]) 
    authorization.register_grant(MyRefreshTokenGrant)
    authorization.register_grant(MyClientCredentialsGrant)
    
    # FIX: Register the validator explicitly
    resource_protector.register_token_validator(MyTokenValidator())
    
    # Attach resource protector instance to the authorization server instance
    authorization.resource_protector = resource_protector 
    
    logger.info("OAuth service initialized with Authorization Code, Refresh, and Client Credentials grants.")

# Call the initialization function immediately to set up the grants
init_oauth_service()


__all__ = [
    'authorization',
    'resource_protector',
    'init_oauth_service',
    'MyAuthorizationCodeGrant',
    'MyRefreshTokenGrant',
    '_get_model', 
]