# character/creators/base_creator.py
from abc import ABC, abstractmethod
from character.base import Character
from config.game_config import ConfigurationManager
from typing import List, Dict, Any

class CreatorInterface(ABC):
    """Abstract base class for different parts of character creation"""
    def __init__(self, config: Any):
        self.config = config

    @abstractmethod
    def handle(self, character: Character) -> None:
        """Handle this part of character creation"""
        pass

    def _get_input(self, prompt: str) -> str:
        """Get sanitized input from user"""
        return input(prompt).strip()
