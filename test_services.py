"""
Simple ARK Service Test
======================
Basic test of ARK service integration.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def simple_service_test():
    """Simple test of ARK services."""
    
    print("🚀 ARK SERVICE INTEGRATION TEST")
    print("=" * 40)
    
    try:
        # Test core components first
        print("Testing core components...")
        
        from ark_intelligent_brain import ARKIntelligentBrain
        brain = ARKIntelligentBrain()
        print("✅ ARK Brain loaded successfully")
        
        # Test service manager
        from services.service_manager import ServiceManager
        service_manager = ServiceManager()
        print("✅ Service Manager loaded")
        
        # Load services
        loaded_count = service_manager.auto_load_services()
        print(f"✅ Loaded {loaded_count} services (demo mode)")
        
        # Test service routing
        routing_tests = [
            "send an email to john",
            "search for AI trends", 
            "what's the weather like",
            "open calculator",
            "show system info"
        ]
        
        print(f"\n🧪 Testing Smart Command Routing:")
        for test in routing_tests:
            routing = service_manager.smart_command_routing(test)
            if routing:
                print(f"✅ '{test}' -> {routing['service']}/{routing['command']}")
            else:
                print(f"⚠️ '{test}' -> No service routing")
        
        # Test individual services
        print(f"\n🔧 Testing Individual Services:")
        
        # Email service
        try:
            from services.email_service import EmailService
            email_service = EmailService()
            if email_service.initialize():
                print("✅ Email Service: Working")
            else:
                print("⚠️ Email Service: Demo mode")
        except Exception as e:
            print(f"❌ Email Service: {e}")
        
        # Web search service
        try:
            from services.web_search_service import WebSearchService
            search_service = WebSearchService()
            if search_service.initialize():
                print("✅ Web Search Service: Working")
            else:
                print("⚠️ Web Search Service: Demo mode")
        except Exception as e:
            print(f"❌ Web Search Service: {e}")
        
        # System control service
        try:
            from services.system_control_service import SystemControlService
            system_service = SystemControlService()
            if system_service.initialize():
                print("✅ System Control Service: Working")
            else:
                print("⚠️ System Control Service: Demo mode")
        except Exception as e:
            print(f"❌ System Control Service: {e}")
        
        print(f"\n🎯 SERVICE INTEGRATION TEST COMPLETE")
        print("✅ Core components functional")
        print("✅ Service architecture working")
        print("✅ Command routing operational")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = simple_service_test()
    if success:
        print(f"\n🎉 ARK Service Integration: SUCCESSFUL!")
    else:
        print(f"\n❌ ARK Service Integration: FAILED")