"""
Servicio OIDC para autenticación y operaciones de usuario final
"""
from typing import Optional
from jwcrypto.jwk import JWK

from keycloak import KeycloakAdmin, KeycloakOpenID

from ...dtos import (
    KeycloakConfig
)

from ...daos import (
    UserDAO,
    GroupDAO
)

from ...token import TokenDAO


class KeycloakAPIClient:
    """
    Cliente OIDC para operaciones service-account en Keycloak.
    """

    REALM_NAME = 'main-realm'

    def __init__(self, config: Optional[KeycloakConfig] = None):
        self.config = config or KeycloakConfig()
        self._admin_service: Optional[KeycloakAdmin] = None
        self._openid_service: Optional[KeycloakOpenID] = None
        self._token_expires_at: Optional[float] = None

        if not self.config.api_client_secret:
            raise ValueError("El secreto del cliente API no está configurado.")
        else:
            self.client_secret = self.config.api_client_secret
    
    def get_public_key(self) -> JWK:
        """Obtiene la clave pública del realm para validar tokens"""
        public_key_pem = self.openid_service.public_key()
        public_key_pem = f"-----BEGIN PUBLIC KEY-----\n{public_key_pem}\n-----END PUBLIC KEY-----"
        self._public_key = JWK.from_pem(public_key_pem.encode("utf-8"))
    
    @property
    def public_key(self) -> JWK:
        return self._public_key
    
    @property
    def admin_service(self) -> KeycloakAdmin:
        """Instancia autenticada de KeycloakAdmin con renovación automática de token"""
        if not self._admin_service:    
            # Crear KeycloakAdmin
            self._admin_service = KeycloakAdmin(
                server_url=self.config.url,
                realm_name=self.REALM_NAME,
                client_id='api',
                client_secret_key=self.client_secret,
                verify=self.config.verify_ssl
            )
        return self._admin_service
        
    @property
    def openid_service(self) -> KeycloakOpenID:
        """Instancia autenticada de KeycloakOpenID"""
        if not self._openid_service:
            # Crear KeycloakOpenID
            self._openid_service = KeycloakOpenID(
                server_url=self.config.url,
                realm_name=self.REALM_NAME,
                client_id='api',
                client_secret_key=self.client_secret,
                verify=self.config.verify_ssl
            )

        return self._openid_service
    
    @property
    def token(self) -> TokenDAO:
        """DAO para gestión de tokens"""
        return TokenDAO(self.openid_service)
    
    @property
    def user(self) -> UserDAO:
        """DAO para gestión de usuarios"""
        return UserDAO(self.admin_service)

    @property
    def group(self) -> GroupDAO:
        """DAO para gestión de grupos"""
        return GroupDAO(self.admin_service)

