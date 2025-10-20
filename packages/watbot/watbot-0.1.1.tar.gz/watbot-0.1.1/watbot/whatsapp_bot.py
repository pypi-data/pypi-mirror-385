"""
WhatsApp Bot wrapper for Node.js implementation
"""

import subprocess
import sys
import os
import signal
import time
import logging
from pathlib import Path
from typing import Optional, List, Callable, Dict, Any
from .config import BotConfig, WhatsAppConfig, AIConfig


class WhatsAppBot:
    """
    WhatsApp Bot with AI-powered responses
    
    Example:
        >>> from watbot import WhatsAppBot, BotConfig
        >>> 
        >>> # Simple usage with defaults
        >>> bot = WhatsAppBot()
        >>> bot.start()
        >>> 
        >>> # Advanced usage with custom config
        >>> config = BotConfig()
        >>> config.whatsapp.debug = True
        >>> config.whatsapp.headless = False
        >>> config.whatsapp.monitor_contacts = ["John Doe", "918812345678"]
        >>> config.ai.personality = "professional and concise"
        >>> 
        >>> bot = WhatsAppBot(config=config)
        >>> bot.start()
    """
    
    def __init__(
        self,
        config: Optional[BotConfig] = None,
        config_file: Optional[str] = None,
        debug: bool = False,
        headless: bool = True,
        monitor_contacts: Optional[List[str]] = None,
        do_not_reply: Optional[List[str]] = None,
        ai_enabled: bool = True,
        personality: Optional[str] = None,
        session_id: str = "default",
    ):
        """
        Initialize WhatsApp Bot
        
        Args:
            config: BotConfig object with all settings
            config_file: Path to JSON config file
            debug: Enable debug mode (shows browser window and logs)
            headless: Run browser in headless mode
            monitor_contacts: List of contacts to monitor (use ["ALL"] for everyone)
            do_not_reply: List of contacts to never reply to
            ai_enabled: Enable AI responses
            personality: AI personality description
            session_id: WhatsApp session identifier
        """
        self.logger = self._setup_logger(debug)
        
        # Load config
        if config:
            self.config = config
        elif config_file:
            self.config = BotConfig.from_file(config_file)
        else:
            self.config = BotConfig()
        
        # Override with direct parameters
        if debug is not None:
            self.config.whatsapp.debug = debug
        if headless is not None:
            self.config.whatsapp.headless = headless
        if monitor_contacts is not None:
            self.config.whatsapp.monitor_contacts = monitor_contacts
        if do_not_reply is not None:
            self.config.whatsapp.do_not_reply = do_not_reply
        if ai_enabled is not None:
            self.config.ai.enabled = ai_enabled
        if personality is not None:
            self.config.ai.personality = personality
        if session_id is not None:
            self.config.whatsapp.session_id = session_id
        
        self.process: Optional[subprocess.Popen] = None
        self.running = False
        
        # Find Node.js script
        self.script_dir = Path(__file__).parent.parent
        self.node_script = self.script_dir / "smart_whatsapp_bot.js"
        
        if not self.node_script.exists():
            raise FileNotFoundError(
                f"Node.js script not found at {self.node_script}. "
                "Make sure smart_whatsapp_bot.js is in the same directory as the watbot package."
            )
        
        self.logger.info("WhatsApp Bot initialized")
        self.logger.debug(f"Config: {self.config.to_dict()}")
    
    def _setup_logger(self, debug: bool) -> logging.Logger:
        """Setup logger with appropriate level"""
        logger = logging.getLogger("watbot.whatsapp")
        logger.setLevel(logging.DEBUG if debug else logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def start(self, blocking: bool = True):
        """
        Start the WhatsApp bot
        
        Args:
            blocking: If True, blocks until bot is stopped. If False, runs in background.
        """
        if self.running:
            self.logger.warning("Bot is already running")
            return
        
        self.logger.info("Starting WhatsApp Bot...")
        
        # Get environment variables
        env = self.config.get_env_dict()
        
        # Check for Node.js
        try:
            subprocess.run(
                ["node", "--version"],
                capture_output=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "Node.js not found. Please install Node.js from https://nodejs.org/"
            )
        
        # Check for npm packages
        self._check_npm_packages()
        
        # Start Node.js process
        self.logger.debug(f"Starting Node.js script: {self.node_script}")
        
        try:
            self.process = subprocess.Popen(
                ["node", str(self.node_script)],
                env=env,
                cwd=str(self.script_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.running = True
            self.logger.info("✅ WhatsApp Bot started successfully")
            
            if blocking:
                self._stream_output()
            else:
                # Start output streaming in background
                import threading
                thread = threading.Thread(target=self._stream_output, daemon=True)
                thread.start()
                
        except Exception as e:
            self.logger.error(f"Failed to start bot: {e}")
            raise
    
    def _stream_output(self):
        """Stream output from Node.js process"""
        if not self.process or not self.process.stdout:
            return
        
        try:
            for line in self.process.stdout:
                line = line.strip()
                if line:
                    if self.config.whatsapp.debug:
                        self.logger.debug(line)
                    else:
                        # Filter important messages
                        if any(marker in line for marker in ['✅', '❌', '🤖', '📥', '📤', '⚠️']):
                            self.logger.info(line)
                        
        except Exception as e:
            self.logger.error(f"Error streaming output: {e}")
    
    def _check_npm_packages(self):
        """Check if required npm packages are installed"""
        package_json = self.script_dir / "package.json"
        
        if not package_json.exists():
            self.logger.warning("package.json not found, skipping npm check")
            return
        
        node_modules = self.script_dir / "node_modules"
        if not node_modules.exists():
            self.logger.info("Installing npm packages...")
            try:
                subprocess.run(
                    ["npm", "install"],
                    cwd=str(self.script_dir),
                    check=True,
                    capture_output=True
                )
                self.logger.info("✅ npm packages installed")
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to install npm packages: {e}")
                raise
    
    def stop(self):
        """Stop the WhatsApp bot"""
        if not self.running or not self.process:
            self.logger.warning("Bot is not running")
            return
        
        self.logger.info("Stopping WhatsApp Bot...")
        
        try:
            # Send SIGTERM for graceful shutdown
            self.process.terminate()
            
            # Wait up to 10 seconds for graceful shutdown
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.logger.warning("Graceful shutdown timed out, forcing stop...")
                self.process.kill()
                self.process.wait()
            
            self.running = False
            self.process = None
            self.logger.info("✅ WhatsApp Bot stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping bot: {e}")
            raise
    
    def restart(self):
        """Restart the WhatsApp bot"""
        self.logger.info("Restarting WhatsApp Bot...")
        self.stop()
        time.sleep(2)
        self.start(blocking=False)
    
    def is_running(self) -> bool:
        """Check if bot is running"""
        if not self.process:
            return False
        return self.process.poll() is None
    
    def wait(self):
        """Wait for bot to finish (blocking)"""
        if self.process:
            self.process.wait()
    
    def __enter__(self):
        """Context manager entry"""
        self.start(blocking=False)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
    
    def __del__(self):
        """Cleanup on deletion"""
        if self.running:
            self.stop()
