"""
Abstract base class for database engines.
Provides a unified interface for different database types.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DatabaseEngine(ABC):
    """Abstract base class for database engine implementations."""
    
    def __init__(self, connection_string: str, **kwargs):
        """
        Initialize the database engine.
        
        Args:
            connection_string: Database connection string
            **kwargs: Additional engine-specific parameters
        """
        self.connection_string = connection_string
        self.engine_params = kwargs
        self._connection_pool = None
        self._is_connected = False
        
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the database."""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Close connection to the database."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to the database."""
        pass
    
    @abstractmethod
    def execute_query(self, query: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute a query and return results.
        
        Args:
            query: SQL query to execute
            params: Query parameters for parameterized queries
            
        Returns:
            Dict containing query results and metadata
        """
        pass
    
    @abstractmethod
    def list_tables(self, database: str) -> List[Dict[str, Any]]:
        """
        List all tables in the specified database.
        
        Args:
            database: Database name
            
        Returns:
            List of table information dictionaries
        """
        pass
    
    @abstractmethod
    def describe_table(self, database: str, table: str) -> Dict[str, Any]:
        """
        Get detailed information about a table.
        
        Args:
            database: Database name
            table: Table name
            
        Returns:
            Dictionary containing table schema and metadata
        """
        pass
    
    @abstractmethod
    def get_sample_data(self, database: str, table: str, limit: int = 10) -> Dict[str, Any]:
        """
        Get sample data from a table.
        
        Args:
            database: Database name
            table: Table name
            limit: Maximum number of rows to return
            
        Returns:
            Dictionary containing sample data and metadata
        """
        pass
    
    @abstractmethod
    def analyze_query_performance(self, query: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze query performance and return execution plan.
        
        Args:
            query: SQL query to analyze
            params: Query parameters
            
        Returns:
            Dictionary containing performance analysis results
        """
        pass
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        Ensures proper connection handling and cleanup.
        """
        connection = None
        returned = False
        try:
            connection = self._get_connection_from_pool()
            yield connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if connection and not returned:
                try:
                    self._return_connection_to_pool(connection)
                    returned = True
                except Exception as pool_err:
                    logger.error(f"Error returning connection to pool: {pool_err}")
            raise
        finally:
            if connection and not returned:
                try:
                    self._return_connection_to_pool(connection)
                except Exception as pool_err:
                    logger.error(f"Error returning connection to pool: {pool_err}")
    
    @abstractmethod
    def _get_connection_from_pool(self):
        """Get a connection from the connection pool."""
        pass
    
    @abstractmethod
    def _return_connection_to_pool(self, connection):
        """Return a connection to the connection pool."""
        pass
    
    @abstractmethod
    def validate_connection_string(self) -> bool:
        """Validate the connection string format."""
        pass
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get information about the database engine."""
        return {
            "engine_type": self.__class__.__name__,
            "connection_string": self._mask_connection_string(),
            "is_connected": self.is_connected(),
            "engine_params": self.engine_params
        }
    
    def _mask_connection_string(self) -> str:
        """Return connection string with sensitive information masked."""
        # Basic masking - implementations can override for better security
        if "://" in self.connection_string:
            parts = self.connection_string.split("://")
            if len(parts) == 2:
                protocol = parts[0]
                rest = parts[1]
                if "@" in rest:
                    user_pass, host_part = rest.split("@", 1)
                    if ":" in user_pass:
                        user, _ = user_pass.split(":", 1)
                        return f"{protocol}://{user}:***@{host_part}"
        return "***" 