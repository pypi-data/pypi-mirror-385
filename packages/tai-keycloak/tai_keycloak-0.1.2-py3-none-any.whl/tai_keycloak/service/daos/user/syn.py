from typing import List, Optional
from keycloak import KeycloakAdmin
from ...dtos import User, OperationResult, KeycloakSDKException


class UserDAO:
    """DAO para operaciones CRUD de usuarios en Keycloak"""

    NAME = 'User'

    def __init__(self, client: KeycloakAdmin):
        self.client = client

    def create(self, user: User, password: Optional[str] = None, temporary: bool = False) -> OperationResult[User]:
        """Crea un nuevo usuario"""
        try:
            user_data = user.model_dump(by_alias=True, exclude_none=True)
            
            # Remover campos que no se envían en la creación
            user_data.pop('id', None)
            
            user.id = self.client.create_user(user_data, exist_ok=False)

            # Establecer contraseña si se proporciona
            if password:
                self.client.set_user_password(user.id, password, temporary=temporary)

            return OperationResult(
                success=True,
                message=f"Usuario '{user.username}' creado exitosamente",
                data=user
            )

        except Exception as e:
            return KeycloakSDKException(e).handle(f"{self.NAME}.create", f"usuario '{user.username}'")

    def get(self, username: str) -> OperationResult[User]:
        """Obtiene un usuario por username"""
        try:
            user_id = self.client.get_user_id(username)
            user_data = self.client.get_user(user_id)
            user = User(**user_data)

            return OperationResult(
                success=True,
                message=f"Usuario '{username}' encontrado",
                data=user
            )

        except Exception as e:
            return KeycloakSDKException(e).handle(f"{self.NAME}.get", f"usuario '{username}'")

    def list(self) -> OperationResult[List[User]]:
        """Lista usuarios con filtros opcionales"""
        try:
            users = []
            for user_data in self.client.get_users():
                users.append(User(**user_data))

            return OperationResult(
                success=True,
                message=f"Encontrados {len(users)} usuarios",
                data=users
            )
        except Exception as e:
            return KeycloakSDKException(e).handle(f"{self.NAME}.list")
    
    def update(self, user: User) -> OperationResult[User]:
        """Actualiza un usuario"""
        try:
            user_id = self.client.get_user_id(user.username)
            self.client.update_user(user_id, user.model_dump(exclude_unset=True))
            user.id = user_id
            return OperationResult(
                success=True,
                message=f'Usuario "{user.username}" actualizado exitosamente',
                data=user
            )
        except Exception as e:
            return KeycloakSDKException(e).handle(f"{self.NAME}.update", f"usuario '{user.username}'")

    def delete(self, username: str) -> OperationResult[None]:
        """Elimina un usuario"""
        try:
            user_id = self.client.get_user_id(username)
            self.client.delete_user(user_id)
            return OperationResult(
                success=True,
                message=f'Usuario "{username}" eliminado exitosamente'
            )
        except Exception as e:
            return KeycloakSDKException(e).handle(f"{self.NAME}.delete", f"usuario '{username}'")

    def add_to_group(self, username: str, group_name: str) -> OperationResult[None]:
        """Agrega un usuario a un grupo"""
        try:
            user_id = self.client.get_user_id(username)
            result = self.client.get_groups({"search": group_name})
            if not result:
                return OperationResult(
                    success=False,
                    message=f"Grupo '{group_name}' no encontrado",
                    data=None
                )
            if len(result) > 1:
                return OperationResult(
                    success=False,
                    message=f"Se encontraron múltiples grupos con el nombre '{group_name}'",
                    data=None
                )
            group_id = result[0]['id']
            self.client.group_user_add(user_id, group_id)
            return OperationResult(
                success=True,
                message=f'Usuario "{username}" agregado al grupo "{group_name}" exitosamente'
            )
        except Exception as e:
            return KeycloakSDKException(e).handle(f"{self.NAME}.add_to_group", f"usuario '{username}' y grupo '{group_name}'")
    
    def remove_from_group(self, username: str, group_name: str) -> OperationResult[None]:
        """Remueve un usuario de un grupo"""
        try:
            user_id = self.client.get_user_id(username)
            result = self.client.get_groups({"search": group_name})
            if not result:
                return OperationResult(
                    success=False,
                    message=f"Grupo '{group_name}' no encontrado",
                    data=None
                )
            if len(result) > 1:
                return OperationResult(
                    success=False,
                    message=f"Se encontraron múltiples grupos con el nombre '{group_name}'",
                    data=None
                )
            group_id = result[0]['id']
            self.client.group_user_remove(user_id, group_id)
            return OperationResult(
                success=True,
                message=f'Usuario "{username}" eliminado del grupo "{group_name}" exitosamente'
            )
        except Exception as e:
            return KeycloakSDKException(e).handle(f"{self.NAME}.remove_from_group", f"usuario '{username}' y grupo '{group_name}'")
    
    def switch_groups(self, username: str, from_group: str, to_group: str) -> OperationResult[None]:
        """Mueve un usuario de un grupo a otro"""
        try:
            self.remove_from_group(username, from_group)
            self.add_to_group(username, to_group)

            return OperationResult(
                success=True,
                message=f'Usuario "{username}" movido del grupo "{from_group}" al grupo "{to_group}" exitosamente'
            )
        except Exception as e:
            return KeycloakSDKException(e).handle(f"{self.NAME}.switch_groups", f"usuario '{username}', desde grupo '{from_group}' a grupo '{to_group}'")
    
    # def add_attribute(self, username: str, key: str, value: str):
    #     try:

    #     except Exception as e:
    #         return KeycloakSDKException(e).handle(f"{self.NAME}.add_attribute", f"usuario '{username}', clave '{key}' value '{value}'")
