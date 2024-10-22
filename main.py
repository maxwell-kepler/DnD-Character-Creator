# main.py
from character.base import Character
from config.game_config import ConfigurationManager
from typing import List


class CharacterCreator:
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
            scores = self._standard_array()
        elif choice == 2:
            scores = self._roll_abilities()
        else:
            scores = self._point_buy()
            
        self._assign_ability_scores(character, scores)
    
    def _standard_array(self) -> List[int]:
        """Return the standard array of ability scores"""
        return [15, 14, 13, 12, 10, 8]
    
    def _roll_abilities(self) -> List[int]:
        """Roll 4d6, drop lowest for each ability score"""
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
        
        print("\nAssign your scores:", scores)
        assignments = {}
        
        for score in scores:
            print("\nAvailable abilities:", [a for a in abilities if a not in assignments])
            while True:
                ability = input(f"Assign {score} to which ability? ").title()
                if ability not in abilities or ability in assignments:
                    print("Invalid ability choice. Try again.")
                    continue
                assignments[ability] = score
                break
        
        character.set_ability_scores(assignments)
    
    def _choose_subclass(self, character: Character) -> None:
        """Handle subclass selection"""
        if not character.class_data or 'subclasses' not in character.class_data['features']['level_3']:
            return
            
        subclasses = character.class_data['features']['level_3']['subclasses']
        print("\nChoose your subclass:")
        subclass_names = list(subclasses.keys())
        
        for i, subclass in enumerate(subclass_names, 1):
            print(f"{i}. {subclasses[subclass]['name']}")
            
        choice = int(input("Enter your choice (number): "))
        subclass_choice = subclass_names[choice - 1]
        character.set_subclass(subclass_choice)
    
    def _choose_skills(self, character: Character) -> None:
        """Handle skill selection for the character"""
        if not character.class_data:
            return
            
        skill_choices = character.class_data['skill_choices']
        num_choices = skill_choices['count']
        available_skills = skill_choices['options'].copy()
        
        print(f"\nChoose {num_choices} skills:")
        for _ in range(num_choices):
            # Display available skills
            print("\nChoose a skill:")
            for i, skill in enumerate(available_skills, 1):
                print(f"{i}. {skill}")
            
            # Get choice
            choice = int(input("Enter your choice (number): "))
            chosen_skill = available_skills.pop(choice - 1)
            character.skill_proficiencies.append(chosen_skill)
        
        # Update skill modifiers after all selections
        character.update_all_skills()
    
    def _get_input(self, prompt: str) -> str:
        return input(prompt).strip()

def main():
    creator = CharacterCreator()
    character = creator.create_character()
    print("\nCharacter Created Successfully!")
    print(character)

if __name__ == "__main__":
    main()