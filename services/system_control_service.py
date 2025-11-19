"""
System Control Service
=====================
System automation and control service for ARK.
"""

import os
import sys
import subprocess
import psutil
import platform
from typing import Dict, Any, List
from .base_service import BaseService, ServiceResult

class SystemControlService(BaseService):
    """System control and automation service for ARK."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("system_control", config)
        self.allowed_operations = self.config.get("allowed_operations", [
            "open_app", "close_app", "system_info", "process_info", "file_operations"
        ])
        
    def initialize(self) -> bool:
        """Initialize system control service."""
        try:
            # Test system access
            self.platform = platform.system()
            self.is_initialized = True
            self.log_info(f"System control service initialized on {self.platform}")
            return True
        except Exception as e:
            self.log_error(f"Failed to initialize system control service: {e}")
            return False
    
    def get_capabilities(self) -> List[str]:
        """Get system control capabilities."""
        return [
            "open_applications",
            "close_applications", 
            "system_information",
            "process_management",
            "file_operations",
            "system_monitoring",
            "automation_scripts"
        ]
    
    def execute_command(self, command: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute system control command."""
        params = parameters or {}
        
        try:
            if command == "system_operation":
                return self._handle_system_operation(params)
            elif command == "open_app":
                return self._open_application(params)
            elif command == "close_app":
                return self._close_application(params)
            elif command == "system_info":
                return self._get_system_info(params)
            elif command == "process_info":
                return self._get_process_info(params)
            else:
                return {"error": f"Unknown system command: {command}"}
                
        except Exception as e:
            self.log_error(f"System command '{command}' failed: {e}")
            return {"error": str(e)}
    
    def _handle_system_operation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general system operation from natural language."""
        user_input = params.get("input", "").lower()
        
        # Parse the operation type
        if any(word in user_input for word in ["open", "launch", "start", "run"]):
            app_name = self._extract_app_name(user_input)
            return self._open_application({"app": app_name})
        elif any(word in user_input for word in ["close", "quit", "exit", "stop"]):
            app_name = self._extract_app_name(user_input)
            return self._close_application({"app": app_name})
        elif any(word in user_input for word in ["system info", "computer info", "system status"]):
            return self._get_system_info(params)
        elif any(word in user_input for word in ["processes", "running apps", "task manager"]):
            return self._get_process_info(params)
        else:
            return {
                "action": "unknown_operation",
                "message": "I can help you open/close applications, get system information, or manage processes. What would you like to do?",
                "suggestions": ["Open an application", "Check system information", "View running processes"]
            }
    
    def _open_application(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Open an application."""
        app = params.get("app", "").lower()
        
        if not app:
            return {
                "action": "request_info",
                "message": "Which application would you like me to open?",
                "needed": "application_name"
            }
        
        try:
            # Common application mappings
            app_mappings = {
                "notepad": "notepad.exe",
                "calculator": "calc.exe", 
                "paint": "mspaint.exe",
                "browser": "msedge.exe",
                "edge": "msedge.exe",
                "chrome": "chrome.exe",
                "firefox": "firefox.exe",
                "explorer": "explorer.exe",
                "file explorer": "explorer.exe",
                "task manager": "taskmgr.exe",
                "control panel": "control.exe",
                "command prompt": "cmd.exe",
                "powershell": "powershell.exe",
                "outlook": "outlook.exe",
                "word": "winword.exe",
                "excel": "excel.exe",
                "powerpoint": "powerpnt.exe"
            }
            
            executable = app_mappings.get(app, f"{app}.exe")
            
            if self.platform == "Windows":
                # Try to start the application
                try:
                    subprocess.Popen(executable, shell=True)
                    return {
                        "action": "app_opened",
                        "app": app,
                        "message": f"Successfully opened {app}",
                        "status": "success"
                    }
                except Exception as e:
                    return {
                        "action": "app_open_failed",
                        "app": app,
                        "message": f"Could not open {app}. Make sure it's installed on your system.",
                        "error": str(e),
                        "suggestion": "Try using the full application name or check if it's installed"
                    }
            else:
                return {
                    "action": "platform_not_supported",
                    "message": f"Application launching not yet supported on {self.platform}",
                    "platform": self.platform
                }
                
        except Exception as e:
            return {
                "action": "error",
                "message": f"Error opening application: {str(e)}"
            }
    
    def _close_application(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Close an application."""
        app = params.get("app", "").lower()
        
        if not app:
            return {
                "action": "request_info", 
                "message": "Which application would you like me to close?",
                "needed": "application_name"
            }
        
        try:
            # Find and terminate processes
            closed_processes = []
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if app in proc.info['name'].lower():
                        proc.terminate()
                        closed_processes.append(proc.info['name'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if closed_processes:
                return {
                    "action": "app_closed",
                    "app": app,
                    "closed_processes": closed_processes,
                    "message": f"Successfully closed {len(closed_processes)} process(es) related to {app}"
                }
            else:
                return {
                    "action": "app_not_found",
                    "app": app,
                    "message": f"No running processes found for {app}",
                    "suggestion": "Check if the application is currently running"
                }
                
        except Exception as e:
            return {
                "action": "error",
                "message": f"Error closing application: {str(e)}"
            }
    
    def _get_system_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get system information."""
        try:
            # Gather system information
            cpu_info = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            system_info = {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "architecture": platform.architecture()[0],
                "processor": platform.processor(),
                "cpu_usage": f"{cpu_info}%",
                "memory": {
                    "total": f"{memory.total / (1024**3):.1f} GB",
                    "available": f"{memory.available / (1024**3):.1f} GB",
                    "usage": f"{memory.percent}%"
                },
                "disk": {
                    "total": f"{disk.total / (1024**3):.1f} GB",
                    "free": f"{disk.free / (1024**3):.1f} GB",
                    "usage": f"{(disk.used / disk.total) * 100:.1f}%"
                },
                "uptime": self._get_uptime()
            }
            
            return {
                "action": "system_info",
                "info": system_info,
                "message": f"System: {system_info['platform']} | CPU: {system_info['cpu_usage']} | Memory: {system_info['memory']['usage']} | Disk: {system_info['disk']['usage']}"
            }
            
        except Exception as e:
            return {
                "action": "error",
                "message": f"Error getting system information: {str(e)}"
            }
    
    def _get_process_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get running process information."""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cpu": f"{proc.info['cpu_percent']:.1f}%",
                        "memory": f"{proc.info['memory_percent']:.1f}%"
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage and get top 10
            top_processes = sorted(processes, key=lambda x: float(x['cpu'].rstrip('%')), reverse=True)[:10]
            
            return {
                "action": "process_info",
                "total_processes": len(processes),
                "top_processes": top_processes,
                "message": f"Found {len(processes)} running processes. Showing top 10 by CPU usage."
            }
            
        except Exception as e:
            return {
                "action": "error",
                "message": f"Error getting process information: {str(e)}"
            }
    
    def _get_uptime(self) -> str:
        """Get system uptime."""
        try:
            uptime_seconds = psutil.boot_time()
            import time
            current_time = time.time()
            uptime = current_time - uptime_seconds
            
            days = int(uptime // 86400)
            hours = int((uptime % 86400) // 3600)
            minutes = int((uptime % 3600) // 60)
            
            return f"{days}d {hours}h {minutes}m"
        except:
            return "Unknown"
    
    def _extract_app_name(self, text: str) -> str:
        """Extract application name from natural language input."""
        text = text.lower()
        
        # Remove operation words
        operation_words = ["open", "launch", "start", "run", "close", "quit", "exit", "stop"]
        for word in operation_words:
            text = text.replace(word, "").strip()
        
        # Remove common filler words
        filler_words = ["the", "a", "an", "please", "can", "you", "application", "app", "program"]
        words = text.split()
        filtered_words = [word for word in words if word not in filler_words]
        
        return " ".join(filtered_words).strip()