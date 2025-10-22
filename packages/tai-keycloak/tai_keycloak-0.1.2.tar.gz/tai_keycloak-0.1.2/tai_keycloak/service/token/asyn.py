from jwcrypto import jwt
from jwcrypto.jwk import JWK
from jwcrypto.common import json_decode
from typing import Dict, Any, Optional
from keycloak import KeycloakOpenID
from ..dtos import Token, OperationResult, KeycloakSDKException


class AsyncTokenDAO:
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

    async def request(self, username: str, password: str) -> OperationResult[Token]:
        """Obtiene un token de acceso para un usuario"""
        try:
            tokens_data = await self.client.a_token(username, password)
            token = Token(**tokens_data)
            return OperationResult(
                success=True,
                message=f"Tokens obtenido exitosamente para el usuario '{username}'",
                data=token
            )
        except Exception as e:
            return KeycloakSDKException(e).handle(f"{self.NAME}.get", f"token para usuario '{username}'")
