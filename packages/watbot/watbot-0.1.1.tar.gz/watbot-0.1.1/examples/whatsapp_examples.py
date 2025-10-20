"""
Example usage of WATBOT WhatsApp Bot
"""

from watbot import WhatsAppBot, BotConfig

# Example 1: Simple usage with defaults
def example_basic():
    print("Example 1: Basic usage")
    bot = WhatsAppBot()
    bot.start()

# Example 2: Custom configuration
def example_custom_config():
    print("Example 2: Custom configuration")
    
    # Create custom config
    config = BotConfig()
    
    # WhatsApp settings
    config.whatsapp.debug = True
    config.whatsapp.headless = False  # Show browser window
    config.whatsapp.monitor_contacts = ["John Doe", "918812345678"]
    config.whatsapp.do_not_reply = ["Spam Contact", "919999999999"]
    config.whatsapp.session_id = "my_session"
    
    # AI settings
    config.ai.enabled = True
    config.ai.personality = "professional and concise"
    config.ai.context_limit = 15
    
    # Start bot
    bot = WhatsAppBot(config=config)
    bot.start()

# Example 3: Direct parameters
def example_direct_params():
    print("Example 3: Direct parameters")
    
    bot = WhatsAppBot(
        debug=True,
        headless=False,
        monitor_contacts=["ALL"],
        do_not_reply=["Spam", "918888888888"],
        ai_enabled=True,
        personality="friendly and funny with dad jokes",
        session_id="test_session"
    )
    bot.start()

# Example 4: Load from JSON config file
def example_config_file():
    print("Example 4: Load from config file")
    
    # First, save a config
    config = BotConfig()
    config.whatsapp.monitor_contacts = ["Friend 1", "Friend 2"]
    config.ai.personality = "sarcastic but helpful"
    config.save_to_file("my_bot_config.json")
    
    # Load and use it
    bot = WhatsAppBot(config_file="my_bot_config.json")
    bot.start()

# Example 5: Context manager (auto cleanup)
def example_context_manager():
    print("Example 5: Context manager usage")
    
    with WhatsAppBot(debug=True) as bot:
        print("Bot is running...")
        bot.wait()  # Wait for bot to finish

# Example 6: Non-blocking mode
def example_non_blocking():
    print("Example 6: Non-blocking mode")
    
    bot = WhatsAppBot()
    bot.start(blocking=False)  # Runs in background
    
    print("Bot is running in background...")
    print("You can do other things here")
    
    # Later, when you want to stop
    import time
    time.sleep(60)  # Do something for 60 seconds
    bot.stop()

# Example 7: Monitor specific contacts only
def example_specific_contacts():
    print("Example 7: Monitor specific contacts only")
    
    bot = WhatsAppBot(
        monitor_contacts=[
            "Mom",
            "Dad",
            "Best Friend",
            "918812345678",  # By phone number
            "+919987654321"  # With country code
        ],
        do_not_reply=[
            "Annoying Person",
            "918888888888"
        ]
    )
    bot.start()

# Example 8: Disable AI (simple auto-reply)
def example_simple_reply():
    print("Example 8: Simple auto-reply without AI")
    
    config = BotConfig()
    config.ai.enabled = False
    config.ai.simple_reply = "I'm currently unavailable. I'll get back to you soon!"
    
    bot = WhatsAppBot(config=config)
    bot.start()

# Example 9: Custom personality
def example_custom_personality():
    print("Example 9: Custom AI personality")
    
    bot = WhatsAppBot(
        ai_enabled=True,
        personality=(
            "You are a helpful assistant with a quirky sense of humor. "
            "Use emojis occasionally and keep responses under 50 words. "
            "Be friendly but professional."
        )
    )
    bot.start()

# Example 10: Check bot status
def example_check_status():
    print("Example 10: Check bot status")
    
    bot = WhatsAppBot()
    bot.start(blocking=False)
    
    import time
    time.sleep(5)
    
    if bot.is_running():
        print("✅ Bot is running")
    else:
        print("❌ Bot is not running")
    
    bot.stop()


if __name__ == "__main__":
    # Run the example you want
    # example_basic()
    # example_custom_config()
    # example_direct_params()
    # example_config_file()
    # example_context_manager()
    # example_non_blocking()
    # example_specific_contacts()
    # example_simple_reply()
    # example_custom_personality()
    example_check_status()
