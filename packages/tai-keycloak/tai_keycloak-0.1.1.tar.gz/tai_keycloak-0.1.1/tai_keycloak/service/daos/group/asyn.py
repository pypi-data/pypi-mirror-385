from typing import List
from keycloak import KeycloakAdmin
from ...dtos import Group, OperationResult, KeycloakSDKException


class AsyncGroupDAO:
    """DAO para operaciones CRUD de grupos en Keycloak"""

    NAME = 'Group'

    def __init__(self, client: KeycloakAdmin):
        self.client = client

    async def create(self, group: Group) -> OperationResult[Group]:
        """Crea un nuevo grupo"""
        try:
            group_data = group.model_dump(exclude_none=True)
            group_data.pop('id', None)
            group_data.pop('sub_groups', None)  # Los subgrupos se manejan por separado
            group.id = await self.client.a_create_group(group_data, skip_exists=False)

            return OperationResult(
                success=True,
                message=f"Grupo '{group.name}' creado exitosamente",
                data=group
            )
        except Exception as e:
            return KeycloakSDKException(e).handle(f"{self.NAME}.create_group", f"grupo '{group.name}'")

    async def get(self, group_name: str) -> OperationResult[Group]:
        """Obtiene información de un grupo"""
        try:
            result = await self.client.a_get_groups({"search": group_name})
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
            group_data = await self.client.a_get_group(group_id)
            group = Group(**group_data)

            return OperationResult(
                success=True,
                message=f"Grupo '{group_name}' encontrado",
                data=group
            )
        except Exception as e:
            return KeycloakSDKException(e).handle(f"{self.NAME}.get", f"grupo: '{group_name}'")

    async def list(self) -> OperationResult[List[Group]]:
        """Lista todos los grupos"""
        try:
            groups = [Group(**group_data) for group_data in await self.client.a_get_groups()]
            return OperationResult(
                success=True,
                message=f"Encontrados {len(groups)} grupos",
                data=groups
            )
        except Exception as e:
            return KeycloakSDKException(e).handle(f"{self.NAME}.list")

    async def delete(self, group_name: str) -> OperationResult[None]:
        """Elimina un grupo"""
        try:
            result = await self.client.a_get_groups({"search": group_name})
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
            await self.client.a_delete_group(group_id)
            return OperationResult(
                success=True,
                message=f"Grupo '{group_name}' eliminado exitosamente"
            )
        except Exception as e:
            return KeycloakSDKException(e).handle(f"{self.NAME}.delete", f"grupo '{group_name}'")

    async def add_user(self, username: str, group_name: str) -> OperationResult[None]:
        """Añade un usuario a un grupo"""
        try:
            result = await self.client.a_get_groups({"search": group_name})
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
            user_id = await self.client.a_get_user_id(username)
            await self.client.a_group_user_add(user_id, group_id)
            return OperationResult(
                success=True,
                message=f"Usuario '{username}' añadido al grupo '{group_name}' exitosamente"
            )
        except Exception as e:
            return KeycloakSDKException(e).handle(f"{self.NAME}.add_user", f"usuario '{username}' y grupo '{group_name}'")
    
    async def remove_user(self, username: str, group_name: str) -> OperationResult[None]:
        """Remueve un usuario de un grupo"""
        try:
            result = await self.client.a_get_groups({"search": group_name})
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
            user_id = await self.client.a_get_user_id(username)
            await self.client.a_group_user_remove(user_id, group_id)
            return OperationResult(
                success=True,
                message="Usuario eliminado del grupo exitosamente"
            )
        except Exception as e:
            return KeycloakSDKException(e).handle(f"{self.NAME}.remove_user", f"usuario '{username}' y grupo '{group_name}'")