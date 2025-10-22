#!/usr/bin/env python3
"""
Config Manager for QINA Security Editor
Persists API key and team ID to a config file.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any


class ConfigManager:
    def __init__(self, app_name: str = "qina_security_editor"):
        self.app_name = app_name
        self.config_dir = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / app_name
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "config.json"

    def load(self) -> Dict[str, Any]:
        if not self.config_file.exists():
            return {}
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f) or {}
        except Exception:
            return {}

    def save(self, data: Dict[str, Any]) -> None:
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def get_api_key(self) -> Optional[str]:
        return self.load().get("api_key")

    def get_team_id(self) -> Optional[str]:
        return self.load().get("team_id")

    def set_api_key(self, api_key: str) -> None:
        data = self.load()
        data["api_key"] = api_key
        self.save(data)

    def set_team_id(self, team_id: str) -> None:
        data = self.load()
        data["team_id"] = str(team_id)
        self.save(data)

    def clear_token(self) -> None:
        data = self.load()
        data.pop("token", None)
        self.save(data)

    def set_token(self, token: str) -> None:
        data = self.load()
        data["token"] = token
        self.save(data)

    def get_token(self) -> Optional[str]:
        return self.load().get("token")

    def clear_all(self) -> None:
        try:
            if self.config_file.exists():
                self.config_file.unlink()
        except Exception:
            pass


    def get_api_base_url(self) -> str:
        """Get the API base URL (QA or Production)"""
        return os.environ.get('CLOUDDEFENSE_API_BASE_URL', 'https://qa.clouddefenseai.com')
    
    def get_ws_base_url(self) -> str:
        """Get the WebSocket base URL (QA or Production)"""
        return os.environ.get('CLOUDDEFENSE_WS_BASE_URL', 'wss://qa.clouddefenseai.com')
    
    def get_environment(self) -> str:
        """Get the current environment (qa or prod)"""
        api_url = self.get_api_base_url()
        if 'qa.clouddefenseai.com' in api_url:
            return 'qa'
        elif 'console.clouddefenseai.com' in api_url:
            return 'prod'
        else:
            return 'qa'  # Default to QA
