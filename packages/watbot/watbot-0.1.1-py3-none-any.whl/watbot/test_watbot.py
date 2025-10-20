"""
Simple test script for WATBOT
"""

from watbot import WhatsAppBot, BotConfig

def test_basic():
    """Test basic bot initialization"""
    print("Testing basic bot initialization...")
    
    bot = WhatsAppBot(
        debug=True,
        headless=True,
        monitor_contacts=["ALL"],
        session_id="test_session"
    )
    
    print(f"✅ Bot initialized")
    print(f"   - Debug: {bot.config.whatsapp.debug}")
    print(f"   - Headless: {bot.config.whatsapp.headless}")
    print(f"   - Monitor: {bot.config.whatsapp.monitor_contacts}")
    print(f"   - AI Enabled: {bot.config.ai.enabled}")
    print(f"   - Session ID: {bot.config.whatsapp.session_id}")
    
    return True

def test_config():
    """Test configuration system"""
    print("\nTesting configuration system...")
    
    # Create config
    config = BotConfig()
    config.whatsapp.monitor_contacts = ["Test Contact"]
    config.ai.personality = "test personality"
    
    # Save to file
    config.save_to_file("test_config.json")
    print("✅ Config saved to test_config.json")
    
    # Load from file
    loaded_config = BotConfig.from_file("test_config.json")
    print("✅ Config loaded from file")
    
    # Verify
    assert loaded_config.whatsapp.monitor_contacts == ["Test Contact"]
    assert loaded_config.ai.personality == "test personality"
    print("✅ Config values verified")
    
    # Cleanup
    import os
    os.remove("test_config.json")
    
    return True

def test_env_dict():
    """Test environment variable generation"""
    print("\nTesting environment variable generation...")
    
    config = BotConfig()
    config.whatsapp.debug = True
    config.whatsapp.monitor_contacts = ["Test"]
    config.ai.personality = "friendly"
    
    env = config.get_env_dict()
    
    assert 'SESSION_ID' in env
    assert 'MONITOR_CONTACTS' in env
    assert 'DEBUG_MODE' in env
    assert 'AI_PERSONALITY' in env
    
    print("✅ Environment variables generated correctly")
    print(f"   Sample: DEBUG_MODE={env['DEBUG_MODE']}")
    print(f"   Sample: AI_PERSONALITY={env['AI_PERSONALITY']}")
    
    return True

def main():
    """Run all tests"""
    print("=" * 50)
    print("WATBOT Test Suite")
    print("=" * 50)
    
    tests = [
        test_basic,
        test_config,
        test_env_dict
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    if failed == 0:
        print("\n✅ All tests passed! WATBOT is ready to use.")
        print("\nQuick start:")
        print("  python -c \"from watbot import WhatsAppBot; WhatsAppBot().start()\"")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
