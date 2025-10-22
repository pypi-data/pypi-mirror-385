from __future__ import annotations
import json
from typing import Dict, Optional, TypeVar, Generic
from pydantic import BaseModel
from keycloak.exceptions import KeycloakError
from tai_alphi import Alphi

import tai_keycloak.config as config

logger = Alphi.get_logger_by_name("tai-keycloak")

T = TypeVar("T")

class OperationResult(BaseModel, Generic[T]):
    """Resultado de una operación en Keycloak"""
    success: bool
    message: str
    data: Optional[T] = None
    error: Optional[KeycloakSDKException] = None
    with_logs: bool = config.OPERATION_LOGS

    model_config = {
        "arbitrary_types_allowed": True,
        "fields": {
            "with_logs": {"exclude": True}
        }
    }

    def model_post_init(self, context):
        if self.with_logs:
            if self.success:
                logger.info(f'[keycloak-SDK] {self.message}')
            else:
                logger.error(f'[keycloak-SDK] {self.message}')
                if self.error:
                    logger.error(f'[keycloak-SERVER] DETAILS: {self.error.message}')
                    if self.error.description:
                        logger.error(f'[keycloak-SERVER] DESCRIPTION: {self.error.description}')

class KeycloakSDKException(Exception):
    """Error personalizado para Keycloak que hereda de Exception"""

    def __init__(self, e: Exception | KeycloakError):
        self.e = e
        self._error_data = None
        # Inicializar la excepción padre con el mensaje principal
        super().__init__(self.message)
    
    def __repr__(self):
        return f'Error("{self.message}")'
    
    def __str__(self):
        return self.formated_error
    
    @property
    def error_data(self) -> Dict[str, str]:
        """Extrae datos del error"""
        if self._error_data is None:
            if isinstance(self.e, KeycloakError):
                error_json = self.e.error_message
                if isinstance(error_json, bytes):
                    error_json = error_json.decode("utf-8")
                error_data = json.loads(error_json)
            else:
                error_data = {"error": str(self.e), "error_description": ""}

            self._error_data = error_data

        return self._error_data

    @property
    def message(self) -> str:
        return self.error_data.get("error", self.error_data.get("errorMessage", str(self.e)))
    
    @property
    def description(self) -> str:
        return self.error_data.get("error_description", "")
    
    @property
    def code(self) -> Optional[int]:
        if isinstance(self.e, KeycloakError):
            return self.e.response_code
        return None
    
    @property
    def formated_error(self) -> str:
        desc = self.description
        if desc:
            return f"{self.message}: {desc}"
        return self.message
    
    def handle(self, function: str, entity: str = "", with_logs=True) -> OperationResult:
        """Maneja errores estándar de Keycloak"""

        if isinstance(self.e, KeycloakError):
            if self.code == 409:  # Conflict
                return OperationResult(
                    success=False,
                    message=f"{function} → El {entity} ya existe",
                    error=self,
                    with_logs=with_logs
                )
            elif self.code == 404:  # Not Found
                return OperationResult(
                    success=False,
                    message=f"{function} → El {entity} no fue encontrado",
                    error=self,
                    with_logs=with_logs
                )
            elif self.code == 401:  # Unauthorized
                return OperationResult(
                    success=False,
                    message=f"{function} → Sin autorización para realizar esta operación",
                    error=self,
                    with_logs=with_logs
                )
            elif self.code == 403:  # Forbidden
                return OperationResult(
                    success=False,
                    message=f"{function} → Sin permisos para realizar esta operación",
                    error=self,
                    with_logs=with_logs
                )
            else:
                return OperationResult(
                    success=False,
                    message=f"{function} → Error inesperado" + (f" para {entity}" if entity else ""),
                    error=self,
                    with_logs=with_logs
                )
        elif isinstance(self.e, Exception):
            return OperationResult(
                success=False,
                message=f"{function} → Error inesperado" + (f" para {entity}" if entity else ""),
                error=self,
                with_logs=with_logs
            )

    