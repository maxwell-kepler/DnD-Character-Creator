# character/base.py
from config.game_config import ConfigurationManager
from typing import Dict, List, Optional

class AbilityScores:
    def __init__(self):
        self.strength = 10
        self.dexterity = 10
        self.constitution = 10
        self.intelligence = 10
        self.wisdom = 10
        self.charisma = 10
    
    def get_modifier(self, ability: str) -> int:
        score = getattr(self, ability.lower())
        return (score - 10) // 2

class Character:
    def __init__(self, name: str, player_name: str = ""):
        # Basic character info
        self.name = name
        self.player_name = player_name
        self.level = 1
        self.experience_points = 0
        
        # Core stats
        self.ability_scores = AbilityScores()
        self.hit_points = 0
        self.armor_class = 10
        self.speed = 30
        self.size = "Medium"
        self.proficiency_bonus = 2
        
        # Configuration
        self.config = ConfigurationManager().get_config()
        
        # Race and class info (to be set later)
        self.race = None
        self.class_name = None
        self.class_data = None
        
        # Skills dictionary
        self.skills = {
            skill: 0 for skill in self.config.character_base['skill_abilities'].keys()
        }
        
        # Proficiencies and features
        self.languages = []
        self.armor_proficiencies = []
        self.weapon_proficiencies = []
        self.skill_proficiencies = []
        self.saving_throw_proficiencies = []
        self.tool_proficiencies = []
    
    def calculate_skill_modifier(self, skill: str) -> int:
        """Calculate the modifier for a given skill"""
        if skill not in self.skills:
            raise ValueError(f"Invalid skill: {skill}")
        
        ability = self.config.character_base['skill_abilities'][skill].lower()
        modifier = self.ability_scores.get_modifier(ability)
        
        if skill in self.skill_proficiencies:
            modifier += self.proficiency_bonus
            
        return modifier

    def update_all_skills(self) -> None:
        """Update all skill modifiers"""
        for skill in self.skills:
            self.skills[skill] = self.calculate_skill_modifier(skill)

    def set_race(self, race_name: str, subrace_name: Optional[str] = None) -> None:
        """Set character race and apply racial traits"""
        if race_name not in self.config.races:
            raise ValueError(f"Invalid race: {race_name}")
        
        race_data = self.config.races[race_name]
        self.race = race_data
        
        # Apply base racial ability score increases
        for ability, increase in self.race['ability_score_increase'].items():
            current = getattr(self.ability_scores, ability.lower())
            setattr(self.ability_scores, ability.lower(), current + increase)
        
        # Apply base racial traits
        self.speed = self.race['speed']
        self.size = self.race['size']
        self.languages.extend(self.race['languages'])
        
        # Apply subrace if provided
        if subrace_name:
            if 'subraces' not in race_data or subrace_name not in race_data['subraces']:
                raise ValueError(f"Invalid subrace: {subrace_name}")
            
            subrace_data = race_data['subraces'][subrace_name]
            self.subrace = subrace_data
            
            # Apply subrace ability score increases
            if 'ability_score_increase' in subrace_data:
                for ability, increase in subrace_data['ability_score_increase'].items():
                    current = getattr(self.ability_scores, ability.lower())
                    setattr(self.ability_scores, ability.lower(), current + increase)
            
            # Apply subrace speed increase if any
            if 'speed_increase' in subrace_data:
                self.speed += subrace_data['speed_increase']
            
            # Add subrace traits
            if 'traits' in subrace_data:
                self.race['traits'].extend(subrace_data['traits'])
        
        # Update skills after applying all racial bonuses
        self.update_all_skills()
    
    def set_class(self, class_name: str) -> None:
        """Set character class and apply class features"""
        if class_name not in self.config.classes:
            raise ValueError(f"Invalid class: {class_name}")
        
        self.class_name = class_name
        self.class_data = self.config.classes[class_name]
        
        # Apply class proficiencies
        self.armor_proficiencies.extend(self.class_data['armor_proficiencies'])
        self.weapon_proficiencies.extend(self.class_data['weapon_proficiencies'])
        self.saving_throw_proficiencies.extend(self.class_data['saving_throws'])
        
        # Set initial hit points (max at first level)
        hit_die = int(self.class_data['hit_dice'].split('d')[1])
        con_mod = self.ability_scores.get_modifier('constitution')
        self.hit_points = hit_die + con_mod
        
        # Apply level 1 features
        self._apply_level_features(1)
        
        # Update skills after applying class features
        self.update_all_skills()

    def set_ability_scores(self, scores: Dict[str, int]) -> None:
        """Set ability scores and update derived statistics"""
        for ability, score in scores.items():
            setattr(self.ability_scores, ability.lower(), score)
        
        # Update derived statistics
        self.update_all_skills()
        self._update_hit_points()
    
    def _update_hit_points(self) -> None:
        """Update hit points based on Constitution modifier and class"""
        if not self.class_data:
            return
            
        hit_die = int(self.class_data['hit_dice'].split('d')[1])
        con_mod = self.ability_scores.get_modifier('constitution')
        self.hit_points = hit_die + con_mod
    
    def set_subclass(self, subclass_name: str) -> None:
        """Set character subclass and apply subclass features"""
        if not self.class_data or 'subclasses' not in self.class_data['features']['level_3']:
            raise ValueError("Character class doesn't have subclasses available")
            
        subclasses = self.class_data['features']['level_3']['subclasses']
        if subclass_name not in subclasses:
            raise ValueError(f"Invalid subclass: {subclass_name}")
            
        self.subclass = subclasses[subclass_name]
        
        # Apply subclass features
        if 'features' in self.subclass:
            for feature in self.subclass['features']:
                # Apply special handling for certain features
                if feature['name'] == "Bonus Proficiencies":
                    if 'armor' in feature['description'].lower():
                        self.armor_proficiencies.extend(["Medium armor", "Shields"])
                    if 'weapon' in feature['description'].lower():
                        self.weapon_proficiencies.append("Martial weapons")
                if feature['name'] == "Bonus Cantrip":
                    # This would be handled by spellcasting system
                    pass
    
    def _apply_level_features(self, level: int) -> None:
        """Apply features for a specific level"""
        level_key = f"level_{level}"
        if level_key in self.class_data['features']:
            for feature in self.class_data['features'][level_key]:
                # Feature application logic here
                # This will be expanded based on feature types
                pass

    def __str__(self) -> str:
        return self.display_info()

    def display_info(self) -> str:
        """Create a formatted display of character information"""
        sections = [
            self._format_header(),
            self._format_core_stats(),
            self._format_abilities(),
            self._format_skills(),
            self._format_features(),
            self._format_proficiencies()
        ]
        
        return "\n\n".join(sections)
    
    def _format_header(self) -> str:
        """Format character header information"""
        race_name = self.race['name'] if self.race else "Unknown Race"
        class_name = self.class_name if self.class_name else "Unknown Class"
        
        return f"""
╔{'═' * 50}╗
║{self.name:^50}║
║{f'Level {self.level} {race_name} {class_name}':^50}║
╚{'═' * 50}╝
"""

    def _format_core_stats(self) -> str:
        """Format core character statistics"""
        return f"""
CORE STATISTICS
──────────────
Hit Points: {self.hit_points}
Armor Class: {self.armor_class}
Speed: {self.speed} ft
Size: {self.size}
"""

    def _format_abilities(self) -> str:
        """Format ability scores and modifiers"""
        lines = ["ABILITY SCORES", "─────────────"]
        for ability in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']:
            score = getattr(self.ability_scores, ability)
            modifier = self.ability_scores.get_modifier(ability)
            save_mod = modifier
            if ability in self.saving_throw_proficiencies:
                save_mod += self.proficiency_bonus
            
            lines.append(f"{ability.title():12} {score:2} ({modifier:+2}) Save: {save_mod:+2}")
        
        return "\n".join(lines)

    def _format_skills(self) -> str:
        """Format skill list with modifiers"""
        lines = ["SKILLS", "──────"]
        
        # Group skills by ability
        skill_groups = {
            'Strength': [], 'Dexterity': [], 'Intelligence': [], 
            'Wisdom': [], 'Charisma': []
        }
        
        skill_abilities = self.config.character_base['skill_abilities']
        
        for skill, modifier in self.skills.items():
            ability = skill_abilities[skill].title()
            proficient = '●' if skill in self.skill_proficiencies else '○'
            skill_groups[ability].append(f"{proficient} {skill:<17} {modifier:+2}")
        
        # Add each group to lines
        for ability, skills in skill_groups.items():
            if skills:
                lines.append(f"\n{ability} Skills:")
                lines.extend(skills)
        
        return "\n".join(lines)

    def _format_features(self) -> str:
        """Format character features and traits"""
        lines = ["FEATURES & TRAITS", "─────────────────"]
        
        # Racial Traits
        if self.race and 'traits' in self.race:
            lines.append("\nRacial Traits:")
            for trait in self.race['traits']:
                lines.append(f"• {trait['name']}")
                lines.append(f"  {trait['description']}")
        
        # Class Features
        if self.class_data and 'features' in self.class_data:
            lines.append("\nClass Features:")
            for level in range(1, self.level + 1):
                level_key = f"level_{level}"
                if level_key in self.class_data['features']:
                    for feature in self.class_data['features'][level_key]:
                        lines.append(f"• {feature['name']} (Level {level})")
                        lines.append(f"  {feature['description']}")
        
        return "\n".join(lines)

    def _format_proficiencies(self) -> str:
        """Format proficiencies section"""
        return f"""
PROFICIENCIES
────────────
Armor: {', '.join(self.armor_proficiencies) if self.armor_proficiencies else 'None'}
Weapons: {', '.join(self.weapon_proficiencies) if self.weapon_proficiencies else 'None'}
Tools: {', '.join(self.tool_proficiencies) if self.tool_proficiencies else 'None'}
Languages: {', '.join(self.languages) if self.languages else 'None'}

Proficiency Bonus: +{self.proficiency_bonus}
"""