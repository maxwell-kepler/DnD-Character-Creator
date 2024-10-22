# character/creators/race_creator.py
from character.base import Character
from character.creators.base_creator import CreatorInterface

class RaceCreator(CreatorInterface):
    """Handles race and subrace selection"""
    
    def handle(self, character: Character) -> None:
        race_choices = list(self.config.races.keys())
        print("\nChoose your race:")
        for i, race in enumerate(race_choices, 1):
            print(f"{i}. {race}")
        
        choice = int(self._get_input("Enter your choice (number): "))
        race_choice = race_choices[choice - 1]
        
        subrace_choice = self._handle_subrace_selection(race_choice)
        character.set_race(race_choice, subrace_choice)
        self._display_race_info(character)

    def _handle_subrace_selection(self, race_choice: str) -> str:
        race_data = self.config.races[race_choice]
        if 'subraces' not in race_data or not race_data['subraces']:
            return None
            
        print(f"\nChoose your {race_choice} subrace:")
        subrace_choices = list(race_data['subraces'].keys())
        
        for i, subrace in enumerate(subrace_choices, 1):
            subrace_name = race_data['subraces'][subrace]['name']
            print(f"{i}. {subrace_name}")
        
        choice = int(self._get_input("Enter your choice (number): "))
        return subrace_choices[choice - 1]

    def _display_race_info(self, character: Character) -> None:
        print(f"\nSelected Race: {character.race['name']}")
        if hasattr(character, 'subrace'):
            print(f"Subrace: {character.subrace['name']}")
        print("\nRacial Traits:")
        for trait in character.race['traits']:
            print(f"• {trait['name']}: {trait['description']}")