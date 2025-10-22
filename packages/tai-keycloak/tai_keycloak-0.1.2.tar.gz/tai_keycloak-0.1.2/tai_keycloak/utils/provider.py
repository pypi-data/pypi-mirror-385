"""
Database connection provider for Keycloak.
Simplified version that parses MAIN_DATABASE_URL and forces database name to 'keycloak'.
Does not depend on SQLAlchemy.
"""
import os
import re
from typing import Optional, Dict
from urllib.parse import urlparse, parse_qs, unquote


class DatabaseProvider:
    """
    Database connection provider specifically for Keycloak.
    
    Parses MAIN_DATABASE_URL and automatically sets database name to 'keycloak'.
    Does not depend on SQLAlchemy.
    """

    ALLOWED_DRIVERS = ['postgresql', 'mysql', 'sqlite']
    
    def __init__(self):
        self.drivername: Optional[str] = None
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self.host: Optional[str] = None
        self.port: Optional[int] = None
        self.database: str = "keycloak"  # Always 'keycloak' for Keycloak instances
        self.query_params: Dict[str, str] = {}
    
    def __repr__(self) -> str:
        """Return a string representation of the DatabaseProvider instance."""
        return f"DatabaseProvider(DRIVER={self.drivername}, HOST={self.host}:{self.port}, DB={self.database})"

    @classmethod
    def from_environment(cls, var_name: str = 'MAIN_DATABASE_URL') -> Optional['DatabaseProvider']:
        """
        Create a DatabaseProvider from an environment variable.
        
        Args:
            var_name: Environment variable name
            
        Returns:
            Configured DatabaseProvider instance
        """
        connection_string = os.getenv(var_name)
        if connection_string is None:
            return None
        
        instance = cls.from_connection_string(connection_string)
        return instance
    
    @classmethod
    def from_connection_string(cls, connection_string: str) -> 'DatabaseProvider':
        """
        Create a DatabaseProvider from a connection string.
        
        The database name from the connection string will be ignored and 
        replaced with 'keycloak'.
        
        Args:
            connection_string: Connection string (e.g., 'postgresql://user:pass@host:port/anydb')
            
        Returns:
            DatabaseProvider instance configured for Keycloak
            
        Raises:
            ValueError: If connection string format is invalid
        """
        try:
            instance = cls()
            
            # Clean and validate connection string
            connection_string = connection_string.strip()
            
            if '://' not in connection_string:
                raise ValueError("Connection string must have format: driver://user:pass@host:port/db")
            
            # Parse using urlparse
            parsed = urlparse(connection_string)
            
            # Validate essential components
            if not parsed.scheme:
                raise ValueError("Driver not specified in connection string")
            
            if not parsed.hostname:
                raise ValueError("Host not specified in connection string")
            
            # Extract components
            instance.drivername = parsed.scheme
            instance.username = parsed.username
            instance.password = parsed.password
            instance.host = parsed.hostname
            instance.port = parsed.port
            
            # Set default ports if not specified
            if instance.port is None:
                default_ports = {
                    'postgresql': 5432,
                    'mysql': 3306,
                    'sqlite': None,
                    'mssql': 1433,
                    'oracle': 1521
                }
                instance.port = default_ports.get(instance.drivername, None)
            
            # Force database to 'keycloak' (ignore original database name)
            instance.database = "keycloak"
            
            # Parse query parameters
            if parsed.query:
                try:
                    query_params = parse_qs(parsed.query)
                    # Convert single-item lists to strings
                    instance.query_params = {
                        k: v[0] if len(v) == 1 else v 
                        for k, v in query_params.items()
                    }
                except Exception:
                    instance.query_params = {}

            return instance
            
        except Exception:
            # Try alternative parsing method
            return cls._parse_connection_string_manually(connection_string)

    @classmethod
    def _parse_connection_string_manually(cls, connection_string: str) -> 'DatabaseProvider':
        """
        Alternative parsing method that handles special characters manually.
        
        For unsupported database types, defaults to H2 configuration.
        
        Args:
            connection_string: Connection string that may contain special characters
            
        Returns:
            Configured DatabaseProvider (with H2 fallback for unsupported drivers)
        """
        instance = cls()
        
        # Extract driver from connection string
        try:
            driver = connection_string.split('://')[0]
            instance.drivername = driver
        except:
            instance.drivername = 'h2'
        
        # For unsupported drivers, just return H2 configuration
        if instance.drivername not in cls.ALLOWED_DRIVERS:
            instance.drivername = 'h2'
            instance.host = 'localhost'
            instance.port = None
            instance.username = None
            instance.password = None
            instance.database = "keycloak"
            return instance
        
        # Try to parse supported databases with regex
        pattern = r'^([^:]+)://(?:([^:@]+)(?::([^@]*))?@)?([^:/]+)(?::(\d+))?(?:/(.*))?$'
        match = re.match(pattern, connection_string.strip())
        
        if match:
            driver, username, password, host, port_str, database_and_query = match.groups()
            
            instance.drivername = driver
            instance.username = unquote(username) if username else None
            instance.password = unquote(password) if password else None
            instance.host = unquote(host) if host else None
            
            # Parse port
            if port_str:
                try:
                    instance.port = int(port_str)
                except ValueError:
                    instance.port = 5432 if driver == 'postgresql' else 3306
            else:
                instance.port = 5432 if driver == 'postgresql' else 3306
            
            # Force database to 'keycloak'
            instance.database = "keycloak"
            
            # Parse query parameters if they exist
            if database_and_query and '?' in database_and_query:
                _, query_string = database_and_query.split('?', 1)
                for param in query_string.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        instance.query_params[unquote(key)] = unquote(value)
        else:
            # Fallback to H2 if parsing fails completely
            instance.drivername = 'h2'
            instance.host = 'localhost'
            instance.port = None
            instance.username = None
            instance.password = None
            instance.database = "keycloak"
        
        return instance

    @classmethod
    def validate_connection_string(cls, connection_string: str) -> bool:
        """
        Validate if a connection string has the correct format.

        Args:
            connection_string: Connection string to validate

        Returns:
            True if format is valid, False otherwise
        """
        try:
            cls.from_connection_string(connection_string)
            return True
        except ValueError:
            return False
    
    @property
    def url(self) -> str:
        """
        Generate JDBC URL specifically for Keycloak configuration.
        
        Returns:
            JDBC URL string for Keycloak
        """
        base_url = f"jdbc:{self.drivername}://{self.host}"
        if self.port:
            base_url += f":{self.port}"
        base_url += f"/{self.database}"
        
        # Add query parameters if any
        if self.query_params:
            query_string = "&".join([f"{k}={v}" for k, v in self.query_params.items()])
            base_url += f"?{query_string}"

        return base_url
    
    @property
    def type(self) -> str:
        """
        Get the database type based on the drivername.
        
        Returns:
            Database type string
        """
        mapper = {
            'postgresql': 'postgres',
            'mysql': 'mysql',
            'sqlite': 'sqlite'
        }
        if self.drivername in mapper:
            return mapper[self.drivername]
        return 'h2'
