from typing import List
from keycloak import KeycloakAdmin
from ..dtos import Client, OperationResult, KeycloakSDKException


class ClientDAO:
    """DAO para operaciones CRUD de clientes en Keycloak"""

    NAME = 'Client'

    def __init__(self, client: KeycloakAdmin):
        self.client = client

    def create(self, client: Client) -> OperationResult[Client]:
        """Crea un nuevo cliente"""
        try:
            client_data = client.model_dump(exclude_none=True)
            client_data.pop('id', None)
            client.id = self.client.create_client(client_data)
            
            return OperationResult(
                success=True,
                message=f"Cliente '{client.id}' creado exitosamente",
                data=client
            )
        except Exception as e:
            return KeycloakSDKException(e).handle(f"{self.NAME}.create", f"client '{client.id}'")

    def get(self, client_id: str) -> OperationResult[Client]:
        """Obtiene información de un cliente"""
        try:
            client_data = self.client.get_client(client_id)
            client = Client(**client_data)
            return OperationResult(
                success=True,
                message=f"Cliente '{client_id}' encontrado",
                data=client
            )
        except Exception as e:
            return KeycloakSDKException(e).handle(f"{self.NAME}.get", f"client: '{client_id}'")

    def list(self) -> OperationResult[List[Client]]:
        """Lista todos los clientes"""
        try:
            clients = []
            for client in self.client.get_clients():
                clients.append(Client(**client))

            return OperationResult(
                success=True,
                message=f"Encontrados {len(clients)} clientes",
                data=clients
            )
        except Exception as e:
            return KeycloakSDKException(e).handle(f"{self.NAME}.list")

    def delete(self, client_id: str) -> OperationResult[None]:
        """Elimina un cliente"""
        try:
            self.client.delete_client(client_id)
            return OperationResult(
                success=True,
                message=f"Cliente '{client_id}' eliminado exitosamente"
            )
        except Exception as e:
            return KeycloakSDKException(e).handle(f"{self.NAME}.delete", f"client '{client_id}'")
    
    def get_secret(self, client_id: str) -> OperationResult[str]:
        """Obtiene el secreto de un cliente confidencial"""
        try:
            client = self.get(client_id)  # Verifica que el cliente exista
            if client.data.publicClient:
                return OperationResult(
                    success=False,
                    message=f"El cliente '{client_id}' es público y no tiene un secreto",
                    data=None
                )
            secret_data = self.client.get_client_secrets(client_id)
            secret = secret_data.get('value')
            return OperationResult(
                success=True,
                message=f"Secreto del cliente '{client_id}' obtenido exitosamente",
                data=secret
            )
        except Exception as e:
            return KeycloakSDKException(e).handle(f"{self.NAME}.get_secret", f"client '{client_id}'")
    
    def regenerate_secret(self, client_id: str) -> OperationResult[str]:
        """Regenera el secreto de un cliente confidencial"""
        try:
            client = self.get(client_id)  # Verifica que el cliente exista
            if client.data.publicClient:
                return OperationResult(
                    success=False,
                    message=f"El cliente '{client_id}' es público y no tiene un secreto",
                    data=None
                )
            secret = self.client.generate_client_secrets(client_id)
            return OperationResult(
                success=True,
                message=f"Secreto del cliente '{client_id}' regenerado exitosamente",
                data=secret
            )
        except Exception as e:
            return KeycloakSDKException(e).handle(f"{self.NAME}.regenerate_secret", f"client '{client_id}'")