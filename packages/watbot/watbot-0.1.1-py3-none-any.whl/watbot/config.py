"""
Configuration management for WATBOT
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import json
import os
import requests


@dataclass
class InstagramConfig:
    """Instagram-specific configuration"""
    cookies_path: str = "instagram_cookies.json"
    session_backup_url: str = "http://localhost:3000/session/backup"
    headless: bool = True
    debug: bool = False
    session_upload_enabled: bool = True
    monitor_profiles: List[str] = field(default_factory=lambda: ["ALL"])
    do_not_reply: List[str] = field(default_factory=list)
    session_id: str = "default"

    def load_cookies(self) -> Optional[Dict[str, Any]]:
        """Load cookies from file"""
        if os.path.exists(self.cookies_path):
            with open(self.cookies_path, 'r') as f:
                return json.load(f)
        return None

    def save_cookies(self, cookies: Dict[str, Any]) -> None:
        """Save cookies to file and backup to remote"""
        # Save locally
        with open(self.cookies_path, 'w') as f:
            json.dump(cookies, f)

        # Backup to remote endpoint
        if self.session_upload_enabled and self.session_backup_url:
            try:
                backup_data = {
                    'session_id': self.session_id,
                    'cookies': cookies
                }
                response = requests.post(
                    self.session_backup_url, 
                    json=backup_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                response.raise_for_status()
            except Exception as e:
                print(f"Failed to backup session: {e}")


@dataclass
class AIConfig:
    """AI Configuration for bot responses"""
    enabled: bool = True
    introduction: str = (
        "🤖 Hello Human, you reached Nithin but he's currently busy working on some cool stuff. "
        "So you get me instead even though I am in initial stage I will put my things to reply "
        "like Nithin with that unsarcastic sarcasm.\n\n"
        "If it's urgent — like actually urgent — just call him. You know how phones work."
    )
    simple_reply: str = (
        "Hi! the person you want to reach is out there doing something. "
        "But if you need anything let me know I can help. Forgot to introduce myself "
        "I am person digitally to answer. If it urgent try for a call or else drop some mail."
    )
    personality: str = "friendly and helpful with subtle sarcasm"
    context_limit: int = 10
    gemini_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "enabled": self.enabled,
            "introduction": self.introduction,
            "simple_reply": self.simple_reply,
            "personality": self.personality,
            "context_limit": self.context_limit,
        }


@dataclass
class WhatsAppConfig:
    """WhatsApp-specific configuration"""
    monitor_contacts: List[str] = field(default_factory=lambda: ["ALL"])
    do_not_reply: List[str] = field(default_factory=list)
    session_id: str = "default"
    headless: bool = True
    debug: bool = False
    session_upload_enabled: bool = True


@dataclass 
class InstagramConfig:
    """Instagram-specific configuration"""
    username: Optional[str] = None
    password: Optional[str] = None
    cookies_path: str = "instagram_cookies.json"
    headless: bool = True
    debug: bool = False
    session_upload_enabled: bool = True
    monitor_profiles: List[str] = field(default_factory=lambda: ["ALL"])
    do_not_reply: List[str] = field(default_factory=list)
    session_id: str = "default"

    def load_cookies(self) -> Optional[Dict[str, Any]]:
        """Load cookies from file"""
        if os.path.exists(self.cookies_path):
            with open(self.cookies_path, 'r') as f:
                return json.load(f)
        return None

    def save_cookies(self, cookies: Dict[str, Any]) -> None:
        """Save cookies to file"""
        with open(self.cookies_path, 'w') as f:
            json.dump(cookies, f)
    session_server_url: str = "http://104.225.221.108:8080"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "monitor_contacts": self.monitor_contacts,
            "do_not_reply": self.do_not_reply,
            "session_id": self.session_id,
            "headless": self.headless,
            "debug": self.debug,
            "session_upload_enabled": self.session_upload_enabled,
            "session_server_url": self.session_server_url,
        }


@dataclass
class BotConfig:
    """Main bot configuration"""
    whatsapp: WhatsAppConfig = field(default_factory=WhatsAppConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    
    @classmethod
    def from_file(cls, config_path: str) -> "BotConfig":
        """Load configuration from JSON file"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        whatsapp_config = WhatsAppConfig(**data.get('whatsapp', {}))
        ai_config = AIConfig(**data.get('ai', {}))
        
        return cls(whatsapp=whatsapp_config, ai=ai_config)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BotConfig":
        """Load configuration from dictionary"""
        whatsapp_config = WhatsAppConfig(**data.get('whatsapp', {}))
        ai_config = AIConfig(**data.get('ai', {}))
        
        return cls(whatsapp=whatsapp_config, ai=ai_config)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "whatsapp": self.whatsapp.to_dict(),
            "ai": self.ai.to_dict(),
        }
    
    def save_to_file(self, config_path: str):
        """Save configuration to JSON file"""
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def get_env_dict(self) -> Dict[str, str]:
        """Get environment variables dictionary for subprocess"""
        env = os.environ.copy()
        
        # WhatsApp config
        env['SESSION_ID'] = self.whatsapp.session_id
        env['MONITOR_CONTACTS'] = json.dumps(self.whatsapp.monitor_contacts)
        env['DO_NOT_REPLY_CONTACTS'] = json.dumps(self.whatsapp.do_not_reply)
        env['HEADLESS'] = str(self.whatsapp.headless).lower()
        env['DEBUG_MODE'] = str(self.whatsapp.debug).lower()
        env['SESSION_UPLOAD_ENABLED'] = str(self.whatsapp.session_upload_enabled).lower()
        env['SESSION_SERVER_URL'] = self.whatsapp.session_server_url
        
        # AI config
        env['USE_AI_RESPONSES'] = str(self.ai.enabled).lower()
        env['AI_INTRODUCTION'] = self.ai.introduction
        env['SIMPLE_REPLY'] = self.ai.simple_reply
        env['AI_PERSONALITY'] = self.ai.personality
        env['AI_CONTEXT_LIMIT'] = str(self.ai.context_limit)
        
        if self.ai.gemini_api_key:
            env['GEMINI_API_KEY'] = self.ai.gemini_api_key
        
        if self.ai.openrouter_api_key:
            env['OPENROUTER_API_KEY'] = self.ai.openrouter_api_key
        
        return env
