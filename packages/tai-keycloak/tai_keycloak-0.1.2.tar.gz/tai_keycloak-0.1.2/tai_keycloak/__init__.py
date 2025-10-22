"""tai-keycloak package"""

from .service import KeycloakClient, KeycloakConfig, User, Role, Group, Client, Realm

__all__ = [
    "KeycloakClient", "KeycloakConfig", "User", "Role", "Group", "Client", "Realm"
]

kc = KeycloakClient()