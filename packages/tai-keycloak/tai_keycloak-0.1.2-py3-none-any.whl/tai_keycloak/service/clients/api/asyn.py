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
    AsyncUserDAO,
    AsyncGroupDAO
)

from ...token import AsyncTokenDAO


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

    async def get_public_key(self) -> JWK:
        """Obtiene la clave pública del realm para validar tokens"""
        public_key_pem = await self.openid_service.a_public_key()
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
    def token(self) -> AsyncTokenDAO:
        """DAO para gestión de tokens"""
        return AsyncTokenDAO(self.openid_service)

    @property
    def user(self) -> AsyncUserDAO:
        """DAO para gestión de usuarios"""
        return AsyncUserDAO(self.admin_service)

    @property
    def group(self) -> AsyncGroupDAO:
        """DAO para gestión de grupos"""
        return AsyncGroupDAO(self.admin_service)

