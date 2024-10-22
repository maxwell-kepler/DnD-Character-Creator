# character/creators/ability_scores.py
from character.base import Character
from character.creators.base_creator import CreatorInterface
from typing import List#, Dict, Any


class AbilityScoreCreator(CreatorInterface):
    """Handles ability score generation and assignment"""
    
    def handle(self, character: Character) -> None:
        print("\nAbility Score Generation")
        print("Choose your method:")
        print("1. Standard Array (15, 14, 13, 12, 10, 8)")
        print("2. Roll 4d6, drop lowest")
        print("3. Point Buy")
        
        choice = int(self._get_input("Enter your choice (1-3): "))
        
        if choice == 1:
            scores = [15, 14, 13, 12, 10, 8]
        elif choice == 2:
            scores = self._roll_abilities()
        else:
            scores = self._point_buy()
            
        self._assign_ability_scores(character, scores)

    def _roll_abilities(self) -> List[int]:
        import random
        scores = []
        for _ in range(6):
            rolls = sorted([random.randint(1, 6) for _ in range(4)])
            scores.append(sum(rolls[1:]))
        return sorted(scores, reverse=True)

    def _point_buy(self) -> List[int]:
        points = 27
        scores = []
        abilities = ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma']
        costs = {8:0, 9:1, 10:2, 11:3, 12:4, 13:5, 14:7, 15:9}
        
        print("\nPoint Buy System")
        print("You have 27 points to spend")
        print("Costs: 8(-0) 9(-1) 10(-2) 11(-3) 12(-4) 13(-5) 14(-7) 15(-9)")
        
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