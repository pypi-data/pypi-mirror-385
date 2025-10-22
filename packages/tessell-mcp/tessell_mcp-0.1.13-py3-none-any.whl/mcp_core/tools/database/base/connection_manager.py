"""
Connection manager for database connections.
Handles connection pooling, environment variable resolution, and config file loading.
"""

import os
import json
import logging
from typing import Dict, Optional, Any
from urllib.parse import urlparse, parse_qs
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages database connections and connection strings."""
    
    def __init__(self):
        self._connections = {}
        self._config_cache = {}
        self._lock = threading.Lock()
        
    def get_connection_string(self, connection_name: str, database: Optional[str] = None) -> Optional[str]:
        """
        Get connection string for a given connection name.
        
        Priority order:
        1. Environment variable CONNSTR_{connection_name}
        2. Config file specified by DATABASE_CONFIG_PATH
        3. None if not found
        
        If 'database' is provided, the returned connection string will point to that database (if supported by the engine).
        
        Args:
            connection_name: Name of the connection
            database: Optional database name to use in the connection string
        Returns:
            Connection string or None if not found
        """
        # Try environment variable first
        env_var_name = f"CONNSTR_{connection_name.upper()}"
        connection_string = os.getenv(env_var_name)
        
        if connection_string:
            logger.debug(f"Found connection string in environment variable: {env_var_name}")
            if database:
                # Replace database in connection string if possible
                connection_string = self._replace_database_in_conn_str(connection_string, database)
            return connection_string
        
        # Try config file
        config_path = os.getenv("DATABASE_CONFIG_PATH")
        if config_path:
            connection_string = self._get_connection_from_config(connection_name, config_path)
            if connection_string:
                logger.debug(f"Found connection string in config file: {config_path}")
                if database:
                    connection_string = self._replace_database_in_conn_str(connection_string, database)
                return connection_string
        
        logger.warning(f"Connection string not found for: {connection_name}")
        return None
    
    def _get_connection_from_config(self, connection_name: str, config_path: str) -> Optional[str]:
        """
        Get connection string from JSON config file.
        
        Args:
            connection_name: Name of the connection
            config_path: Path to the config file
            
        Returns:
            Connection string or None if not found
        """
        try:
            if config_path not in self._config_cache:
                with open(config_path, 'r') as f:
                    self._config_cache[config_path] = json.load(f)
            
            config = self._config_cache[config_path]
            if connection_name in config:
                return config[connection_name].get("connection_string")
                
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error reading config file {config_path}: {e}")
        
        return None
    
    def parse_connection_string(self, connection_string: str) -> Dict[str, Any]:
        """
        Parse a connection string into its components.
        
        Args:
            connection_string: Database connection string
            
        Returns:
            Dictionary containing parsed connection components
        """
        try:
            parsed = urlparse(connection_string)
            query_params = parse_qs(parsed.query)
            
            # Extract username and password
            username = password = None
            if parsed.username:
                username = parsed.username
            if parsed.password:
                password = parsed.password
            
            # Extract database name
            database = parsed.path.lstrip('/') if parsed.path else None
            
            # Parse query parameters
            params = {}
            for key, values in query_params.items():
                params[key] = values[0] if values else None
            
            return {
                "scheme": parsed.scheme,
                "host": parsed.hostname,
                "port": parsed.port,
                "username": username,
                "password": password,
                "database": database,
                "params": params
            }
            
        except Exception as e:
            logger.error(f"Error parsing connection string: {e}")
            return {}
    
    def validate_connection_string(self, connection_string: str) -> bool:
        """
        Validate a connection string format.
        
        Args:
            connection_string: Connection string to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            parsed = self.parse_connection_string(connection_string)
            required_fields = ["scheme", "host"]
            
            # Check required fields
            for field in required_fields:
                if not parsed.get(field):
                    logger.error(f"Missing required field in connection string: {field}")
                    return False
            
            # Validate scheme
            valid_schemes = ["postgresql", "postgres", "mysql", "oracle", "mssql"]
            if parsed["scheme"] not in valid_schemes:
                logger.error(f"Invalid database scheme: {parsed['scheme']}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Connection string validation error: {e}")
            return False
    
    def get_connection_info(self, connection_name: str) -> Dict[str, Any]:
        """
        Get detailed connection information.
        
        Args:
            connection_name: Name of the connection
            
        Returns:
            Dictionary containing connection information
        """
        connection_string = self.get_connection_string(connection_name)
        if not connection_string:
            return {"error": f"Connection not found: {connection_name}"}
        
        parsed = self.parse_connection_string(connection_string)
        return {
            "connection_name": connection_name,
            "connection_string": self._mask_connection_string(connection_string),
            "parsed": parsed,
            "is_valid": self.validate_connection_string(connection_string)
        }
    
    def _mask_connection_string(self, connection_string: str) -> str:
        """
        Mask sensitive information in connection string.
        
        Args:
            connection_string: Original connection string
            
        Returns:
            Masked connection string
        """
        try:
            parsed = urlparse(connection_string)
            if parsed.password:
                # Replace password with asterisks
                netloc = parsed.netloc.replace(f":{parsed.password}@", ":***@")
                return connection_string.replace(parsed.netloc, netloc)
        except Exception:
            pass
        
        return connection_string
    
    def list_available_connections(self) -> Dict[str, Any]:
        """
        List all available connections from environment and config.
        
        Returns:
            Dictionary containing all available connections
        """
        connections = {}
        
        # Get connections from environment variables
        for key, value in os.environ.items():
            if key.startswith("CONNSTR_"):
                connection_name = key[8:].lower()  # Remove CONNSTR_ prefix
                connections[connection_name] = {
                    "source": "environment",
                    "connection_string": self._mask_connection_string(value)
                }
        
        # Get connections from config file
        config_path = os.getenv("DATABASE_CONFIG_PATH")
        if config_path:
            try:
                if config_path not in self._config_cache:
                    with open(config_path, 'r') as f:
                        self._config_cache[config_path] = json.load(f)
                
                config = self._config_cache[config_path]
                for connection_name, config_data in config.items():
                    if connection_name not in connections:
                        connections[connection_name] = {
                            "source": "config_file",
                            "connection_string": self._mask_connection_string(
                                config_data.get("connection_string", "")
                            ),
                            "description": config_data.get("description", "")
                        }
                        
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logger.error(f"Error reading config file {config_path}: {e}")
        
        return connections

    def _replace_database_in_conn_str(self, connection_string: str, database: str) -> str:
        """
        Replace the database name in a connection string with the provided database.
        Only supports PostgreSQL and Oracle connection strings for now.
        """
        # PostgreSQL: postgresql://user:pass@host:port/dbname?params
        if connection_string.startswith("postgresql://"):
            import re
            return re.sub(r"(postgresql://[^/]+/)[^?]+", r"\1" + database, connection_string)
        # Oracle: oracle+...://user:pass@host:port/dbname
        if connection_string.startswith("oracle"):
            import re
            return re.sub(r"(oracle[\w+]*://[^/]+/)[^?]+", r"\1" + database, connection_string)
        # Otherwise, return as is
        return connection_string


# Global connection manager instance
connection_manager = ConnectionManager() 