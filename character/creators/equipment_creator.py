# character/creators/equipment_creator.py
from character.base import Character
from character.creators.base_creator import CreatorInterface
from typing import Dict, List, Any

class EquipmentCreator(CreatorInterface):
    """Handles equipment selection"""
    
    def handle(self, character: Character) -> None:
        if not character.class_name or character.class_name not in self.config.equipment['class_equipment']:
            return
            
        equipment_options = self.config.equipment['class_equipment'][character.class_name]
        print("\nChoose your starting equipment:")
        
        self._process_equipment_options(character, equipment_options)
        self._add_starting_money(character)

    def _process_equipment_options(self, character: Character, equipment_options: Dict) -> None:
        """Process all equipment options for a character"""
        for i, option_set in enumerate(equipment_options['option_sets'], 1):
            if 'fixed' in option_set:
                self._handle_fixed_equipment(character, option_set['fixed'])
            elif 'choices' in option_set:
                print(f"\nEquipment Choice Set {i}:")
                self._handle_equipment_choices(character, option_set['choices'], i)

    def _handle_fixed_equipment(self, character: Character, items: List[str]) -> None:
        """Handle adding fixed equipment items"""
        for item in items:
            if item.endswith('_pack'):
                try:
                    character.add_pack(item)
                except ValueError as e:
                    print(f"Warning: Could not add pack {item}: {e}")
            else:
                try:
                    character.add_item(item)
                    print(f"Added: {item}")
                except ValueError as e:
                    print(f"Warning: Couldn't add {item} - {e}")

    def _handle_equipment_choices(self, character: Character, choices: List[Any], option_num: int) -> None:
        """Handle presenting and processing equipment choices"""
        # Display choices
        for i, choice in enumerate(choices, 1):
            if isinstance(choice, list):
                print(f"{i}. {', '.join(choice)}")
            else:
                # Handle pack display names
                if choice.endswith('_pack'):
                    pack_data = self.config.equipment['packs'].get(choice)
                    if pack_data:
                        print(f"{i}. {pack_data['name']}")
                    else:
                        print(f"{i}. {choice}")
                else:
                    print(f"{i}. {choice}")
        
        # Get user choice
        while True:
            try:
                choice_idx = int(input("Enter your choice (number): ")) - 1
                if 0 <= choice_idx < len(choices):
                    chosen_items = choices[choice_idx]
                    if isinstance(chosen_items, list):
                        for item in chosen_items:
                            self._handle_equipment_choice(character, item)
                    else:
                        self._handle_equipment_choice(character, chosen_items)
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError as e:
                print(f"Please enter a valid number between 1 and {len(choices)}")

    def _handle_equipment_choice(self, character: Character, item: str) -> None:
        """Handle a single equipment choice, including category-based choices and packs"""
        # Define special choices that need category handling
        special_choices = {
            "martial_melee_weapon": ("martial_melee", "Choose a martial melee weapon:"),
            "martial_ranged_weapon": ("martial_ranged", "Choose a martial ranged weapon:"),
            "simple_melee_weapon": ("simple_melee", "Choose a simple melee weapon:"),
            "simple_ranged_weapon": ("simple_ranged", "Choose a simple ranged weapon:"),
            "two_martial_weapons": ("martial_combined", "Choose two martial weapons (can be the same):"),
            "other_musical_instrument": ("instruments", "Choose a musical instrument:")
        }
        
        # Check if this is a pack
        if item.endswith('_pack'):
            try:
                character.add_pack(item)
            except ValueError as e:
                print(f"Warning: Could not add pack {item}: {e}")
                print("Defaulting to Explorer's Pack...")
                try:
                    character.add_pack("explorers_pack")
                except ValueError as e2:
                    print(f"Error: Could not add default pack either: {e2}")
            return
        
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
                print(f"Warning: {e}")

    def _get_instruments_from_category(self) -> List[str]:
        """Get list of available musical instruments"""
        instruments = []
        musical_instruments = self.config.equipment['adventuring_gear_subclasses'].get('musical_instruments', {})
        for instrument_data in musical_instruments.values():
            instruments.append(instrument_data['name'])
        return sorted(instruments)

    def _get_weapons_from_category(self, category: str) -> List[str]:
        """Get list of weapons from a specific category"""
        weapons = []
        if category in self.config.equipment['weapons']:
            for weapon_data in self.config.equipment['weapons'][category].values():
                weapons.append(weapon_data['name'])
        return sorted(weapons)

    def _choose_from_weapon_category(self, character: Character, category: str, prompt: str) -> None:
        """Handle choosing a weapon from a specific category"""
        weapons = self._get_weapons_from_category(category)
        if not weapons:
            print(f"No weapons available in category: {category}")
            return
        
        print(f"\n{prompt}")
        for i, weapon in enumerate(weapons, 1):
            print(f"{i}. {weapon}")
        
        while True:
            try:
                choice = int(input("Enter your choice (number): ")) - 1
                if 0 <= choice < len(weapons):
                    character.add_item(weapons[choice])
                    break
                else:
                    print(f"Please enter a number between 1 and {len(weapons)}")
            except ValueError:
                print("Please enter a valid number")

    def _choose_two_martial_weapons(self, character: Character) -> None:
        """Handle the special case of choosing two martial weapons"""
        # Combine both martial melee and ranged weapons
        melee_weapons = self._get_weapons_from_category("martial_melee")
        ranged_weapons = self._get_weapons_from_category("martial_ranged")
        all_weapons = sorted(melee_weapons + ranged_weapons)
        
        print("\nChoose your first martial weapon:")
        for i, weapon in enumerate(all_weapons, 1):
            print(f"{i}. {weapon}")
        
        # First weapon choice
        while True:
            try:
                choice1 = int(input("Enter your first choice (number): ")) - 1
                if 0 <= choice1 < len(all_weapons):
                    character.add_item(all_weapons[choice1])
                    break
                else:
                    print(f"Please enter a number between 1 and {len(all_weapons)}")
            except ValueError:
                print("Please enter a valid number")
        
        # Second weapon choice (can be the same as the first)
        print("\nChoose your second martial weapon (can be the same as the first):")
        for i, weapon in enumerate(all_weapons, 1):
            print(f"{i}. {weapon}")
        
        while True:
            try:
                choice2 = int(input("Enter your second choice (number): ")) - 1
                if 0 <= choice2 < len(all_weapons):
                    character.add_item(all_weapons[choice2])
                    break
                else:
                    print(f"Please enter a number between 1 and {len(all_weapons)}")
            except ValueError:
                print("Please enter a valid number")

    def _choose_musical_instrument(self, character: Character) -> None:
        """Handle musical instrument selection"""
        instruments = self._get_instruments_from_category()
        
        print("\nChoose a musical instrument:")
        for i, instrument in enumerate(instruments, 1):
            print(f"{i}. {instrument}")
        
        while True:
            try:
                musicChoice = int(input("Enter your choice (number): ")) - 1
                if 0 <= musicChoice < len(instruments):
                    print(instruments[musicChoice])
                    character.add_item(instruments[musicChoice])
                    break
                else:
                    print(f"Please enter a number between 1 and {len(instruments)}")
            except ValueError:
                print("Please enter a valid number")


    def _add_starting_money(self, character: Character) -> None:
        """
        Add starting money to character based on their class.
        Each class has a different starting amount of money.
        """
        starting_money = {
            'fighter': {'gp': 5, 'sp': 4},  # 5 gold, 4 silver
            'bard': {'gp': 5},              # 5 gold
            'cleric': {'gp': 5},            # 5 gold
            'rogue': {'gp': 4},             # 4 gold
            'wizard': {'gp': 4},            # 4 gold
            'ranger': {'gp': 4, 'sp': 5},   # 4 gold, 5 silver
            'paladin': {'gp': 5, 'sp': 5},  # 5 gold, 5 silver
            'monk': {'gp': 5},              # 5 gold
            'barbarian': {'gp': 4},         # 4 gold
            'druid': {'gp': 4, 'sp': 5},    # 4 gold, 5 silver
            'warlock': {'gp': 4},           # 4 gold
            'sorcerer': {'gp': 4}           # 4 gold
        }

        # If class not found, provide default starting money
        default_money = {'gp': 4}  # Default: 4 gold pieces

        class_money = starting_money.get(character.class_name.lower(), default_money)
        
        # Add money to character's currency pouch
        for currency, amount in class_money.items():
            character.currency[currency] = amount
            print(f"Added starting money: {amount} {currency}")