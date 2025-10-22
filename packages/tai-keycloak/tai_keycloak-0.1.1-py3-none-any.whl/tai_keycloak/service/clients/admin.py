"""
Servicio principal para interactuar con Keycloak (Administración)
"""
from typing import Dict, Optional, Any

from keycloak import KeycloakAdmin

from ..dtos import (
    KeycloakConfig, OperationResult, KeycloakSDKException
)

from ..daos import (
    UserDAO, GroupDAO, ClientDAO, RealmDAO,
    ClientRoleDAO, RealmRoleDAO
)


class KeycloakAdminClient:
    """
    Servicio principal para gestionar instancias de Keycloak (Administración).
    
    Proporciona una interfaz elegante y robusta para:
    - Gestión de realms
    - Gestión de usuarios
    - Gestión de grupos y roles
    - Gestión de clientes
    """

    REALM_NAME = 'main-realm'

    def __init__(self, config: Optional[KeycloakConfig] = None):
        self.config = config or KeycloakConfig()
        self._service: Optional[KeycloakAdmin] = None
        
    @property
    def service(self) -> KeycloakAdmin:
        """Instancia autenticada de KeycloakAdmin"""
        if not self._service:
            self._service = KeycloakAdmin(
                server_url=self.config.url,
                username=self.config.username,
                password=self.config.password,
                verify=self.config.verify_ssl
            )
            self._service.connection.get_token()
            self._service.change_current_realm(self.REALM_NAME)
        return self._service
    
    @property
    def user(self) -> UserDAO:
        """DAO para gestión de usuarios"""
        return UserDAO(self.service)
    
    @property
    def group(self) -> GroupDAO:
        """DAO para gestión de grupos"""
        return GroupDAO(self.service)
    
    @property
    def client(self) -> ClientDAO:
        """DAO para gestión de clientes"""
        return ClientDAO(self.service)

    @property
    def realm(self) -> RealmDAO:
        """DAO para gestión de realms"""
        return RealmDAO(self.service)

    @property
    def api_role(self) -> ClientRoleDAO:
        """DAO para gestión de roles de cliente"""
        return ClientRoleDAO(self.service, 'api')
    
    @property
    def app_role(self) -> ClientRoleDAO:
        """DAO para gestión de roles de cliente"""
        return ClientRoleDAO(self.service, 'app')

    @property
    def realm_role(self) -> RealmRoleDAO:
        """DAO para gestión de roles de realm"""
        return RealmRoleDAO(self.service)

    # === INFORMACIÓN DEL SERVIDOR ===
    
    def get_server_info(self, with_logs: bool=True) -> OperationResult[Dict[str, Any]]:
        """Obtiene información detallada del servidor Keycloak (admin)"""
        try:
            server_info = self.service.get_server_info()
            return OperationResult(
                success=True,
                message="Información del servidor obtenida",
                data=server_info,
                with_logs=with_logs
            )
        except Exception as e:
            return KeycloakSDKException(e).handle("KeycloakAdminClient.get_server_info", "Error obteniendo información del servidor", with_logs=with_logs)

