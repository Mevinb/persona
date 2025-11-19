"""
ARK Powerful Bot 3.0 - Service Integration
==========================================
A comprehensive AI assistant with integrated services.
"""

from ark_intelligent_brain import ARKIntelligentBrain
from services.service_manager import ServiceManager

class ARKProfessional:
    """Advanced Personal AI Assistant with integrated services."""
    
    def __init__(self):
        self.version = "3.0"
        self.name = "ARK Professional"
        self.capabilities = [
            "Intelligent Reasoning",
            "Task Management", 
            "System Automation", 
            "Adaptive Learning",
            "Email Management",
            "Web Search & Information",
            "System Control",
            "Service Integration"
        ]
        
        # Initialize core AI brain
        self.brain = ARKIntelligentBrain()
        
        # Initialize service manager
        self.service_manager = ServiceManager()
        loaded_services = self.service_manager.auto_load_services()
        
        print(f"\n🤖 {self.name} {self.version} - Powerful Bot with Service Integration")
        print("Capabilities: " + " • ".join(self.capabilities))
        
        # Show available services
        available_services = self.service_manager.get_available_services()
        if available_services:
            print(f"🔧 Active Services: {', '.join(available_services)}")
        else:
            print("🔧 Services: Running in demo mode")
    
    def respond(self, user_input: str) -> str:
        """Process user input with service integration."""
        
        # Check if this is a service-related command
        service_routing = self.service_manager.smart_command_routing(user_input)
        
        if service_routing:
            # Execute service command
            result = self.service_manager.execute_service_command(
                service_routing["service"],
                service_routing["command"], 
                {"input": user_input}
            )
            
            if result.success:
                service_response = result.data
                formatted_response = self._format_service_response(
                    service_routing["service"], 
                    service_response
                )
                
                # Store interaction for learning
                self.brain.process_input(user_input)
                return formatted_response
            else:
                # Service failed, fall back to brain response
                error_context = f"Service '{service_routing['service']}' issue: {result.error}"
                fallback_response = self.brain.process_input(user_input)
                return f"{fallback_response}\n\n⚠️ Note: {error_context}"
        
        # No service match, use standard brain processing
        return self.brain.process_input(user_input)
    
    def _format_service_response(self, service_name: str, response: dict) -> str:
        """Format service response for user display."""
        
        action = response.get("action", "")
        message = response.get("message", "")
        
        if service_name == "email":
            return self._format_email_response(action, response)
        elif service_name == "web_search":
            return self._format_search_response(action, response)
        elif service_name == "system_control":
            return self._format_system_response(action, response)
        else:
            return message or str(response)
    
    def _format_email_response(self, action: str, response: dict) -> str:
        """Format email service responses."""
        
        if action == "email_draft":
            draft = response.get("draft", {})
            email_text = f"📧 **Email Draft Prepared**\n\n"
            email_text += f"**To:** {draft.get('to', 'Unknown')}\n"
            email_text += f"**Subject:** {draft.get('subject', '(No Subject)')}\n\n"
            email_text += f"**Message:**\n{draft.get('body', '(No Content)')}\n\n"
            email_text += "Would you like me to send this email or make any changes?"
            return email_text
        
        elif action == "emails_retrieved":
            emails = response.get("emails", [])
            email_list = []
            for email in emails:
                status = "🔴 NEW" if email.get("unread") else "✓"
                email_list.append(f"{status} **{email.get('from')}** - {email.get('subject')}\n   _{email.get('preview', '')[:60]}..._")
            
            email_text = f"📨 **Your Recent Emails:**\n\n"
            email_text += "\n".join(email_list)
            email_text += f"\n\n{response.get('message', '')}"
            return email_text
        
        elif action == "request_info":
            return f"📧 {response.get('message', '')}"
        
        else:
            return response.get("message", "Email operation completed")
    
    def _format_search_response(self, action: str, response: dict) -> str:
        """Format web search responses."""
        
        if action == "search_results":
            results = response.get("results", [])
            query = response.get("query", "")
            
            formatted_results = []
            for i, result in enumerate(results[:3], 1):
                formatted_results.append(f"**{i}. {result.get('title', 'No Title')}**\n   {result.get('snippet', 'No description')}\n   🔗 _{result.get('domain', 'unknown')}_")
            
            search_text = f"🔍 **Search Results for \\"{query}\\":**\n\n"
            search_text += "\n".join(formatted_results)
            search_text += f"\n\n{response.get('message', '')}"
            return search_text
        
        elif action == "weather_info":
            weather = response.get("weather", {})
            current = weather.get("current", {})
            forecast = weather.get("forecast", [])
            
            forecast_text = ""
            for day in forecast[:3]:
                forecast_text += f"   {day.get('day')}: {day.get('high')}/{day.get('low')} - {day.get('condition')}\n"
            
            weather_text = f"🌤️ **Weather for {weather.get('location', 'your area')}:**\n\n"
            weather_text += "**Current Conditions:**\n"
            weather_text += f"🌡️ {current.get('temperature', 'Unknown')} - {current.get('condition', 'Unknown')}\n"
            weather_text += f"💧 Humidity: {current.get('humidity', 'Unknown')}\n"
            weather_text += f"💨 Wind: {current.get('wind', 'Unknown')}\n\n"
            weather_text += "**Forecast:**\n"
            weather_text += forecast_text
            return weather_text
        
        elif action == "news_results":
            articles = response.get("articles", [])
            topic = response.get("topic", "")
            
            news_list = []
            for article in articles[:3]:
                news_list.append(f"📰 **{article.get('headline', 'No Headline')}**\n   _{article.get('summary', 'No summary')}_\n   📅 {article.get('time', '')} | 📺 {article.get('source', '')}")
            
            news_text = f"📰 **Latest News{f' about {topic}' if topic != 'general' else ''}:**\n\n"
            news_text += "\n".join(news_list)
            return news_text
        
        else:
            return response.get("message", "Search completed")
    
    def _format_system_response(self, action: str, response: dict) -> str:
        """Format system control responses."""
        
        if action == "app_opened":
            return f"✅ **Application Opened**\n\nSuccessfully launched {response.get('app', 'application')}!"
        
        elif action == "app_closed":
            closed_processes = response.get('closed_processes', [])
            return f"✅ **Application Closed**\n\nStopped {len(closed_processes)} process(es) for {response.get('app', 'application')}"
        
        elif action == "system_info":
            info = response.get("info", {})
            memory = info.get("memory", {})
            disk = info.get("disk", {})
            
            system_text = "💻 **System Information:**\n\n"
            system_text += f"**Platform:** {info.get('platform', 'Unknown')} {info.get('platform_version', '')}\n"
            system_text += f"**Processor:** {info.get('processor', 'Unknown')}\n"
            system_text += f"**CPU Usage:** {info.get('cpu_usage', 'Unknown')}\n"
            system_text += f"**Memory:** {memory.get('usage', 'Unknown')} used ({memory.get('available', 'Unknown')} available)\n"
            system_text += f"**Disk Space:** {disk.get('usage', 'Unknown')} used ({disk.get('free', 'Unknown')} free)\n"
            system_text += f"**Uptime:** {info.get('uptime', 'Unknown')}"
            return system_text
        
        elif action == "process_info":
            top_processes = response.get("top_processes", [])
            total = response.get("total_processes", 0)
            
            process_list = []
            for proc in top_processes[:5]:
                process_list.append(f"   {proc.get('name', 'Unknown')} (PID: {proc.get('pid', '?')}) - CPU: {proc.get('cpu', '?')}, Memory: {proc.get('memory', '?')}")
            
            process_text = f"⚙️ **Running Processes ({total} total):**\n\n"
            process_text += "**Top Processes by CPU Usage:**\n"
            process_text += "\n".join(process_list)
            return process_text
        
        elif action == "app_open_failed":
            return f"❌ **Could not open {response.get('app', 'application')}**\n\n{response.get('message', '')}\n\n💡 {response.get('suggestion', '')}"
        
        elif action == "request_info":
            return f"🤖 {response.get('message', '')}"
        
        else:
            return response.get("message", "System operation completed")
    
    def get_service_status(self) -> dict:
        """Get status of all services."""
        return self.service_manager.get_all_status()
    
    def get_capabilities_overview(self) -> str:
        """Get overview of all capabilities."""
        service_capabilities = self.service_manager.get_service_capabilities()
        
        overview = f"🤖 **{self.name} {self.version} Capabilities:**\n\n"
        
        # Core capabilities
        overview += "**Core AI Features:**\n"
        for capability in self.capabilities[:4]:
            overview += f"   ✓ {capability}\n"
        
        # Service capabilities
        if service_capabilities:
            overview += "\n**Integrated Services:**\n"
            for service, caps in service_capabilities.items():
                cap_preview = ', '.join(caps[:3])
                if len(caps) > 3:
                    cap_preview += "..."
                overview += f"   🔧 **{service.title()}:** {cap_preview}\n"
        
        return overview
