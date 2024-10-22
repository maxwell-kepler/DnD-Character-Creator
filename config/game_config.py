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
    class_equipment: Dict[str, Any]  # Add this field
    equipment_types: Dict[str, str]  # Add this for equipment types
    packs: Dict[str, Any]  # Add this for packs

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
        """Load and combine all configuration data"""
        equipment_data = self._load_yaml("equipment.yaml")
        
        return GameConfig(
            character_base=self._load_yaml("character_base.yaml"),
            equipment=equipment_data.get('equipment', {}),
            races=self._load_yaml("races.yaml"),
            classes=self._load_yaml("classes.yaml"),
            class_equipment=equipment_data.get('class_equipment', {}),
            equipment_types=equipment_data.get('equipment_types', {}),
            packs=equipment_data.get('packs', {})
        )
    
    def get_config(self) -> GameConfig:
        return self.config