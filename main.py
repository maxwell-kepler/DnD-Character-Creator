# main.py
from character.base import Character
from config.game_config import ConfigurationManager
from typing import Optional, List

class CharacterCreator:
    def __init__(self):
        self.config = ConfigurationManager().get_config()
    
    def create_character(self) -> Character:
        """Create a new character with configuration-based validation"""
        name = self._get_input("Enter character name: ")
        player_name = self._get_input("Enter player name: ")
        
        character = Character(name=name, player_name=player_name)
        
        # Load race options from config
        race_choice = self._choose_from_list(
            "Choose your race:",
            list(self.config.races.keys())
        )
        self._apply_race(character, race_choice)
        
        # Load class options from config
        class_choice = self._choose_from_list(
            "Choose your class:",
            list(self.config.classes.keys())
        )
        self._apply_class(character, class_choice)
        
        return character
    
    def _get_input(self, prompt: str) -> str:
        return input(prompt).strip()
    
    def _choose_from_list(self, prompt: str, options: List[str]) -> str:
        print(f"\n{prompt}")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        
        while True:
            try:
                choice = int(input("\nEnter your choice (number): "))
                if 1 <= choice <= len(options):
                    return options[choice - 1]
            except ValueError:
                pass
            print(f"Please enter a number between 1 and {len(options)}")
    
    def _apply_race(self, character: Character, race: str) -> None:
        """Apply racial traits and bonuses from configuration"""
        race_config = self.config.races[race]
        
        # Apply ability score increases
        for ability, increase in race_config['ability_score_increase'].items():
            current_score = getattr(character.ability_scores, ability.lower())
            setattr(character.ability_scores, ability.lower(), current_score + increase)
        
        # Apply other racial traits
        character.speed = race_config['speed']
        character.size = race_config['size']
        # Add other racial features as needed
    
    def _apply_class(self, character: Character, class_name: str) -> None:
        """Apply class features and proficiencies from configuration"""
        class_config = self.config.classes[class_name]
        
        # Apply saving throw proficiencies
        character.saving_throw_proficiencies.extend(class_config['saving_throws'])
        
        # Handle skill choices
        available_skills = class_config['skill_choices']['options']
        num_choices = class_config['skill_choices']['count']
        
        print(f"\nChoose {num_choices} skills:")
        for _ in range(num_choices):
            skill = self._choose_from_list(
                "Choose a skill:",
                [skill for skill in available_skills if skill not in character.skill_proficiencies]
            )
            character.skill_proficiencies.append(skill)
        
        character.update_skills()

def main():
    creator = CharacterCreator()
    character = creator.create_character()
    print("\nCharacter Created Successfully!")
    print(character)

if __name__ == "__main__":
    main()