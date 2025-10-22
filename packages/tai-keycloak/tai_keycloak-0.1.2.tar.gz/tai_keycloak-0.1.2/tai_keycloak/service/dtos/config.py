"""
Modelos Pydantic para representar entidades de Keycloak de forma tipada y validada.
"""
import re
import os
from typing import Optional
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

import tai_keycloak.config as config

class KeycloakConfig(BaseSettings):
    """
    Configuración de conexión administrativa a Keycloak.
    
    Soporta configuración mediante MAIN_KEYCLOAK_URL con los siguientes formatos:
    - user:password@host:port (completo)
    - user@host:port (password por defecto)
    - host:port (user y password por defecto)
    - host (user, password y puerto inteligente)
    
    Detección inteligente de puerto (sin puerto explícito):
    - localhost/127.0.0.1 → puerto 8090, http (desarrollo local)
    - *.azurewebsites.net → puerto 443, https (Azure Web Apps con SSL)
    - otros hosts → puerto 443, https (producción)
    
    Ejemplos:
    - MAIN_KEYCLOAK_URL=admin:secret@keycloak.company.com:8080
    - MAIN_KEYCLOAK_URL=admin@keycloak.company.com:8080
    - MAIN_KEYCLOAK_URL=keycloak.company.com  # → https://keycloak.company.com
    - MAIN_KEYCLOAK_URL=localhost  # → http://localhost:8090
    - MAIN_KEYCLOAK_URL=myapp.azurewebsites.net  # → https://myapp.azurewebsites.net
    """
    protocol: str = config.KEYCLOAK_DEFAULT_PROTOCOL
    hostname: str = config.KEYCLOAK_DEFAULT_HOSTNAME
    http_port: int = config.KEYCLOAK_DEFAULT_HTTP_PORT
    https_port: int = config.KEYCLOAK_DEFAULT_HTTPS_PORT
    username: str = config.KEYCLOAK_DEFAULT_ADMIN_USER
    password: str = config.KEYCLOAK_DEFAULT_ADMIN_PASSWORD
    loglevel: str = config.KEYCLOAK_DEFAULT_LOGLEVEL
    api_client_secret: Optional[str] = None
    verify_ssl: bool = True

    @model_validator(mode='before')
    @classmethod
    def parse_main_keycloak_url(cls, values):
        """Parse MAIN_KEYCLOAK_URL si está presente"""
        if isinstance(values, dict):
            main_url = os.getenv('MAIN_KEYCLOAK_URL')
            if main_url:
                parsed = cls._parse_keycloak_url(main_url)
                # Solo sobrescribir valores que no hayan sido explícitamente configurados
                for key, value in parsed.items():
                    if key not in values:
                        values[key] = value
        return values

    @property
    def url(self) -> str:
        """Construye la URL completa del servidor Keycloak"""
        if (self.protocol == 'http' and self.http_port == 80) or (self.protocol == 'https' and self.https_port == 443):
            # Omitir puerto estándar para URLs más limpias
            return f"{self.protocol}://{self.hostname}"
        else:
            port = self.http_port if self.protocol == 'http' else self.https_port
            return f"{self.protocol}://{self.hostname}:{port}"

    @staticmethod
    def _parse_keycloak_url(url_string: str) -> dict:
        """
        Parse diferentes formatos de MAIN_KEYCLOAK_URL
        y devuelve un dict con los componentes extraídos.
        """
        
        result = {}
        
        # Regex para parsear diferentes formatos
        # Patrón: [user[:password]@]host[:port]
        pattern = r'^(?:(?P<protocol>https?)://)?(?:(?P<user>[^:@]+)(?::(?P<password>[^@]+))?@)?(?P<host>[^:\/]+)(?::(?P<port>\d+))?$'
        
        match = re.match(pattern, url_string.strip())
        
        if not match:
            raise ValueError(f"Formato inválido para MAIN_KEYCLOAK_URL: {url_string}")
        
        groups = match.groupdict()
        
        # Extraer componentes
        host = groups.get('host')
        protocol = groups.get('protocol') or config.KEYCLOAK_DEFAULT_PROTOCOL
        username = groups.get('user') or config.KEYCLOAK_DEFAULT_ADMIN_USER
        password = groups.get('password') or config.KEYCLOAK_DEFAULT_ADMIN_PASSWORD
        port = groups.get('port') or config.KEYCLOAK_DEFAULT_HTTP_PORT if protocol == 'http' else config.KEYCLOAK_DEFAULT_HTTPS_PORT
        
        if not host:
            raise ValueError("Host es requerido en MAIN_KEYCLOAK_URL")
        
        result.update({
            'username': username,
            'password': password,
            'hostname': host,
            'protocol': protocol,
            'http_port': int(port) if protocol == 'http' else config.KEYCLOAK_DEFAULT_HTTP_PORT,
            'https_port': int(port) if protocol == 'https' else config.KEYCLOAK_DEFAULT_HTTPS_PORT,
        })
        
        return result

    model_config = SettingsConfigDict(
        env_prefix="KEYCLOAK_",        # variables individuales empiezan por KEYCLOAK_
        case_sensitive=False,       # ignora mayúsculas/minúsculas
    )
