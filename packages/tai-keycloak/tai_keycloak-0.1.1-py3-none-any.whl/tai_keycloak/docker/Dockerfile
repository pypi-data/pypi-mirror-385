# Dockerfile para instancia de Keycloak preconfigurada con tai-keycloak
FROM quay.io/keycloak/keycloak:24.0.0

# Metadatos
LABEL maintainer="MateoSaezMata <msaez@triplealpha.in>"
LABEL description="Keycloak instance with tai-keycloak preconfigured environment"
LABEL version="0.1.0"

# Copiar realm preconfigurado
COPY main-realm.json /opt/keycloak/data/import/

# Crear directorio para logs y configurar script de entrada
USER root
RUN mkdir -p /opt/keycloak/logs && chown keycloak:keycloak /opt/keycloak/logs

# Copiar y configurar script de entrada (como root)
COPY start-keycloak.sh /opt/keycloak/bin/start-keycloak.sh
RUN chmod +x /opt/keycloak/bin/start-keycloak.sh && \
    chown keycloak:keycloak /opt/keycloak/bin/start-keycloak.sh

# Volver al usuario keycloak
USER keycloak

# Exponer puerto 80 para Azure Web Apps
EXPOSE 80

# Sobrescribir ENTRYPOINT y usar nuestro script
ENTRYPOINT []
CMD ["/opt/keycloak/bin/start-keycloak.sh"]

# Healthcheck adaptativo según el puerto configurado
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
    CMD curl -f http://localhost:${KC_HTTP_PORT:-80}/realms/master || exit 1