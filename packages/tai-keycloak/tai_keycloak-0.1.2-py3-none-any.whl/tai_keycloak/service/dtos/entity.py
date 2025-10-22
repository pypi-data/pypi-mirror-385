"""
Modelos Pydantic para representar entidades de Keycloak de forma tipada y validada.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class ClientProtocol(str, Enum):
    """Protocolo del cliente Keycloak"""
    OPENID_CONNECT = "openid-connect"
    SAML = "saml"


class AccessType(str, Enum):
    """Tipo de acceso del cliente"""
    PUBLIC = "public"
    CONFIDENTIAL = "confidential"
    BEARER_ONLY = "bearer-only"


class Role(BaseModel):
    """Modelo para roles de Keycloak"""
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    composite: bool = False
    clientRole: bool = False
    containerId: Optional[str] = None
    attributes: Optional[Dict[str, List[str]]] = None


class Group(BaseModel):
    """Modelo para grupos de Keycloak"""
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=255)
    path: Optional[str] = None
    attributes: Optional[Dict[str, List[str]]] = None
    realm_roles: Optional[List[str]] = None
    client_roles: Optional[Dict[str, List[str]]] = None
    sub_groups: Optional[List['Group']] = None


class User(BaseModel):
    """Modelo para usuarios de Keycloak"""
    id: Optional[str] = None
    username: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    firstName: Optional[str] = Field(None)
    lastName: Optional[str] = Field(None)
    enabled: bool = True
    emailVerified: bool = Field(True)
    attributes: Optional[Dict[str, List[str]]] = None
    groups: Optional[List[str]] = None
    realm_roles: Optional[List[str]] = None
    client_roles: Optional[Dict[str, List[str]]] = None
    credentials: Optional[List[Dict[str, Any]]] = None


class Client(BaseModel):
    """Modelo para clientes de Keycloak"""
    id: Optional[str] = None
    clientId: str = Field(..., serialization_alias='clientId')
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: bool = True
    alwaysDisplayInConsole: bool = Field(False)
    clientAuthenticatorType: str = Field('client-secret')
    redirectUris: List[str] = Field(default_factory=list, serialization_alias='redirectUris')
    webOrigins: List[str] = Field(default_factory=list)
    protocol: ClientProtocol = ClientProtocol.OPENID_CONNECT
    accessType: AccessType = Field(AccessType.PUBLIC, exclude=True)
    publicClient: bool = Field(True)
    bearerOnly: bool = Field(False)
    standardFlowEnabled: bool = Field(True)
    implicitFlowEnabled: bool = Field(False)
    directAccessGrantsEnabled: bool = Field(True)
    serviceAccountsEnabled: bool = Field(False)
    publicClient: bool = Field(True)
    attributes: Optional[Dict[str, Any]] = None

    def model_post_init(self, context):
        if self.accessType == AccessType.PUBLIC:
            self.publicClient = True
            self.bearerOnly = False
        elif self.accessType == AccessType.CONFIDENTIAL:
            self.publicClient = False
            self.bearerOnly = False
        elif self.accessType == AccessType.BEARER_ONLY:
            self.publicClient = False
            self.bearerOnly = True


class Realm(BaseModel):
    """Modelo para realm de Keycloak"""
    id: Optional[str] = None
    realm: str = Field(..., min_length=1, max_length=255)
    displayName: Optional[str] = Field(None)
    displayNameHtml: Optional[str] = Field(None)
    enabled: bool = True
    sslRequired: str = Field('external')
    registrationAllowed: bool = Field(False)
    registrationEmailAsUsername: bool = Field(False)
    rememberMe: bool = Field(False)
    verifyEmail: bool = Field(False)
    loginWithEmailAllowed: bool = Field(True)
    duplicateEmailsAllowed: bool = Field(False)
    resetPasswordAllowed: bool = Field(False)
    editUsernameAllowed: bool = Field(False)
    bruteForceProtected: bool = Field(False)
    passwordPolicy: Optional[str] = Field(None)
    attributes: Optional[Dict[str, Any]] = None
    users: Optional[List[User]] = None
    groups: Optional[List[Group]] = None
    roles: Optional[Dict[str, List[Role]]] = None
    clients: Optional[List[Client]] = None

# Permitir referencias circulares
Group.model_rebuild()