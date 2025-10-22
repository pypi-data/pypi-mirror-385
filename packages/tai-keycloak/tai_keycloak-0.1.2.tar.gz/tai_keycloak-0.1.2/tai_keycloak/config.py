KEYCLOAK_DEFAULT_PROTOCOL = 'http'
KEYCLOAK_DEFAULT_HOSTNAME = 'localhost'
KEYCLOAK_DEFAULT_HTTP_PORT = 8090  # Puerto para desarrollo local (evita conflicto con FastAPI)
KEYCLOAK_DEFAULT_HTTPS_PORT = 8443  # Puerto HTTPS para desarrollo local  
KEYCLOAK_DEFAULT_ADMIN_USER = 'admin'
KEYCLOAK_DEFAULT_ADMIN_PASSWORD = 'admin'
KEYCLOAK_DEFAULT_LOGLEVEL = 'INFO'

# Configuración específica para contenedores
KEYCLOAK_CONTAINER_HTTP_PORT = 80   # Puerto para Azure Web Apps
KEYCLOAK_CONTAINER_HTTPS_PORT = 443  # Puerto HTTPS para producción

OPERATION_LOGS = True