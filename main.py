# main.py

# Standard library imports
from typing import Dict, List, Any

# Configuration imports
from config.game_config import ConfigurationManager

# Base character class
from character.base import Character

# Creator classes
from character.creators.base_creator import CreatorInterface
from character.creators.ability_scores import AbilityScoreCreator
from character.creators.race_creator import RaceCreator
from character.creators.equipment_creator import EquipmentCreator
from character.creators.skill_creator import SkillCreator

# main.py
class CharacterCreator:
    """Main character creation orchestrator"""
    
    def __init__(self):
        self.config = ConfigurationManager().get_config()
        self.creators = {
            'ability_scores': AbilityScoreCreator(self.config),
            'race': RaceCreator(self.config),
            'equipment': EquipmentCreator(self.config),
            'skills': SkillCreator(self.config)
        }
    
    def create_character(self) -> Character:
        """Create a new character using the creation pipeline"""
        name = self._get_input("Enter character name: ")
        player_name = self._get_input("Enter player name: ")
        
        character = Character(name=name, player_name=player_name)
        
        # Run through the creation pipeline
        self.creators['ability_scores'].handle(character)
        self.creators['race'].handle(character)
        
        # Set class
        self._set_character_class(character)
        
        # Complete remaining creation steps
        self.creators['equipment'].handle(character)
        self.creators['skills'].handle(character)
        
        return character

    def _set_character_class(self, character: Character) -> None:
        class_choices = list(self.config.classes.keys())
        print("\nChoose your class:")
        for i, class_name in enumerate(class_choices, 1):
            print(f"{i}. {class_name}")
        
        choice = int(self._get_input("Enter your choice (number): "))
        class_choice = class_choices[choice - 1]
        character.set_class(class_choice)

    def _get_input(self, prompt: str) -> str:
        return input(prompt).strip()

def main():
    creator = CharacterCreator()
    character = creator.create_character()
    print("\nCharacter Created Successfully!")
    print(character)

if __name__ == "__main__":
    main()


'''class CharacterCreator:
    def __init__(self):
        self.config = ConfigurationManager().get_config()
    
    def create_character(self) -> Character:
        """Create a new character with configuration-based validation"""
        name = self._get_input("Enter character name: ")
        player_name = self._get_input("Enter player name: ")
        
        character = Character(name=name, player_name=player_name)
        
        # Generate ability scores first
        self._handle_ability_scores(character)
        
        # Choose race and subrace
        self._choose_race_and_subrace(character)
        
        # Choose and set class
        class_choices = list(self.config.classes.keys())
        print("\nChoose your class:")
        for i, class_name in enumerate(class_choices, 1):
            print(f"{i}. {class_name}")
        
        choice = int(input("Enter your choice (number): "))
        class_choice = class_choices[choice - 1]
        character.set_class(class_choice)
        
        # Choose equipment
        self._choose_equipment(character)
        
        # Choose skills based on class options
        self._choose_skills(character)
        
        # Choose subclass if level is 3 or higher
        if character.level >= 3:
            self._choose_subclass(character)
        
        return character

    def _choose_race_and_subrace(self, character: Character) -> None:
        """Handle race and subrace selection"""
        # Display available races
        race_choices = list(self.config.races.keys())
        print("\nChoose your race:")
        for i, race in enumerate(race_choices, 1):
            print(f"{i}. {race}")
        
        choice = int(input("Enter your choice (number): "))
        race_choice = race_choices[choice - 1]
        race_data = self.config.races[race_choice]
        
        # Check if the race has subraces
        subrace_choice = None
        if 'subraces' in race_data and race_data['subraces']:
            print(f"\nChoose your {race_choice} subrace:")
            subrace_choices = list(race_data['subraces'].keys())
            
            for i, subrace in enumerate(subrace_choices, 1):
                subrace_name = race_data['subraces'][subrace]['name']
                print(f"{i}. {subrace_name}")
            
            choice = int(input("Enter your choice (number): "))
            subrace_choice = subrace_choices[choice - 1]
            
            # Display subrace description
            print(f"\nSelected: {race_data['subraces'][subrace_choice]['name']}")
            if 'traits' in race_data['subraces'][subrace_choice]:
                print("Subracial Traits:")
                for trait in race_data['subraces'][subrace_choice]['traits']:
                    print(f"• {trait['name']}: {trait['description']}")
        
        # Set race and subrace
        character.set_race(race_choice, subrace_choice)
        
        # Display selected race/subrace information
        print(f"\nSelected Race: {character.race['name']}")
        if hasattr(character, 'subrace'):
            print(f"Subrace: {character.subrace['name']}")
        print("\nRacial Traits:")
        for trait in character.race['traits']:
            print(f"• {trait['name']}: {trait['description']}")

    def _handle_ability_scores(self, character: Character) -> None:
        """Handle ability score generation and assignment"""
        print("\nAbility Score Generation")
        print("Choose your method:")
        print("1. Standard Array (15, 14, 13, 12, 10, 8)")
        print("2. Roll 4d6, drop lowest")
        print("3. Point Buy")
        
        choice = int(input("Enter your choice (1-3): "))
        
        if choice == 1:
            scores = [15, 14, 13, 12, 10, 8]
        elif choice == 2:
            scores = self._roll_abilities()
        else:
            scores = self._point_buy()
            
        self._assign_ability_scores(character, scores)
    
    def _roll_abilities(self) -> List[int]:
        """Roll 4d6, drop lowest for each ability score"""
        import random
        scores = []
        for _ in range(6):
            rolls = sorted([random.randint(1, 6) for _ in range(4)])
            scores.append(sum(rolls[1:]))  # Drop lowest roll
        scores.sort(reverse=True)
        return scores
    
    def _point_buy(self) -> List[int]:
        """Handle point buy ability score generation"""
        print("\nPoint Buy System")
        print("You have 27 points to spend")
        print("Costs: 8(-0) 9(-1) 10(-2) 11(-3) 12(-4) 13(-5) 14(-7) 15(-9)")
        
        points = 27
        scores = []
        abilities = ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma']
        costs = {8:0, 9:1, 10:2, 11:3, 12:4, 13:5, 14:7, 15:9}
        
        for ability in abilities:
            while True:
                try:
                    score = int(input(f"\nChoose score for {ability} (8-15, {points} points remaining): "))
                    if score not in costs:
                        print("Invalid score. Choose between 8 and 15.")
                        continue
                    
                    cost = costs[score]
                    if cost > points:
                        print("Not enough points remaining.")
                        continue
                    
                    points -= cost
                    scores.append(score)
                    break
                except ValueError:
                    print("Please enter a valid number.")
        
        return scores
    
    def _assign_ability_scores(self, character: Character, scores: List[int]) -> None:
        """Assign generated scores to abilities"""
        abilities = ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma']
        assignments = {}
        
        print("\nAssign your scores:", scores)
        for score in scores:
            remaining_abilities = [a for a in abilities if a not in assignments]
            
            print(f"\nAssign {score} to which ability?")
            for i, ability in enumerate(remaining_abilities, 1):
                print(f"{i}. {ability}")
            
            while True:
                try:
                    choice = int(input("Enter number: "))
                    if 1 <= choice <= len(remaining_abilities):
                        ability = remaining_abilities[choice - 1]
                        assignments[ability] = score
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(remaining_abilities)}")
                except ValueError:
                    print("Please enter a valid number")
        
        character.set_ability_scores(assignments)
    
    def _choose_skills(self, character: Character) -> None:
        """Handle skill selection for the character"""
        if not character.class_data:
            return
            
        skill_choices = character.class_data['skill_choices']
        num_choices = skill_choices['count']
        available_skills = skill_choices['options'].copy()
        
        print(f"\nChoose {num_choices} skills:")
        for _ in range(num_choices):
            print("\nChoose a skill:")
            for i, skill in enumerate(available_skills, 1):
                print(f"{i}. {skill}")
            
            choice = int(input("Enter your choice (number): "))
            chosen_skill = available_skills.pop(choice - 1)
            character.skill_proficiencies.append(chosen_skill)
        
        character.update_all_skills()
    
    def _get_input(self, prompt: str) -> str:
        return input(prompt).strip()

    def _choose_equipment(self, character: Character) -> None:
        """Handle equipment selection based on character class"""
        if not character.class_name or character.class_name not in self.config.equipment['class_equipment']:
            return
            
        equipment_options = self.config.equipment['class_equipment'][character.class_name]
        
        print("\nChoose your starting equipment:")
        
        # Process each option set
        for i, option_set in enumerate(equipment_options['option_sets'], 1):
            # Handle fixed equipment first
            if 'fixed' in option_set:
                for item in option_set['fixed']:
                    try:
                        character.add_item(item)
                        print(f"Added: {item}")
                    except ValueError as e:
                        print(f"Warning: Couldn't add {item} - {e}")
                continue
                
            # Handle choice-based equipment
            if 'choices' in option_set:
                print(f"\nOption Set {i}:")
                for j, choice in enumerate(option_set['choices'], 1):
                    if isinstance(choice, list):
                        print(f"{j}. {', '.join(choice)}")
                    else:
                        print(f"{j}. {choice}")
                
                while True:
                    try:
                        choice_idx = int(input("Enter your choice (number): ")) - 1
                        if 0 <= choice_idx < len(option_set['choices']):
                            chosen_items = option_set['choices'][choice_idx]
                            if isinstance(chosen_items, list):
                                for item in chosen_items:
                                    self._handle_equipment_choice(character, item)
                            else:
                                self._handle_equipment_choice(character, chosen_items)
                            break
                        else:
                            print("Invalid choice. Please try again.")
                    except ValueError as e:
                        print(f"Error: {e}")
                        print("Please enter a valid number.")

    def _handle_equipment_choice(self, character: Character, item: str) -> None:
        """Handle a single equipment choice, including category-based choices"""
        # Define special choices that need category handling
        special_choices = {
            "martial_melee_weapon": ("martial_melee", "Choose a martial melee weapon:"),
            "martial_ranged_weapon": ("martial_ranged", "Choose a martial ranged weapon:"),
            "simple_melee_weapon": ("simple_melee", "Choose a simple melee weapon:"),
            "simple_ranged_weapon": ("simple_ranged", "Choose a simple ranged weapon:"),
            "two_martial_weapons": ("martial_combined", "Choose two martial weapons (can be the same):"),
            "other_musical_instrument": ("instruments", "Choose a musical instrument:")
        }
        
        # Special handling for category-based choices
        if item in special_choices:
            category, prompt = special_choices[item]
            if category == "martial_combined":
                self._choose_two_martial_weapons(character)
            elif category == "instruments":
                self._choose_musical_instrument(character)
            else:
                self._choose_from_weapon_category(character, category, prompt)
        else:
            # Direct item addition
            try:
                character.add_item(item)
            except ValueError as e:
                print(f"Warning: {e}")'''

