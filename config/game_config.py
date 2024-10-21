# config/game_config.py
from pathlib import Path
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass
from functools import lru_cache

@dataclass
class GameConfig:
    """Container for game configuration data"""
    character_base: Dict[str, Any]
    equipment: Dict[str, Any]
    races: Dict[str, Any]
    classes: Dict[str, Any]

class ConfigurationManager:
    """Handles loading and accessing game configuration"""
    _instance: Optional['ConfigurationManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.config = self._load_all_config()
    
    @staticmethod
    def _load_yaml(filename: str) -> Dict[str, Any]:
        config_path = Path(__file__).parent / "data" / filename
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    @lru_cache()
    def _load_all_config(self) -> GameConfig:
        return GameConfig(
            character_base=self._load_yaml("character_base.yaml"),
            equipment=self._load_yaml("equipment.yaml"),
            races=self._load_yaml("races.yaml"),
            classes=self._load_yaml("classes.yaml")
        )
    
    def get_config(self) -> GameConfig:
        return self.config