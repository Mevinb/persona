"""
Email Service
============
Comprehensive email management service for ARK.
"""

import re
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
from .base_service import BaseService, ServiceResult

class EmailService(BaseService):
    """Email service for ARK - supports Gmail, Outlook, and other providers."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("email", config)
        self.provider = self.config.get("provider", "gmail")
        self.smtp_server = None
        self.imap_server = None
        
    def initialize(self) -> bool:
        """Initialize email service."""
        try:
            # Configure based on provider
            if self.provider == "gmail":
                self.smtp_config = {
                    "server": "smtp.gmail.com",
                    "port": 587,
                    "use_tls": True
                }
                self.imap_config = {
                    "server": "imap.gmail.com",
                    "port": 993,
                    "use_ssl": True
                }
            elif self.provider == "outlook":
                self.smtp_config = {
                    "server": "smtp-mail.outlook.com", 
                    "port": 587,
                    "use_tls": True
                }
                self.imap_config = {
                    "server": "outlook.office365.com",
                    "port": 993,
                    "use_ssl": True
                }
            
            self.is_initialized = True
            self.log_info(f"Email service initialized with {self.provider}")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to initialize email service: {e}")
            return False
    
    def get_capabilities(self) -> List[str]:
        """Get email service capabilities."""
        return [
            "send_email",
            "read_emails", 
            "search_emails",
            "compose_email",
            "manage_folders",
            "email_templates"
        ]
    
    def execute_command(self, command: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute email command."""
        params = parameters or {}
        
        try:
            if command == "compose":
                return self._compose_email(params)
            elif command == "send":
                return self._send_email(params)
            elif command == "read":
                return self._read_emails(params)
            elif command == "search":
                return self._search_emails(params)
            else:
                return {"error": f"Unknown email command: {command}"}
                
        except Exception as e:
            self.log_error(f"Email command '{command}' failed: {e}")
            return {"error": str(e)}
    
    def _compose_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Compose a new email based on natural language input."""
        user_input = params.get("input", "")
        
        # Extract email components from natural language
        email_data = self._parse_email_request(user_input)
        
        if not email_data.get("recipient"):
            return {
                "action": "request_info",
                "message": "I'll help you compose an email. Who would you like to send it to?",
                "needed": "recipient"
            }
        
        if not email_data.get("content") and not email_data.get("subject"):
            return {
                "action": "request_info", 
                "message": f"What would you like to say to {email_data['recipient']}?",
                "needed": "content"
            }
        
        # Generate email draft
        draft = {
            "to": email_data["recipient"],
            "subject": email_data.get("subject", ""),
            "body": email_data.get("content", ""),
            "priority": email_data.get("priority", "normal")
        }
        
        return {
            "action": "email_draft",
            "draft": draft,
            "message": f"I've prepared an email draft for {draft['to']}. Would you like me to send it or make changes?"
        }
    
    def _send_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send an email."""
        # This would require proper authentication setup
        return {
            "action": "email_sent",
            "message": "Email sent successfully! (Demo mode - authentication needed for actual sending)",
            "status": "demo_mode"
        }
    
    def _read_emails(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read recent emails."""
        # Demo email data
        demo_emails = [
            {
                "from": "team@company.com",
                "subject": "Weekly Team Meeting",
                "preview": "Hi everyone, our weekly team meeting is scheduled for...",
                "time": "2 hours ago",
                "unread": True
            },
            {
                "from": "client@business.com", 
                "subject": "Project Update Request",
                "preview": "Could you please provide an update on the current project status...",
                "time": "5 hours ago",
                "unread": True
            }
        ]
        
        return {
            "action": "emails_retrieved",
            "emails": demo_emails,
            "message": f"You have {len([e for e in demo_emails if e['unread']])} unread emails"
        }
    
    def _search_emails(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search emails."""
        query = params.get("query", "")
        return {
            "action": "search_results",
            "message": f"Searched for: {query} (Demo mode - would show matching emails)",
            "results": []
        }
    
    def _parse_email_request(self, text: str) -> Dict[str, Any]:
        """Parse natural language email request."""
        email_data = {}
        
        # Extract recipient using patterns
        recipient_patterns = [
            r"send (?:an? )?email to ([\\w\\s]+)",
            r"email ([\\w\\s]+)",
            r"message ([\\w\\s]+)",
            r"to ([\\w@\\.]+)"
        ]
        
        for pattern in recipient_patterns:
            match = re.search(pattern, text.lower())
            if match:
                email_data["recipient"] = match.group(1).strip()
                break
        
        # Extract subject
        subject_patterns = [
            r"subject[:\\s]+([^\\n]+)",
            r"about ([^\\n]+)",
            r"regarding ([^\\n]+)"
        ]
        
        for pattern in subject_patterns:
            match = re.search(pattern, text.lower())
            if match:
                email_data["subject"] = match.group(1).strip()
                break
        
        # Detect urgency
        if any(word in text.lower() for word in ["urgent", "asap", "immediately", "rush"]):
            email_data["priority"] = "high"
        
        # Extract content (everything after common separators)
        content_separators = ["saying:", "message:", "tell them:", "content:"]
        for separator in content_separators:
            if separator in text.lower():
                parts = text.lower().split(separator, 1)
                if len(parts) > 1:
                    email_data["content"] = parts[1].strip()
                    break
        
        return email_data