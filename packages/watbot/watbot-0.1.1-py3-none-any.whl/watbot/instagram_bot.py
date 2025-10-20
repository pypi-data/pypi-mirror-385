from typing import Optional, Set, Dict, Any, List
import logging
import json
import time
import os
import random
import hashlib
from collections import deque
from playwright.sync_api import sync_playwright, Page, Browser, Playwright, Response
from .config import InstagramConfig, AIConfig

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InstagramBot:
    """Instagram Bot using Playwright for automation"""
    
    def __init__(
        self,
        config: InstagramConfig,
        ai_config: Optional[AIConfig] = None
    ):
        """Initialize Instagram Bot with configuration"""
        self.config = config
        self.ai_config = ai_config or AIConfig()
        
        # Playwright components
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.context = None
        
        # State tracking
        self.is_running = False
        self.processed_messages: Set[str] = set()
        self.sent_initial_response: Set[str] = set()
        self.conversation_states: Dict[str, float] = {}
        self.monitoring_start_time: Dict[str, float] = {}
        self.last_responded_message: Dict[str, str] = {}
        self.monitored_users: Set[str] = set()
        self.bot_messages: Set[str] = set()
        self.current_conversation_id: Optional[str] = None
        self.log_buffer = deque(maxlen=500)
        
        # Persistence
        self.message_tracking_file = "message_tracking.json"
        self.session_dir = os.path.join(os.path.dirname(__file__), "sessions")
        self._load_message_tracking()
        
        # Configure logging
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Set up logging configuration"""
        if self.config.debug:
            logging.getLogger().setLevel(logging.DEBUG)
            
        class LogHandler(logging.Handler):
            def __init__(self, bot):
                super().__init__()
                self.bot = bot
                
            def emit(self, record):
                log_entry = self.format(record)
                self.bot.log_buffer.append(log_entry)
                
        log_handler = LogHandler(self)
        log_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        logging.getLogger().addHandler(log_handler)

    def _load_message_tracking(self) -> None:
        """Load message tracking data from file"""
        try:
            if os.path.exists(self.message_tracking_file):
                with open(self.message_tracking_file, 'r') as f:
                    data = json.load(f)
                    self.processed_messages = set(data.get('processed_messages', []))
                    self.conversation_states = data.get('conversation_states', {})
                    self.sent_initial_response = set(data.get('sent_initial_response', []))
                    self.last_responded_message = data.get('last_responded_message', {})
                    self.bot_messages = set(data.get('bot_messages', []))
                    logging.info(f"Loaded {len(self.processed_messages)} processed messages")
        except Exception as e:
            logging.error(f"Failed to load message tracking: {e}")

    def _save_message_tracking(self) -> None:
        """Save message tracking data to file"""
        try:
            data = {
                'processed_messages': list(self.processed_messages),
                'conversation_states': self.conversation_states,
                'sent_initial_response': list(self.sent_initial_response),
                'last_responded_message': self.last_responded_message,
                'bot_messages': list(self.bot_messages)
            }
            with open(self.message_tracking_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logging.error(f"Failed to save message tracking: {e}")

    def setup_browser(self) -> bool:
        """Set up Playwright browser for Instagram automation"""
        try:
            if not os.path.exists(self.session_dir):
                os.makedirs(self.session_dir)

            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=self.config.headless,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )

            self.context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                viewport={'width': 1366, 'height': 768}
            )
            
            # Load session if exists
            session_file = os.path.join(self.session_dir, f"{self.config.session_id}.json")
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    storage = json.load(f)
                    self.context.add_cookies(storage.get('cookies', []))

            self.page = self.context.new_page()
            return True
            
        except Exception as e:
            logging.error(f"Failed to setup browser: {e}")
            return False

    def save_session(self) -> None:
        """Save browser session to file"""
        try:
            session_file = os.path.join(self.session_dir, f"{self.config.session_id}.json")
            cookies = self.context.cookies() if self.context else []
            storage = {'cookies': cookies}
            with open(session_file, 'w') as f:
                json.dump(storage, f)
        except Exception as e:
            logging.error(f"Failed to save session: {e}")

    def start(self) -> bool:
        """Start the Instagram bot"""
        if self.is_running:
            logging.warning("Bot is already running")
            return False
            
        try:
            if not self.setup_browser():
                return False
                
            # Navigate to Instagram
            self.page.goto('https://www.instagram.com')
            
            # Login if needed
            if not self._is_logged_in():
                self._login()
                
            self.is_running = True
            
            # Start monitoring messages
            self._monitor_messages()
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to start Instagram bot: {e}")
            self.stop()
            return False

    def stop(self) -> None:
        """Stop the Instagram bot and clean up resources"""
        self.is_running = False
        
        # Save state before stopping
        self._save_message_tracking()
        
        if self.page:
            self.page.close()
            
        if self.context:
            if self.config.session_upload_enabled:
                self.save_session()
            self.context.close()
            
        if self.browser:
            self.browser.close()
            
        if self.playwright:
            self.playwright.stop()

        logging.info("Instagram bot stopped")

    def _add_human_delay(self) -> None:
        """Add random delay to simulate human behavior"""
        time.sleep(random.uniform(1, 3))

    def _is_logged_in(self) -> bool:
        """Check if currently logged into Instagram"""
        try:
            return bool(self.page.query_selector('nav a[href*="/profile"]'))
        except Exception:
            return False

    def _login(self) -> None:
        """Login to Instagram using provided credentials"""
        if not self.config.username or not self.config.password:
            raise ValueError("Instagram username and password required")
            
        try:
            # Fill login form
            self.page.fill('input[name="username"]', self.config.username)
            self.page.fill('input[name="password"]', self.config.password)
            self._add_human_delay()
            self.page.click('button[type="submit"]')
            
            # Wait for successful login
            self.page.wait_for_selector('nav a[href*="/profile"]')
            logging.info("Successfully logged into Instagram")
            
        except Exception as e:
            logging.error(f"Failed to login to Instagram: {e}")
            raise

    def send_message(self, username: str, message: str) -> bool:
        """Send a direct message to a user"""
        if not self.is_running:
            raise RuntimeError("Bot must be started first")
            
        try:
            # Navigate to DM compose
            self.page.click('a[href="/direct/inbox/"]')
            self._add_human_delay()
            self.page.click('button[aria-label="New message"]')
            
            # Search for user
            self.page.fill('input[placeholder="Search..."]', username)
            self._add_human_delay()
            
            # Click on user
            user_btn = self.page.query_selector(f'button[aria-label*="{username}"]')
            if not user_btn:
                logging.error(f"Could not find user {username}")
                return False
                
            user_btn.click()
            self._add_human_delay()
            
            # Click next
            self.page.click('button[aria-label="Next"]')
            self._add_human_delay()
            
            # Send message
            self.page.fill('textarea[placeholder="Message..."]', message)
            self.page.press('textarea', 'Enter')
            
            message_id = self._generate_message_id(message)
            self.bot_messages.add(message_id)
            self._save_message_tracking()
            
            logging.info(f"Sent message to {username}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send message to {username}: {e}")
            return False

    def _generate_message_id(self, message: str) -> str:
        """Generate unique ID for message"""
        text = message.strip().lower()
        timestamp = int(time.time())
        return hashlib.md5(f"{text}:{timestamp}".encode()).hexdigest()

    def _monitor_messages(self) -> None:
        """Monitor direct messages and respond"""
        logging.info("Starting message monitoring")
        
        while self.is_running:
            try:
                self._check_messages()
                time.sleep(5)
            except Exception as e:
                logging.error(f"Error monitoring messages: {e}")
                time.sleep(30)

    def _check_messages(self) -> None:
        """Check for new messages in monitored conversations"""
        try:
            # Navigate to inbox
            if "/direct/inbox/" not in self.page.url:
                self.page.goto("https://www.instagram.com/direct/inbox/")
            
            # Get unread conversations
            unread_threads = self.page.query_selector_all('div[aria-label*="unread"]')
            
            for thread in unread_threads:
                try:
                    # Get thread info
                    sender = thread.query_selector('a[role="link"]').inner_text()
                    
                    # Skip if not monitoring this user
                    if ("ALL" not in self.config.monitor_profiles and 
                        sender not in self.config.monitor_profiles):
                        continue
                        
                    # Skip if in do not reply list
                    if sender in self.config.do_not_reply:
                        continue
                        
                    # Open conversation
                    thread.click()
                    self._add_human_delay()
                    
                    # Process messages
                    messages = self.page.query_selector_all('div[role="listitem"]')
                    
                    for msg in messages:
                        message_id = self._generate_message_id(
                            msg.inner_text()
                        )
                        
                        if message_id not in self.processed_messages:
                            self._process_message(msg, sender)
                            self.processed_messages.add(message_id)
                            self._save_message_tracking()
                            
                except Exception as e:
                    logging.error(f"Error processing thread: {e}")
                    continue
                    
        except Exception as e:
            logging.error(f"Error checking messages: {e}")

    def _process_message(self, message_elem, sender: str) -> None:
        """Process a message and generate response"""
        try:
            # Get message content
            content = message_elem.query_selector('span[dir="auto"]').inner_text()
            
            # Track conversation state
            self.conversation_states[sender] = time.time()
            
            # Send initial response
            if (sender not in self.sent_initial_response and 
                self.ai_config.introduction):
                if self.send_message(sender, self.ai_config.introduction):
                    self.sent_initial_response.add(sender)
                    self._save_message_tracking()
            
            # Generate and send AI response
            if self.ai_config.enabled:
                response = self._generate_ai_response(content, sender)
                if response and self.send_message(sender, response):
                    self.last_responded_message[sender] = content
                    self._save_message_tracking()
                    
        except Exception as e:
            logging.error(f"Error processing message: {e}")

    def _generate_ai_response(self, message: str, sender: str) -> Optional[str]:
        """Generate AI response to message"""
        try:
            # Build conversation context
            context = self._build_conversation_context(sender)
            
            # Use configured AI provider
            if self.ai_config.gemini_api_key:
                response = self._generate_gemini_response(message, context)
            elif self.ai_config.openrouter_api_key:
                response = self._generate_openrouter_response(message, context)
            else:
                response = self.ai_config.simple_reply
                
            return response
            
        except Exception as e:
            logging.error(f"Error generating AI response: {e}")
            return None

    def _build_conversation_context(self, sender: str) -> str:
        """Build context for AI conversation"""
        context = []
        
        # Add personality
        if self.ai_config.personality:
            context.append(f"Personality: {self.ai_config.personality}")
        
        # Add conversation history
        if sender in self.last_responded_message:
            context.append(
                f"Last message: {self.last_responded_message[sender]}"
            )
            
        return "\n".join(context)

    def _generate_gemini_response(self, message: str, context: str) -> Optional[str]:
        """Generate response using Google Gemini"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.ai_config.gemini_api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"{context}\nMessage: {message}\nResponse:"
            response = model.generate_content(prompt)
            
            return response.text
            
        except Exception as e:
            logging.error(f"Error generating Gemini response: {e}")
            return None

    def _generate_openrouter_response(self, message: str, context: str) -> Optional[str]:
        """Generate response using OpenRouter API"""
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {self.ai_config.openrouter_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {"role": "system", "content": context},
                    {"role": "user", "content": message}
                ]
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            return response.json()['choices'][0]['message']['content']
            
        except Exception as e:
            logging.error(f"Error generating OpenRouter response: {e}")
            return None

    def get_log_buffer(self) -> List[str]:
        """Get contents of log buffer"""
        return list(self.log_buffer)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InstagramBot:
    """Instagram Bot using Playwright for automation"""
    
    def __init__(
        self,
        config: InstagramConfig,
        ai_config: Optional[AIConfig] = None
    ):
        """Initialize Instagram Bot with configuration"""
        self.config = config
        self.ai_config = ai_config or AIConfig()
        
        # Playwright components
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
        # State tracking
        self.is_running = False
        self.processed_messages: Set[str] = set()
        self.sent_initial_response: Set[str] = set()
        self.conversation_states: Dict[str, float] = {}
        self.monitoring_start_time: Dict[str, float] = {}
        self.last_responded_message: Dict[str, str] = {}
        self.log_buffer = deque(maxlen=500)
        
        # Persistence
        self.message_tracking_file = "message_tracking.json"
        self._load_message_tracking()
        
        # Configure logging
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Set up logging configuration"""
        if self.config.debug:
            logging.getLogger().setLevel(logging.DEBUG)
            
        class LogHandler(logging.Handler):
            def __init__(self, bot):
                super().__init__()
                self.bot = bot
                
            def emit(self, record):
                log_entry = self.format(record)
                self.bot.log_buffer.append(log_entry)
                
        log_handler = LogHandler(self)
        log_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        logging.getLogger().addHandler(log_handler)

    def _load_message_tracking(self) -> None:
        """Load message tracking data from file."""
        try:
            if os.path.exists(self.message_tracking_file):
                with open(self.message_tracking_file, 'r') as f:
                    data = json.load(f)
                    self.processed_messages = set(data.get('processed_messages', []))
                    self.conversation_states = data.get('conversation_states', {})
                    self.sent_initial_response = set(data.get('sent_initial_response', []))
                    self.last_responded_message = data.get('last_responded_message', {})
                    logging.info(f"Loaded {len(self.processed_messages)} processed messages")
        except Exception as e:
            logging.error(f"Failed to load message tracking: {e}")

    def _save_message_tracking(self) -> None:
        """Save message tracking data to file."""
        try:
            data = {
                'processed_messages': list(self.processed_messages),
                'conversation_states': self.conversation_states,
                'sent_initial_response': list(self.sent_initial_response),
                'last_responded_message': self.last_responded_message
            }
            with open(self.message_tracking_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logging.error(f"Failed to save message tracking: {e}")

    async def start(self) -> bool:
        """Start the Instagram bot using cookie-based auth"""
        if self.is_running:
            logging.warning("Bot is already running")
            return False
            
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.firefox.launch(headless=self.config.headless)
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            
            # Navigate to Instagram
            self.page.goto('https://www.instagram.com')
            
            # Ensure logged in with cookies
            if not await self._ensure_logged_in():
                raise RuntimeError("Cookie-based authentication failed")
            
            self.is_running = True
            logging.info("Instagram bot started successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to start Instagram bot: {e}")
            self.stop()
            return False

    def stop(self) -> None:
        """Stop the Instagram bot and clean up resources"""
        try:
            self.is_running = False
            
            # Save message tracking
            self._save_message_tracking()
            
            # Save and backup session cookies
            if self.context and self.config.session_upload_enabled:
                cookies = self.context.cookies()
                self.config.save_cookies(cookies)  # This also handles remote backup
                
            # Cleanup resources
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
                
            logging.info("Instagram bot stopped and session backed up")
            
        except Exception as e:
            logging.error(f"Error during bot shutdown: {e}")
        finally:
            self.page = None
            self.context = None
            self.browser = None
            self.playwright = None

    def _is_logged_in(self) -> bool:
        """Check if currently logged into Instagram"""
        try:
            # Check for login state by looking for profile icon
            return bool(self.page.query_selector('nav a[href*="/profile"]'))
        except Exception:
            return False

    async def _ensure_logged_in(self) -> bool:
        """Check and ensure logged in state using cookies"""
        try:
            # Load and apply cookies
            cookies = self.config.load_cookies()
            if not cookies:
                logging.error("No cookies available - login required")
                return False
                
            # Apply cookies
            self.context.add_cookies(cookies)
            self.page.reload()
            
            # Verify login state
            logged_in = bool(self.page.query_selector('nav a[href*="/profile"]'))
            if logged_in:
                logging.info("Successfully logged in with cookies")
            else:
                logging.error("Cookie-based login failed")
                
            return logged_in
            
        except Exception as e:
            logging.error(f"Error ensuring login state: {e}")
            return False

    async def send_message(self, username: str, message: str) -> None:
        """Send a DM to specified Instagram user"""
        if not self.is_running:
            raise RuntimeError("Bot must be started first")
            
        try:
            # Navigate to DM compose
            self.page.click('a[href="/direct/inbox/"]')
            self.page.click('button[aria-label="New message"]')
            
            # Search and select recipient
            self.page.fill('input[placeholder="Search..."]', username)
            self.page.click(f'button[aria-label*="{username}"]')
            self.page.click('button[aria-label="Next"]')
            
            # Send message
            self.page.fill('textarea[placeholder="Message..."]', message)
            self.page.press('textarea', 'Enter')
            
            logging.info(f"Sent message to {username}")
            
        except Exception as e:
            logging.error(f"Failed to send message to {username}: {e}")
            raise

    async def monitor_messages(self) -> None:
        """Monitor DMs for new messages and respond using AI"""
        if not self.is_running:
            raise RuntimeError("Bot must be started first")
            
        logging.info("Starting message monitoring")
        while self.is_running:
            try:
                await self._check_messages()
                time.sleep(5)  # Avoid excessive polling
                
            except Exception as e:
                logging.error(f"Error monitoring messages: {e}")
                time.sleep(30)  # Back off on error

    async def _check_messages(self) -> None:
        """Check for and process new messages"""
        # Navigate to inbox if needed
        if "/direct/inbox/" not in self.page.url:
            self.page.goto('https://www.instagram.com/direct/inbox/')
            
        # Get unread message threads
        threads = self.page.query_selector_all(
            'div[aria-label*="unread"]'
        )
        
        for thread in threads:
            try:
                thread.click()
                
                # Get sender username
                sender = thread.query_selector('a[role="link"]').inner_text()
                
                # Skip if not in monitored profiles
                if ("ALL" not in self.config.monitor_profiles and 
                    sender not in self.config.monitor_profiles):
                    continue
                
                # Skip if in do-not-reply list
                if sender in self.config.do_not_reply:
                    continue
                    
                # Get latest messages
                messages = self.page.query_selector_all(
                    'div[role="listitem"]'
                )
                
                for msg in messages:
                    # Process only new messages
                    msg_id = self._get_message_id(msg)
                    if msg_id not in self.processed_messages:
                        await self._process_message(msg, sender)
                        self.processed_messages.add(msg_id)
                        
            except Exception as e:
                logging.error(f"Error processing thread: {e}")

    def _get_message_id(self, message_elem) -> str:
        """Generate unique ID for message to avoid duplicates"""
        try:
            content = message_elem.inner_text()
            timestamp = message_elem.get_attribute('data-timestamp')
            return hashlib.md5(f"{content}{timestamp}".encode()).hexdigest()
        except Exception as e:
            # Fallback to content hash only
            logging.warning(f"Using fallback message ID generation: {e}")
            return hashlib.md5(message_elem.inner_text().encode()).hexdigest()

    async def _process_message(self, message_elem, sender: str) -> None:
        """Process a single message and generate AI response if needed"""
        try:
            # Get message content
            content = message_elem.query_selector('span[dir="auto"]').inner_text()
            
            # Track conversation state
            self.conversation_states[sender] = time.time()
            
            # Send initial response if needed
            if sender not in self.sent_initial_response and self.ai_config.introduction:
                await self.send_message(sender, self.ai_config.introduction)
                self.sent_initial_response.add(sender)
                
            # Generate and send AI response
            if self.ai_config.enabled:
                response = await self._generate_ai_response(content, sender)
                if response:
                    await self.send_message(sender, response)
                    
        except Exception as e:
            logging.error(f"Error processing message from {sender}: {e}")

    async def _generate_ai_response(self, message: str, sender: str) -> Optional[str]:
        """Generate AI response to message using configured provider"""
        try:
            # Build conversation context
            context = self._build_conversation_context(sender)
            
            # Use Gemini API if configured
            if self.ai_config.gemini_api_key:
                response = await self._generate_gemini_response(message, context)
                
            # Use OpenRouter API if configured  
            elif self.ai_config.openrouter_api_key:
                response = await self._generate_openrouter_response(message, context)
                
            # Fallback to simple reply
            else:
                response = self.ai_config.simple_reply
                
            # Track response
            if response:
                self.last_responded_message[sender] = message
                
            return response
            
        except Exception as e:
            logging.error(f"Failed to generate AI response: {e}")
            return self.ai_config.simple_reply

    def _build_conversation_context(self, sender: str) -> str:
        """Build conversation context for AI response"""
        context = []
        
        # Add personality context
        context.append(f"You are replying as: {self.ai_config.personality}")
        
        # Add conversation history context
        if sender in self.last_responded_message:
            context.append(
                f"Their last message: {self.last_responded_message[sender]}"
            )
            
        # Join context sections
        return "\n".join(context)

    async def _generate_gemini_response(self, message: str, context: str) -> Optional[str]:
        """Generate response using Google Gemini API"""
        import google.generativeai as genai
        
        try:
            genai.configure(api_key=self.ai_config.gemini_api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"{context}\n\nMessage: {message}\n\nResponse:"
            response = model.generate_content(prompt)
            
            return response.text
            
        except Exception as e:
            logging.error(f"Failed to generate Gemini response: {e}")
            return None

    async def _generate_openrouter_response(self, message: str, context: str) -> Optional[str]:
        """Generate response using OpenRouter API"""
        import requests
        
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.ai_config.openrouter_api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {"role": "system", "content": context},
                    {"role": "user", "content": message}
                ]
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            logging.error(f"Failed to generate OpenRouter response: {e}")
            return None

    def get_log_buffer(self) -> list:
        """Get current contents of log buffer"""
        return list(self.log_buffer)
        # except Exception as e:
        #     logging.warning(f"Could not load message tracking: {e}")

    def save_message_tracking(self) -> None:
        """Save message tracking data to file."""
        try:
            data = {
                'processed_messages': list(self.processed_messages),
                'bot_messages': list(self.bot_messages),
                'conversation_states': self.conversation_states,
                'sent_initial_response': list(self.sent_initial_response),
                'last_responded_message': self.last_responded_message
            }
            with open(self.message_tracking_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save message tracking: {e}")

    def generate_message_id(self, text: str, conversation_id: str, element_position: Optional[int] = None) -> str:
        """Generate unique ID for a message."""
        try:
            text_clean = text.strip().lower()
            base_string = f"{conversation_id}:{text_clean}"
            if element_position is not None:
                base_string += f":{element_position}"
            return hashlib.md5(base_string.encode()).hexdigest()[:16]
        except Exception as e:
            logging.debug(f"Error generating message ID: {e}")
            return f"{conversation_id}_{hash(text)}_{int(time.time())}"

    def setup_headless_browser(self) -> bool:
        """Set up Playwright browser for Instagram automation."""
        try:
            if self.playwright:
                try:
                    self.playwright.stop()
                except:
                    pass

            if not os.path.exists(self.session_dir):
                os.makedirs(self.session_dir)

            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=True if self.config.headless else False,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-extensions-except',
                    '--disable-plugins-discovery',
                    '--no-first-run',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection',
                    '--window-size=1366,768'
                ]
            )

            self.context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1366, 'height': 768},
                locale='en-US',
                timezone_id='America/New_York',
                storage_state=os.path.join(self.session_dir, 'session.json') if os.path.exists(os.path.join(self.session_dir, 'session.json')) else None
            )
            self.page = self.context.new_page()
            logging.info("Browser setup successfully with session storage")
            return True
        except Exception as e:
            logging.error(f"Failed to setup browser: {e}")
            return False

    def save_session(self) -> None:
        """Save browser session to file."""
        try:
            session_file = os.path.join(self.session_dir, 'session.json')
            storage_state = self.context.storage_state()
            with open(session_file, 'w') as f:
                json.dump(storage_state, f)
        except Exception as e:
            logging.error(f"Failed to save session: {e}")

    def add_human_delays(self) -> None:
        """Add random delays to simulate human behavior."""
        delay = random.uniform(1, 3)
        time.sleep(delay)

    def load_cookies_from_json(self, json_file_path: str) -> bool:
        """Load cookies from JSON file for authentication."""
        try:
            if not self.page:
                if not self.setup_headless_browser():
                    return False

            logging.info("Navigating to Instagram...")
            self.page.goto("https://www.instagram.com", wait_until='networkidle', timeout=60000)
            self.add_human_delays()

            with open(json_file_path, 'r') as f:
                cookies_data = json.load(f)

            playwright_cookies = self._convert_cookies(cookies_data)
            if not playwright_cookies:
                logging.error("No valid cookies to add")
                return False

            self.context.add_cookies(playwright_cookies)
            
            logging.info("Refreshing page...")
            try:
                self.page.reload(wait_until='domcontentloaded', timeout=60000)
                time.sleep(3)
                logging.info("Page refreshed successfully - cookies applied")
                self.save_session()
            except Exception as refresh_error:
                logging.warning(f"Page refresh had issues but continuing: {refresh_error}")

            return True
        except Exception as e:
            logging.error(f"Error loading cookies: {e}")
            return False

    def _convert_cookies(self, cookies_data: list) -> list:
        """Convert cookies to Playwright format."""
        playwright_cookies = []
        same_site_mapping = {
            'no_restriction': 'None',
            'lax': 'Lax',
            'strict': 'Strict',
            'unspecified': 'Lax'
        }

        for cookie in cookies_data:
            try:
                playwright_cookie = {
                    'name': cookie['name'],
                    'value': cookie['value'],
                    'domain': cookie['domain'],
                    'path': cookie.get('path', '/'),
                    'secure': cookie.get('secure', True),
                    'httpOnly': cookie.get('httpOnly', False)
                }

                raw_same_site = cookie.get('sameSite', 'Lax')
                if isinstance(raw_same_site, str):
                    raw_same_site = raw_same_site.lower()
                playwright_cookie['sameSite'] = same_site_mapping.get(raw_same_site, 'Lax')

                if 'expirationDate' in cookie and cookie['expirationDate']:
                    try:
                        expiry_timestamp = float(cookie['expirationDate'])
                        if expiry_timestamp > time.time():
                            playwright_cookie['expires'] = int(expiry_timestamp)
                    except (ValueError, TypeError):
                        logging.warning(f"Invalid expiry date for cookie {cookie['name']}")

                playwright_cookies.append(playwright_cookie)
            except Exception as cookie_error:
                logging.warning(f"Failed to convert cookie {cookie.get('name', 'unknown')}: {cookie_error}")

        return playwright_cookies

    def navigate_to_direct_inbox(self) -> bool:
        """Navigate to Instagram direct messages inbox."""
        try:
            inbox_url = "https://www.instagram.com/direct/inbox/"
            logging.info(f"Navigating to inbox: {inbox_url}")
            self.page.goto(inbox_url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(5)

            inbox_indicators = [
                'div[role="grid"]',
                '[aria-label*="conversation"]',
                '[data-testid*="conversation"]',
                'div[aria-label*="Direct"]'
            ]

            for indicator in inbox_indicators:
                try:
                    element = self.page.wait_for_selector(indicator, timeout=5000)
                    if element:
                        logging.info("Successfully navigated to direct inbox")
                        return True
                except:
                    continue

            logging.warning("Could not confirm inbox navigation, but continuing")
            return True
        except Exception as e:
            logging.error(f"Error navigating to inbox: {e}")
            return False

    def get_conversations_from_inbox(self) -> list:
        """Get list of available conversations from inbox."""
        if not self.navigate_to_direct_inbox():
            return []

        time.sleep(3)
        conversations = []
        conversation_selectors = [
            'div[role="grid"] > div',
            '[role="listitem"]',
            'div[data-testid*="conversation"]',
            'a[href*="/direct/t/"]'
        ]

        for selector in conversation_selectors:
            try:
                conv_elements = self.page.query_selector_all(selector)
                if not conv_elements:
                    continue

                logging.info(f"Found {len(conv_elements)} conversation elements")
                for element in conv_elements:
                    try:
                        href = element.get_attribute('href')
                        if href and '/direct/t/' in href:
                            conv_id = href.split('/direct/t/')[-1].rstrip('/')
                            conv_text = element.text_content() or ""
                            conversations.append({
                                'id': conv_id,
                                'text': conv_text,
                                'element': element
                            })
                        else:
                            conv_text = element.text_content() or ""
                            if len(conv_text.strip()) > 0:
                                links = element.query_selector_all('a[href*="/direct/t/"]')
                                if links:
                                    href = links[0].get_attribute('href')
                                    if href:
                                        conv_id = href.split('/direct/t/')[-1].rstrip('/')
                                        conversations.append({
                                            'id': conv_id,
                                            'text': conv_text,
                                            'element': element
                                        })
                    except Exception as conv_error:
                        logging.debug(f"Error parsing conversation element: {conv_error}")
                        continue

                if conversations:
                    break
            except Exception as e:
                logging.debug(f"Conversation selector {selector} failed: {e}")
                continue

        # Remove duplicates
        unique_conversations = {conv['id']: conv for conv in conversations}
        result = list(unique_conversations.values())
        logging.info(f"Found {len(result)} unique conversations")
        return result

    def monitor_and_respond(self):
        """Main monitoring loop to check for new messages and respond."""
        while self.is_running:
            try:
                for conversation_id in self.monitored_users:
                    try:
                        logging.info(f"Checking conversation: {conversation_id}")
                        
                        if not self.navigate_to_conversation(conversation_id):
                            continue

                        messages = self.get_messages_from_current_conversation()
                        
                        for msg in messages:
                            if not self._should_process_message(msg):
                                continue

                            logging.info(f"New message in {conversation_id}: {msg['text']}")
                            
                            # Get AI response
                            ai_response = self.get_ai_response(msg['text'], conversation_id)
                            if ai_response:
                                logging.info(f"AI Response: {ai_response}")
                                time.sleep(random.randint(2, 5))  # Human-like delay
                                
                                if self.send_message_in_current_conversation(ai_response):
                                    self.processed_messages.add(msg['id'])
                                    self.last_responded_message[conversation_id] = msg['text']
                                    self.save_message_tracking()
                        
                        time.sleep(2)  # Delay between conversation checks
                        
                    except Exception as conv_error:
                        logging.error(f"Error monitoring conversation {conversation_id}: {conv_error}")
                        continue
                
                time.sleep(5)  # Delay between monitoring cycles
                
            except Exception as e:
                logging.error(f"Error in monitoring loop: {e}")
                time.sleep(10)

    def _should_process_message(self, msg: dict) -> bool:
        """Check if a message should be processed."""
        if msg['is_outgoing'] or msg['id'] in self.processed_messages:
            return False

        if msg['id'] in self.bot_messages:
            return False

        monitoring_start = self.monitoring_start_time.get(self.current_conversation_id, time.time())
        if msg['timestamp'] < monitoring_start:
            return False

        last_responded = self.last_responded_message.get(self.current_conversation_id, "")
        if msg['text'] == last_responded:
            return False

        return True

    def start_bot(self, cookies_file: str = None, users: list = None) -> str:
        """Start the Instagram bot."""
        if self.is_running:
            return "Bot is already running"

        try:
            if cookies_file and not self.load_cookies_from_json(cookies_file):
                return "Failed to load cookies or login to Instagram"

            if users:
                self.monitored_users = set(users)
                logging.info(f"Monitoring conversations: {list(self.monitored_users)}")

            self.is_running = True
            logging.info("Instagram bot started - monitoring conversations")
            self.monitor_and_respond()
            return "Bot started successfully"

        except Exception as e:
            logging.error(f"Error starting bot: {e}")
            return f"Failed to start bot: {e}"

    def stop_bot(self) -> str:
        """Stop the Instagram bot and clean up resources."""
        self.is_running = False
        self._cleanup()
        return "Bot stopped successfully"

    def _cleanup(self) -> None:
        """Clean up resources and session data."""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            self.browser = None
            self.page = None
            self.context = None
            self.playwright = None
            self._clear_session_data()
            logging.info("Cleanup completed successfully")
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")

    def _clear_session_data(self) -> None:
        """Clear session data and tracking files."""
        try:
            if os.path.exists(self.message_tracking_file):
                os.remove(self.message_tracking_file)
            
            session_file = os.path.join(self.session_dir, 'session.json')
            if os.path.exists(session_file):
                os.remove(session_file)
            
            if os.path.exists('temp_cookies.json'):
                os.remove('temp_cookies.json')
            
            self.processed_messages.clear()
            self.bot_messages.clear()
            self.conversation_states.clear()
            self.sent_initial_response.clear()
            self.last_responded_message.clear()
            self.monitoring_start_time.clear()
            self.monitored_users.clear()
            self.current_conversation_id = None
        except Exception as e:
            logging.error(f"Error clearing session data: {e}")