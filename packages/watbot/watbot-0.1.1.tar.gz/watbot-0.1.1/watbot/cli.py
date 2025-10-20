"""
Command-line interface for WATBOT
"""

import argparse
import sys
import json
from pathlib import Path
from .whatsapp_bot import WhatsAppBot
from .config import BotConfig


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="WATBOT - WhatsApp & Instagram Automation Bot with AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start with defaults
  watbot start
  
  # Start with custom config file
  watbot start --config my_config.json
  
  # Start with specific contacts
  watbot start --monitor "John Doe" "918812345678" --debug
  
  # Start without AI (simple auto-reply)
  watbot start --no-ai --reply "I'm busy, will reply later"
  
  # Generate config file
  watbot config --output my_config.json
  
For more info: https://github.com/nithin434/woat
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start the WhatsApp bot")
    start_parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to JSON config file"
    )
    start_parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Enable debug mode"
    )
    start_parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Show browser window (disable headless mode)"
    )
    start_parser.add_argument(
        "--monitor", "-m",
        nargs="+",
        help="Contacts to monitor (names or numbers)"
    )
    start_parser.add_argument(
        "--do-not-reply",
        nargs="+",
        help="Contacts to never reply to"
    )
    start_parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Disable AI responses (use simple auto-reply)"
    )
    start_parser.add_argument(
        "--reply",
        type=str,
        help="Simple auto-reply message (when AI is disabled)"
    )
    start_parser.add_argument(
        "--personality", "-p",
        type=str,
        help="AI personality description"
    )
    start_parser.add_argument(
        "--session", "-s",
        type=str,
        default="default",
        help="Session ID for WhatsApp"
    )
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Generate config file")
    config_parser.add_argument(
        "--output", "-o",
        type=str,
        default="watbot_config.json",
        help="Output file path"
    )
    config_parser.add_argument(
        "--template",
        action="store_true",
        help="Generate template with all options"
    )
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show version")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "version":
        from . import __version__
        print(f"WATBOT version {__version__}")
        sys.exit(0)
    
    elif args.command == "config":
        generate_config(args)
    
    elif args.command == "start":
        start_bot(args)


def generate_config(args):
    """Generate config file"""
    config = BotConfig()
    
    if args.template:
        # Add comments to template
        config_dict = config.to_dict()
        config_dict["_comments"] = {
            "monitor_contacts": "List of contacts to monitor. Use ['ALL'] for everyone",
            "do_not_reply": "List of contacts to never reply to",
            "session_id": "WhatsApp session identifier",
            "headless": "Run browser in headless mode (true/false)",
            "debug": "Enable debug logging (true/false)",
            "ai.enabled": "Enable AI responses (true/false)",
            "ai.personality": "AI personality description",
            "ai.context_limit": "Number of recent messages to include for context"
        }
    else:
        config_dict = config.to_dict()
    
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, indent=2)
    
    print(f"✅ Config file generated: {output_path}")
    print(f"📝 Edit the file and use: watbot start --config {output_path}")


def start_bot(args):
    """Start the bot"""
    try:
        # Load config from file if provided
        if args.config:
            config = BotConfig.from_file(args.config)
        else:
            config = BotConfig()
        
        # Override with command-line arguments
        if args.debug:
            config.whatsapp.debug = True
        
        if args.no_headless:
            config.whatsapp.headless = False
        
        if args.monitor:
            config.whatsapp.monitor_contacts = args.monitor
        
        if args.do_not_reply:
            config.whatsapp.do_not_reply = args.do_not_reply
        
        if args.no_ai:
            config.ai.enabled = False
        
        if args.reply:
            config.ai.simple_reply = args.reply
        
        if args.personality:
            config.ai.personality = args.personality
        
        if args.session:
            config.whatsapp.session_id = args.session
        
        # Start bot
        print("🚀 Starting WATBOT...")
        bot = WhatsAppBot(config=config)
        bot.start(blocking=True)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
