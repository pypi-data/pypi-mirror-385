import os
import tai_keycloak.config as config
from .provider import DatabaseProvider  # noqa: F401


class EnvironmentVariables:
    """ 
    Utility class to manage Keycloak environment variables.
    """

    VARIABLES_TO_SET = [
        'KC_DB', 'KC_DB_URL', 'KC_DB_USERNAME', 'KC_DB_PASSWORD', 
        'KC_DB_URL_DATABASE', 'KEYCLOAK_ADMIN', 'KEYCLOAK_ADMIN_PASSWORD',
        'KC_HTTP_ENABLED', 'KC_HOSTNAME_STRICT', 'KC_PROXY', 'KC_HTTP_PORT'
    ]

    db_provider = DatabaseProvider.from_environment()

    def set(self) -> None:
        """
        Set the necessary environment variables for Keycloak based on the
        current configuration and database provider.
        """
        # Set database-related environment variables
        if self.db_provider and self.db_provider.drivername in self.db_provider.ALLOWED_DRIVERS:
            os.environ['KC_DB'] = self.db_provider.type
            os.environ['KC_DB_URL'] = self.db_provider.url
            if self.db_provider.username:
                os.environ['KC_DB_USERNAME'] = self.db_provider.username
            if self.db_provider.password:
                os.environ['KC_DB_PASSWORD'] = self.db_provider.password
            os.environ['KC_DB_URL_DATABASE'] = self.db_provider.database
        else:
            # Default to H2 for unsupported databases
            os.environ['KC_DB'] = 'h2'
            os.environ['KC_DB_URL_DATABASE'] = 'keycloak'

        # Set admin user and password if not already set
        os.environ.setdefault('KEYCLOAK_ADMIN', config.KEYCLOAK_DEFAULT_ADMIN_USER)
        os.environ.setdefault('KEYCLOAK_ADMIN_PASSWORD', config.KEYCLOAK_DEFAULT_ADMIN_PASSWORD)

        # Set HTTP settings
        os.environ.setdefault('KC_HTTP_ENABLED', 'true')
        os.environ.setdefault('KC_HOSTNAME_STRICT', 'false')
        os.environ.setdefault('KC_PROXY', 'edge')

        # Set HTTP port based on protocol
        if os.environ.get('KC_HTTP_PORT') is None:
            if os.environ.get('KC_HTTPS_ENABLED', 'false').lower() == 'true':
                os.environ['KC_HTTP_PORT'] = str(config.KEYCLOAK_DEFAULT_HTTPS_PORT)
            else:
                os.environ['KC_HTTP_PORT'] = str(config.KEYCLOAK_DEFAULT_HTTP_PORT)
        
        # Set log level
        os.environ.setdefault('KC_LOG_LEVEL', config.KEYCLOAK_DEFAULT_LOGLEVEL)

    def default_variables(self) -> dict:
        """
        Returns a dictionary of the default environment variables
        that would be set for Keycloak.
        """
        return {var: os.getenv(var) for var in self.VARIABLES_TO_SET if os.getenv(var) is not None}