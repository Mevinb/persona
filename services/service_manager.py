"""
Service Manager
==============
Central manager for all ARK services.
"""

import os
import json
import importlib
from typing import Dict, Any, List, Optional
from .base_service import BaseService, ServiceResult

class ServiceManager:
    """Manages all ARK services."""
    
    def __init__(self, config_path: str = "config/services.json"):
        self.services: Dict[str, BaseService] = {}
        self.config_path = config_path
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load service configuration."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                # Default configuration
                default_config = {
                    "email": {
                        "enabled": True,
                        "provider": "gmail",
                        "credentials": {}
                    },
                    "calendar": {
                        "enabled": True,
                        "provider": "google",
                        "credentials": {}
                    },
                    "file_manager": {
                        "enabled": True,
                        "cloud_providers": ["google_drive", "onedrive"]
                    },
                    "web_search": {
                        "enabled": True,
                        "search_engine": "google",
                        "news_enabled": True,
                        "weather_enabled": True
                    },
                    "system_control": {
                        "enabled": True,
                        "allowed_operations": ["open_app", "close_app", "system_info"]
                    },
                    "communication": {
                        "enabled": True,
                        "platforms": ["teams", "slack"]
                    }
                }
                self.save_config(default_config)
                return default_config
        except Exception as e:
            print(f"Error loading service config: {e}")
            return {}
    
    def save_config(self, config: Dict[str, Any]):
        """Save service configuration."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving service config: {e}")
    
    def register_service(self, service: BaseService) -> bool:
        """Register a new service."""
        try:
            if service.initialize():
                self.services[service.name] = service
                service.log_info("Service registered successfully")
                return True
            else:
                service.log_error("Service initialization failed")
                return False
        except Exception as e:
            print(f"Error registering service {service.name}: {e}")
            return False
    
    def get_service(self, name: str) -> Optional[BaseService]:
        """Get a service by name."""
        return self.services.get(name)
    
    def execute_service_command(self, service_name: str, command: str, parameters: Dict[str, Any] = None) -> ServiceResult:
        """Execute a command on a specific service."""
        service = self.get_service(service_name)
        
        if not service:
            return ServiceResult(False, error=f"Service '{service_name}' not found")
        
        if not service.is_available():
            return ServiceResult(False, error=f"Service '{service_name}' is not available")
        
        try:
            result = service.execute_command(command, parameters or {})
            return ServiceResult(True, data=result)
        except Exception as e:
            return ServiceResult(False, error=f"Service command failed: {str(e)}")
    
    def get_available_services(self) -> List[str]:
        """Get list of available services."""
        return [name for name, service in self.services.items() if service.is_available()]
    
    def get_service_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of all services."""
        capabilities = {}
        for name, service in self.services.items():
            if service.is_available():
                capabilities[name] = service.get_capabilities()
        return capabilities
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all services."""
        status = {}
        for name, service in self.services.items():
            status[name] = service.get_status()
        return status
    
    def auto_load_services(self):
        """Automatically load and register all available services."""
        service_modules = [
            "email_service",
            "calendar_service", 
            "file_manager_service",
            "web_search_service",
            "system_control_service",
            "communication_service"
        ]
        
        loaded_count = 0
        
        for module_name in service_modules:
            try:
                module = importlib.import_module(f"services.{module_name}")
                service_class = getattr(module, module_name.replace("_service", "").title().replace("_", "") + "Service")
                
                service_config = self.config.get(module_name.replace("_service", ""), {})
                if service_config.get("enabled", True):
                    service = service_class(config=service_config)
                    if self.register_service(service):
                        loaded_count += 1
                        print(f"✅ Loaded {service.name} service")
                    else:
                        print(f"❌ Failed to load {service.name} service")
                else:
                    print(f"⚠️ {module_name} service is disabled in config")
                    
            except ImportError:
                print(f"⚠️ Service module {module_name} not found - will create it")
            except Exception as e:
                print(f"❌ Error loading {module_name}: {e}")
        
        print(f"\\n🎯 Service Manager: Loaded {loaded_count} services")
        return loaded_count
    
    def smart_command_routing(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Intelligently route user commands to appropriate services."""
        user_input_lower = user_input.lower()
        
        # Email-related commands
        if any(word in user_input_lower for word in ["email", "mail", "send message", "inbox", "compose"]):
            email_service = self.get_service("email")
            if email_service and email_service.is_available():
                if "send" in user_input_lower or "compose" in user_input_lower:
                    return {"service": "email", "command": "compose", "input": user_input}
                elif "read" in user_input_lower or "check" in user_input_lower:
                    return {"service": "email", "command": "read", "input": user_input}
        
        # Calendar-related commands
        if any(word in user_input_lower for word in ["schedule", "calendar", "meeting", "appointment", "event"]):
            calendar_service = self.get_service("calendar")
            if calendar_service and calendar_service.is_available():
                if "schedule" in user_input_lower or "create" in user_input_lower:
                    return {"service": "calendar", "command": "create_event", "input": user_input}
                elif "show" in user_input_lower or "list" in user_input_lower:
                    return {"service": "calendar", "command": "list_events", "input": user_input}
        
        # File-related commands
        if any(word in user_input_lower for word in ["file", "document", "folder", "save", "open file", "download"]):
            file_service = self.get_service("file_manager")
            if file_service and file_service.is_available():
                return {"service": "file_manager", "command": "file_operation", "input": user_input}
        
        # Search-related commands
        if any(word in user_input_lower for word in ["search", "find", "look up", "weather", "news"]):
            search_service = self.get_service("web_search")
            if search_service and search_service.is_available():
                if "weather" in user_input_lower:
                    return {"service": "web_search", "command": "weather", "input": user_input}
                elif "news" in user_input_lower:
                    return {"service": "web_search", "command": "news", "input": user_input}
                else:
                    return {"service": "web_search", "command": "search", "input": user_input}
        
        # System control commands
        if any(word in user_input_lower for word in ["open", "close", "launch", "run", "system"]):
            system_service = self.get_service("system_control")
            if system_service and system_service.is_available():
                return {"service": "system_control", "command": "system_operation", "input": user_input}
        
        return None