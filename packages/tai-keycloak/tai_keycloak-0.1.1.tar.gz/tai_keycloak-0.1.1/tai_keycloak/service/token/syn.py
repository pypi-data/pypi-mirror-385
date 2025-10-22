from jwcrypto import jwt
from jwcrypto.jwk import JWK
from jwcrypto.common import json_decode
from typing import Dict, Any, Optional
from keycloak import KeycloakOpenID
from ..dtos import Token, OperationResult, KeycloakSDKException


class TokenDAO:
    """Interfaz base para DAOs de tokens"""

    NAME = 'Token'

    def __init__(self, client: KeycloakOpenID):
        self.client = client

    @staticmethod
    def decode(token: str, key: Optional[JWK] = None) -> OperationResult[Dict[str, Any]]:
        """
        Decodifica y opcionalmente valida un token JWT.
        """
        try:

            full_jwt = jwt.JWT(jwt=token)
            full_jwt.leeway = 60
            
            if key is not None:
                full_jwt.validate(key)

            token = json_decode(full_jwt.claims)

            return OperationResult(
                success=True,
                message="Token decodificado exitosamente",
                data=token
            )
        except Exception as e:
            return KeycloakSDKException(e).handle(f"Token.decode", "decodificación de token")

    def request(self, username: Optional[str] = None, password: Optional[str] = None) -> OperationResult[Token]:
        """Obtiene un token de acceso para un usuario"""
        try:
            if username is None or password is None:
                tokens_data = self.client.token(grant_type='client_credentials')
                msg = "Tokens de servicio obtenido exitosamente"
            else:
                tokens_data = self.client.token(username, password)
                msg = f"Tokens obtenido exitosamente para el usuario '{username}'"

            token = Token(**tokens_data)
            return OperationResult(
                success=True,
                message=msg,
                data=token
            )
        except Exception as e:
            return KeycloakSDKException(e).handle(f"{self.NAME}.get", f"token para usuario '{username}'")

