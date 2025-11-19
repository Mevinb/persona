"""
Base Service Class
=================
Abstract base class for all ARK services.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging

class BaseService(ABC):
    """Base class for all ARK services."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        self.logger = logging.getLogger(f"ARK.Services.{name}")
        self.is_initialized = False
        
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the service. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def execute_command(self, command: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a service command. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities this service provides."""
        pass
    
    def is_available(self) -> bool:
        """Check if service is available and ready."""
        return self.enabled and self.is_initialized
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status information."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "initialized": self.is_initialized,
            "available": self.is_available(),
            "capabilities": self.get_capabilities()
        }
    
    def log_info(self, message: str):
        """Log info message."""
        self.logger.info(f"[{self.name}] {message}")
    
    def log_error(self, message: str):
        """Log error message."""
        self.logger.error(f"[{self.name}] {message}")
    
    def log_warning(self, message: str):
        """Log warning message."""
        self.logger.warning(f"[{self.name}] {message}")

class ServiceResult:
    """Standard result object for service operations."""
    
    def __init__(self, success: bool, data: Any = None, message: str = "", error: str = ""):
        self.success = success
        self.data = data
        self.message = message
        self.error = error
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "data": self.data,
            "message": self.message,
            "error": self.error
        }