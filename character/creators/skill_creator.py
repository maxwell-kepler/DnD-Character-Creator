# character/creators/skill_creator.py
from character.base import Character
from character.creators.base_creator import CreatorInterface
from typing import List

class SkillCreator(CreatorInterface):
    """Handles skill selection"""
    
    def handle(self, character: Character) -> None:
        if not character.class_data:
            return
            
        skill_choices = character.class_data['skill_choices']
        num_choices = skill_choices['count']
        available_skills = skill_choices['options'].copy()
        
        print(f"\nChoose {num_choices} skills:")
        self._select_skills(character, available_skills, num_choices)
        character.update_all_skills()

    def _select_skills(self, character: Character, available_skills: List[str], num_choices: int) -> None:
        for _ in range(num_choices):
            print("\nChoose a skill:")
            for i, skill in enumerate(available_skills, 1):
                print(f"{i}. {skill}")
            
            choice = int(self._get_input("Enter your choice (number): "))
            chosen_skill = available_skills.pop(choice - 1)
            character.skill_proficiencies.append(chosen_skill)