# character/base.py
from config.game_config import ConfigurationManager
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class InventoryItem:
    name: str
    weight: float
    cost: float
    quantity: int = 1
    
    @property
    def total_weight(self) -> float:
        return self.weight * self.quantity
    
    @property
    def total_cost(self) -> float:
        return self.cost * self.quantity


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

        # New equipment tracking
        self.inventory: List[InventoryItem] = []
        self.currency = {
            'cp': 0,  # Copper pieces
            'sp': 0,  # Silver pieces
            'ep': 0,  # Electrum pieces
            'gp': 0,  # Gold pieces
            'pp': 0   # Platinum pieces
        }


    
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


    def add_item(self, name: str, quantity: int = 1) -> None:
        """Add an item to the character's inventory with improved error handling"""
        if not self.config.equipment:
            raise ValueError("Equipment configuration not loaded")
        
        # Handle ammunition quantities
        base_name = name
        explicit_quantity = None
        if base_name.endswith(')'): 
            try:
                base_name, count = name.rsplit('(', 1)
                base_name = base_name.strip()
                explicit_quantity = int(count.rstrip(')').strip())
            except ValueError:
                pass  # If parsing fails, use the original name
        
        # Search through all equipment categories
        item_data = self._find_item_in_config(base_name)
        if not item_data:
            raise ValueError(f"Item not found: {base_name}")
        
        # Use explicit quantity if provided (e.g., "arrows (20)")
        final_quantity = explicit_quantity if explicit_quantity is not None else quantity
        
        # Convert cost string to value
        cost_str = item_data.get('cost', '0 gp')
        cost_value = self._parse_currency(cost_str)
        
        # Create and add inventory item
        item = InventoryItem(
            name=item_data['name'],
            weight=float(item_data.get('weight', 0)),
            cost=cost_value,
            quantity=final_quantity
        )
        
        # Check for existing item and combine quantities if found
        for existing_item in self.inventory:
            if existing_item.name == item.name:
                existing_item.quantity += final_quantity
                print(f"Added {final_quantity} to existing {item.name} (total: {existing_item.quantity})")
                return
        
        self.inventory.append(item)
        print(f"Added {item.name}" + (f" (×{final_quantity})" if final_quantity > 1 else ""))
    
    
    def _normalize_item_name(self, name: str) -> str:
        """Normalize item name for comparison (e.g., 'Chain Mail' -> 'chain_mail')"""
        return name.lower().replace(' ', '_')

    def _find_item_in_config(self, name: str) -> Optional[Dict]:
        """Enhanced item search to include adventuring gear"""
        normalized_name = self._normalize_item_name(name)
        equipment = self.config.equipment
        
        # Search armor
        for category in equipment['armor'].values():
            if normalized_name in category:
                return category[normalized_name]
            for item_key, item_data in category.items():
                if self._normalize_item_name(item_data['name']) == normalized_name:
                    return item_data
        
        # Search weapons
        for category in equipment['weapons'].values():
            if normalized_name in category:
                return category[normalized_name]
            for item_key, item_data in category.items():
                if self._normalize_item_name(item_data['name']) == normalized_name:
                    return item_data
        
        # Search adventuring gear
        if 'adventuring_gear' in equipment:
            for category in equipment['adventuring_gear'].values():
                if normalized_name in category:
                    return category[normalized_name]
                for item_key, item_data in category.items():
                    if self._normalize_item_name(item_data['name']) == normalized_name:
                        return item_data
        
        # Search adventuring gear subclasses
        if 'adventuring_gear_subclasses' in equipment:
            for subclass in equipment['adventuring_gear_subclasses'].values():
                if normalized_name in subclass:
                    return subclass[normalized_name]
                for item_key, item_data in subclass.items():
                    if self._normalize_item_name(item_data['name']) == normalized_name:
                        return item_data
        
        # Search packs
        if 'packs' in equipment:
            if normalized_name in equipment['packs']:
                return equipment['packs'][normalized_name]
        
        # Search musical instruments
        if normalized_name in equipment['adventuring_gear_subclasses']['musical_instruments']:
            return equipment['adventuring_gear_subclasses']['musical_instruments'][normalized_name]
        
        return None
    
    def _parse_currency(self, cost_str: str) -> float:
        """Convert a currency string (e.g., '50 gp') to gold piece value"""
        if not cost_str:
            return 0.0
            
        amount, currency = cost_str.split()
        amount = float(amount)
        
        # Convert to gold pieces
        conversion = {
            'cp': 0.01,
            'sp': 0.1,
            'ep': 0.5,
            'gp': 1.0,
            'pp': 10.0
        }
        
        return amount * conversion[currency.lower()]
    
    def get_carry_capacity(self) -> float:
        """Calculate the character's maximum carry capacity"""
        strength_score = self.ability_scores.strength
        # Base carrying capacity is strength score × 15
        capacity = strength_score * 15
        
        # Apply size modifiers
        size_multipliers = {
            'Tiny': 0.5,
            'Small': 1.0,
            'Medium': 1.0,
            'Large': 2.0,
            'Huge': 4.0,
            'Gargantuan': 8.0
        }
        
        return capacity * size_multipliers[self.size]
    
    def get_total_weight(self) -> float:
        """Calculate total weight of all carried items"""
        return sum(item.total_weight for item in self.inventory)
    
    def get_total_value(self) -> Dict[str, float]:
        """Calculate total value of all equipment in various currencies"""
        total_gp = sum(item.total_cost for item in self.inventory)
        
        # Add currency pouch contents
        total_gp += (
            self.currency['cp'] * 0.01 +
            self.currency['sp'] * 0.1 +
            self.currency['ep'] * 0.5 +
            self.currency['gp'] +
            self.currency['pp'] * 10
        )
        
        # Convert to different denominations
        return {
            'pp': int(total_gp / 10),
            'gp': int(total_gp % 10),
            'sp': int((total_gp * 10) % 10),
            'cp': int((total_gp * 100) % 10)
        }
    
    def get_encumbrance_level(self) -> Tuple[str, float]:
        """Get the character's encumbrance level and movement penalty"""
        strength_score = self.ability_scores.strength
        total_weight = self.get_total_weight()
        
        # Encumbrance thresholds
        normal_max = strength_score * 5
        heavy_max = strength_score * 10
        capacity_max = self.get_carry_capacity()
        
        if total_weight > capacity_max:
            return "Overencumbered", 0  # Cannot move
        elif total_weight > heavy_max:
            return "Heavily Encumbered", 20  # Speed reduced by 20 feet
        elif total_weight > normal_max:
            return "Encumbered", 10  # Speed reduced by 10 feet
        else:
            return "Normal", 0  # No penalty
    
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

    def add_pack(self, pack_name: str) -> None:
        """Add a pack and all its contents to the character's inventory"""
        if 'packs' not in self.config.equipment or pack_name not in self.config.equipment['packs']:
            raise ValueError(f"Pack not found: {pack_name}")
        
        pack_data = self.config.equipment['packs'][pack_name]
        print(f"\nAdding {pack_data['name']} contents:")
        
        total_weight = 0
        total_value = 0
        
        for content in pack_data['contents']:
            ref = content['reference']
            quantity = content['quantity']
            
            # Find the referenced item in adventuring_gear
            item_data = self._find_referenced_item(ref)
            if not item_data:
                print(f"Warning: Item not found: {ref}")
                continue
            
            try:
                # Add the item to inventory
                self.add_item(item_data['name'], quantity)
                
                # Calculate weight and value
                item_weight = float(item_data.get('weight', 0)) * quantity
                item_value = self._parse_currency(item_data.get('cost', '0 gp')) * quantity
                
                total_weight += item_weight
                total_value += item_value
                
                print(f"Added: {quantity}x {item_data['name']}")
                
            except ValueError as e:
                print(f"Warning: {e}")
        
        # Verify pack total matches expected
        expected_cost = self._parse_currency(pack_data['cost'])
        print(f"\nPack Summary:")
        print(f"Total Weight: {total_weight:.1f} lbs")
        print(f"Total Value: {total_value:.2f} gp")
        if abs(total_value - expected_cost) > 0.01:
            print(f"Note: Pack cost ({expected_cost} gp) differs from sum of items ({total_value:.2f} gp)")

    def _find_referenced_item(self, reference: str) -> Optional[Dict]:
        """Find an item in adventuring_gear by its reference key"""
        equipment = self.config.equipment['adventuring_gear']
        
        # Search through all categories in adventuring_gear
        for category in equipment.values():
            # Search items in this category
            if reference in category:
                return category[reference]
            
            # Try matching by normalized name
            for item_key, item_data in category.items():
                if self._normalize_item_name(item_data['name']) == self._normalize_item_name(reference):
                    return item_data
        
        # Also search adventuring_gear_subclasses
        if 'adventuring_gear_subclasses' in self.config.equipment:
            for subclass in self.config.equipment['adventuring_gear_subclasses'].values():
                if reference in subclass:
                    return subclass[reference]
                # Try matching by normalized name
                for item_key, item_data in subclass.items():
                    if self._normalize_item_name(item_data['name']) == self._normalize_item_name(reference):
                        return item_data
        
        return None

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
            self._format_proficiencies(),
            self._format_equipment() 
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

    def _format_equipment(self) -> str:
        """Format equipment section with weights and values"""
        if not self.inventory:
            return "\nEQUIPMENT\n─────────\nNone"
        
        total_weight = self.get_total_weight()
        carry_capacity = self.get_carry_capacity()
        encumbrance_level, speed_penalty = self.get_encumbrance_level()
        total_value = self.get_total_value()
        
        # Format currency string
        currency_str = []
        for denomination, amount in total_value.items():
            if amount > 0:
                currency_str.append(f"{amount} {denomination}")
        
        lines = [
            "\nEQUIPMENT",
            "─────────"
        ]
        
        # List all items with their individual weights
        for item in sorted(self.inventory, key=lambda x: x.name):
            quantity_str = f" (×{item.quantity})" if item.quantity > 1 else ""
            lines.append(f"• {item.name}{quantity_str} - {item.total_weight} lbs")
        
        # Add summary section
        lines.extend([
            "\nSUMMARY",
            "────────",
            f"Total Weight: {total_weight:.1f} / {carry_capacity:.1f} lbs",
            f"Encumbrance Level: {encumbrance_level}",
            f"Speed Penalty: {speed_penalty} ft" if speed_penalty else "Speed Penalty: None",
            f"Total Value: {', '.join(currency_str)}"
        ])
        
        # Add currency pouch contents if any exists
        if any(self.currency.values()):
            lines.extend([
                "\nCURRENCY POUCH",
                "──────────────",
                f"PP: {self.currency['pp']}",
                f"GP: {self.currency['gp']}",
                f"EP: {self.currency['ep']}",
                f"SP: {self.currency['sp']}",
                f"CP: {self.currency['cp']}"
            ])
        
        return "\n".join(lines)