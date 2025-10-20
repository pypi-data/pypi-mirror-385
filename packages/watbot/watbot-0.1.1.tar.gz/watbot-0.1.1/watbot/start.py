"""
Quick start script for WATBOT
Just run: python start.py
"""

import sys
from watbot import WhatsAppBot, BotConfig

def main():
    print("=" * 60)
    print("🤖 WATBOT - WhatsApp Automation Bot")
    print("=" * 60)
    print()
    
    # Simple configuration prompt
    print("Quick Setup:")
    print("1. Default (monitor all contacts)")
    print("2. Custom (choose specific contacts)")
    print("3. Debug mode (see browser)")
    print()
    
    choice = input("Select option (1-3, default=1): ").strip() or "1"
    
    config = BotConfig()
    
    if choice == "2":
        print("\nEnter contacts to monitor (comma-separated):")
        print("Examples: Mom,Dad,Best Friend or 918812345678,919987654321")
        contacts = input("Contacts: ").strip()
        if contacts:
            config.whatsapp.monitor_contacts = [c.strip() for c in contacts.split(",")]
        
        do_not_reply = input("\nContacts to NEVER reply to (comma-separated, optional): ").strip()
        if do_not_reply:
            config.whatsapp.do_not_reply = [c.strip() for c in do_not_reply.split(",")]
    
    elif choice == "3":
        config.whatsapp.debug = True
        config.whatsapp.headless = False
        print("\n✅ Debug mode enabled - you'll see the browser window")
    
    # AI settings
    use_ai = input("\nUse AI for responses? (Y/n, default=Y): ").strip().lower()
    if use_ai in ['n', 'no']:
        config.ai.enabled = False
        simple_msg = input("Enter simple auto-reply message: ").strip()
        if simple_msg:
            config.ai.simple_reply = simple_msg
    else:
        personality = input("\nCustom AI personality (optional, press Enter to skip): ").strip()
        if personality:
            config.ai.personality = personality
    
    print("\n" + "=" * 60)
    print("Configuration Summary:")
    print(f"  Monitor: {config.whatsapp.monitor_contacts}")
    if config.whatsapp.do_not_reply:
        print(f"  Ignore: {config.whatsapp.do_not_reply}")
    print(f"  AI Enabled: {config.ai.enabled}")
    if config.ai.enabled and config.ai.personality != "friendly and helpful with subtle sarcasm":
        print(f"  Personality: {config.ai.personality}")
    print(f"  Debug: {config.whatsapp.debug}")
    print("=" * 60)
    print()
    
    confirm = input("Start bot with these settings? (Y/n): ").strip().lower()
    if confirm in ['n', 'no']:
        print("❌ Cancelled")
        return
    
    print("\n🚀 Starting bot...")
    print("📱 Scan QR code with WhatsApp when it appears")
    print("⏸️  Press Ctrl+C to stop\n")
    
    try:
        bot = WhatsAppBot(config=config)
        bot.start()
    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Node.js is installed")
        print("2. Run 'npm install' in the project directory")
        print("3. Check if Chrome/Chromium is installed")
        print("\nFor help: https://github.com/nithin434/woat/issues")

if __name__ == "__main__":
    main()
