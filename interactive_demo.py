"""
ARK Powerful Bot Interactive Demo
===============================
Live demonstration of ARK's service integration.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def interactive_demo():
    """Interactive demonstration of ARK services."""
    
    print("🤖 ARK POWERFUL BOT - INTERACTIVE DEMO")
    print("=" * 50)
    
    try:
        # Initialize ARK with service integration
        from ark_intelligent_brain import ARKIntelligentBrain
        from services.service_manager import ServiceManager
        
        print("Initializing ARK with service integration...")
        brain = ARKIntelligentBrain()
        service_manager = ServiceManager()
        service_manager.auto_load_services()
        
        print(f"\n✅ ARK Powerful Bot Ready!")
        print("Available services: email, web_search, system_control")
        print("Enhanced AI capabilities with service integration")
        
        # Example interactions
        print(f"\n📋 Example commands you can try:")
        examples = [
            "Send an email to my manager",
            "Search for artificial intelligence news", 
            "What's the weather today?",
            "Open calculator",
            "Show system information",
            "Get the latest tech news"
        ]
        
        for i, example in enumerate(examples, 1):
            print(f"   {i}. {example}")
        
        print(f"\n{'=' * 50}")
        print("🎮 INTERACTIVE MODE - Type 'quit' to exit")
        print("Try asking ARK to help with emails, searches, weather, or system tasks!")
        print(f"{'=' * 50}")
        
        while True:
            try:
                user_input = input(f"\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'stop']:
                    print("🤖 ARK: Goodbye! Thanks for trying ARK Powerful Bot!")
                    break
                
                if not user_input:
                    continue
                
                print("🤖 ARK: ", end="")
                
                # Check for service routing
                service_routing = service_manager.smart_command_routing(user_input)
                
                if service_routing:
                    # Execute service
                    result = service_manager.execute_service_command(
                        service_routing["service"],
                        service_routing["command"],
                        {"input": user_input}
                    )
                    
                    if result.success:
                        response = result.data
                        
                        # Format response based on service
                        service_name = service_routing["service"]
                        action = response.get("action", "")
                        message = response.get("message", "")
                        
                        print(f"[{service_name.upper()} SERVICE ACTIVATED]")
                        
                        if service_name == "email":
                            if action == "email_draft":
                                draft = response.get("draft", {})
                                print(f"📧 Email draft prepared for {draft.get('to')}:")
                                print(f"   Subject: {draft.get('subject', 'No subject')}")
                                print(f"   Message: {draft.get('body', 'No content')}")
                            else:
                                print(message)
                        
                        elif service_name == "web_search":
                            if action == "search_results":
                                query = response.get("query", "")
                                results = response.get("results", [])
                                print(f"🔍 Found {len(results)} results for '{query}':")
                                for i, result in enumerate(results[:2], 1):
                                    print(f"   {i}. {result.get('title', 'No title')}")
                            elif action == "weather_info":
                                weather = response.get("weather", {})
                                current = weather.get("current", {})
                                print(f"🌤️ Weather: {current.get('temperature')} - {current.get('condition')}")
                            elif action == "news_results":
                                articles = response.get("articles", [])
                                print(f"📰 Latest news headlines:")
                                for article in articles[:2]:
                                    print(f"   • {article.get('headline', 'No headline')}")
                            else:
                                print(message)
                        
                        elif service_name == "system_control":
                            if action == "app_opened":
                                print(f"✅ Opened {response.get('app', 'application')}")
                            elif action == "system_info":
                                info = response.get("info", {})
                                print(f"💻 System: {info.get('cpu_usage', '?')} CPU, {info.get('memory', {}).get('usage', '?')} memory")
                            else:
                                print(message)
                        
                        else:
                            print(message)
                    
                    else:
                        print(f"Service error: {result.error}")
                        # Fallback to brain
                        fallback = brain.process_input(user_input)
                        print(f"\nFalling back to AI brain: {fallback}")
                
                else:
                    # No service match, use brain
                    response = brain.process_input(user_input)
                    print(f"[AI BRAIN] {response}")
                
            except KeyboardInterrupt:
                print(f"\n🤖 ARK: Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the interactive demo."""
    
    print("Starting ARK Powerful Bot Interactive Demo...")
    print("This showcases real-time service integration capabilities.\n")
    
    success = interactive_demo()
    
    if success:
        print(f"\n✅ Demo completed successfully!")
    else:
        print(f"\n❌ Demo encountered issues")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())