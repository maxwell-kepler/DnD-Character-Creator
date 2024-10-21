# character/base.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from config.game_config import ConfigurationManager

@dataclass
class AbilityScores:
    """Ability scores container with configuration-based initialization"""
    def __post_init__(self):
        config = ConfigurationManager().get_config()
        default_score = config.character_base['base_stats']['default_ability_score']
        for ability in config.character_base['abilities']:
            setattr(self, ability, default_score)
    
    def get_modifier(self, ability: str) -> int:
        score = getattr(self, ability)
        return (score - 10) // 2

@dataclass
class Character:
    name: str
    player_name: str = ""
    level: int = 1
    experience_points: int = 0
    ability_scores: AbilityScores = field(default_factory=AbilityScores)
    skills: Dict[str, int] = field(default_factory=dict)
    skill_proficiencies: List[str] = field(default_factory=list)
    saving_throw_proficiencies: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.config = ConfigurationManager().get_config()
        self._initialize_skills()
        self._initialize_base_stats()
    
    def _initialize_skills(self):
        """Initialize skills based on configuration"""
        self.skills = {
            skill: 0 for skill in self.config.character_base['skill_abilities'].keys()
        }
    
    def _initialize_base_stats(self):
        """Initialize base statistics from configuration"""
        base_stats = self.config.character_base['base_stats']
        self.hit_points = base_stats['base_hit_points']
        self.speed = base_stats['base_speed']
        self.size = base_stats['base_size']
        self.proficiency_bonus = base_stats['base_proficiency_bonus']
    
    def get_skill_modifier(self, skill: str) -> int:
        """Calculate skill modifier using configuration-based ability mappings"""
        if skill not in self.skills:
            raise ValueError(f"Invalid skill: {skill}")
        
        ability = self.config.character_base['skill_abilities'][skill]
        modifier = self.ability_scores.get_modifier(ability)
        
        if skill in self.skill_proficiencies:
            modifier += self.proficiency_bonus
        
        return modifier
    
    def update_skills(self):
        """Update all skill modifiers"""
        for skill in self.skills:
            self.skills[skill] = self.get_skill_modifier(skill)