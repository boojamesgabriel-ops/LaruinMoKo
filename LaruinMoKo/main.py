# This module connects all project features through one terminal-based main menu.
from game_catalog import add_game, search_game, view_all_games, view_game
from game_management import delete_game, edit_game
from payment import view_payment_records
from rental_management import rent_game, return_game, view_rental_records


# This dictionary maps each menu choice to the function that performs the action.
MENU_ACTIONS = {
    "1": add_game,
    "2": view_game,
    "3": view_all_games,
    "4": search_game,
    "5": edit_game,
    "6": delete_game,
    "7": rent_game,
    "8": return_game,
    "9": view_rental_records,
    "10": view_payment_records,
}


# This function prints every available operation in the rental system.
def print_menu():
    print("\n====================================")
    print("        PS5 CD RENTAL SYSTEM")
    print("====================================")
    print("1. Add Game")
    print("2. View Game")
    print("3. View All Games")
    print("4. Search Game")
    print("5. Edit Game")
    print("6. Delete Game")
    print("7. Rent Game and Pay")
    print("8. Return Game")
    print("9. View Rental Records")
    print("10. View Payment Records")
    print("11. Exit")


# This function keeps the program running until the user exits or closes the input.
def main():
    while True:
        print_menu()
        try:
            choice = input("Choose an option: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nProgram closed.")
            return

        if choice == "11":
            print("Thank you for using our system.")
            return

        action = MENU_ACTIONS.get(choice)
        if action is None:
            print("Invalid choice. Please enter a number from 1 to 11.")
            continue

        try:
            action()
        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled.")


# This block starts the menu only when this file is run directly.
if __name__ == "__main__":
    main()
