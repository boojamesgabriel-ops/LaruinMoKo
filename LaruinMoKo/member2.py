"""Game maintenance module for the PS5 CD Game Rental System.

This module contains only the Member 2 features: editing and deleting games.
The data file (games.txt) is expected to be in the same folder as this file.
"""

import math
from pathlib import Path


# Using the script's folder makes this module work from any current directory.
GAMES_FILE = Path(__file__).with_name("games.txt")


def load_games():
    """Read games.txt and return the records as a list of dictionaries.

    None is returned when the file cannot be loaded safely. An empty file
    returns an empty list.
    """
    games = []

    try:
        with GAMES_FILE.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()

                # Ignore blank lines in the text file.
                if not line:
                    continue

                parts = line.split("|")
                if len(parts) != 6:
                    raise ValueError(
                        f"Invalid record format on line {line_number}."
                    )

                game_id, title, genre, price_text, quantity_text, availability = parts

                # Validate file data before allowing it to be changed.
                if not game_id.isdigit():
                    raise ValueError(f"Invalid Game ID on line {line_number}.")

                rental_price = float(price_text)
                quantity = int(quantity_text)

                if (
                    not title.strip()
                    or not genre.strip()
                    or not math.isfinite(rental_price)
                    or rental_price <= 0
                    or quantity < 0
                ):
                    raise ValueError(f"Invalid game data on line {line_number}.")

                # Availability is derived from quantity, keeping the data consistent.
                availability = "Available" if quantity > 0 else "Unavailable"
                games.append(
                    {
                        "game_id": game_id,
                        "title": title.strip(),
                        "genre": genre.strip(),
                        "rental_price": rental_price,
                        "quantity": quantity,
                        "availability": availability,
                    }
                )

        return games

    except FileNotFoundError:
        print("games.txt not found.")
    except ValueError as error:
        print(f"Unable to load games: {error}")
    except OSError as error:
        print(f"Unable to read games.txt: {error}")
    except Exception as error:
        print(f"An unexpected error occurred while loading games: {error}")

    return None


def format_number(number):
    """Return a number without an unnecessary .0 for text-file storage."""
    return f"{number:g}"


def save_games(games):
    """Write every game record to games.txt. Return True when successful."""
    try:
        with GAMES_FILE.open("w", encoding="utf-8") as file:
            for game in games:
                record = "|".join(
                    [
                        game["game_id"],
                        game["title"],
                        game["genre"],
                        format_number(game["rental_price"]),
                        str(game["quantity"]),
                        game["availability"],
                    ]
                )
                file.write(record + "\n")
        return True

    except (OSError, ValueError) as error:
        print(f"Unable to save games.txt: {error}")
    except Exception as error:
        print(f"An unexpected error occurred while saving games: {error}")

    return False


def display_games(games):
    """Display game records in a readable table."""
    if not games:
        print("\nNo games found.")
        return

    print("\n" + "=" * 91)
    print(
        f"{'Game ID':<10}{'Title':<30}{'Genre':<16}"
        f"{'Price':>10}{'Quantity':>11}  {'Availability':<12}"
    )
    print("-" * 91)

    for game in games:
        print(
            f"{game['game_id']:<10}{game['title'][:28]:<30}"
            f"{game['genre'][:14]:<16}{format_number(game['rental_price']):>10}"
            f"{game['quantity']:>11}  {game['availability']:<12}"
            
        )

    print("=" * 91)


def validate_game_id(prompt="Enter Game ID: "):
    """Keep asking until a non-empty numeric Game ID is entered."""
    while True:
        game_id = input(prompt).strip()

        if not game_id:
            print("Game ID cannot be empty.")
        elif not game_id.isdigit():
            print("Invalid input. Game ID must be numeric.")
        else:
            return game_id


def validate_non_blank(prompt, field_name):
    """Keep asking until text containing at least one character is entered."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print(f"{field_name} cannot be blank.")


def validate_positive_number(prompt):
    """Keep asking until a finite number greater than zero is entered."""
    while True:
        try:
            value = float(input(prompt).strip())
            if not math.isfinite(value) or value <= 0:
                print("Rental Price must be a positive number.")
            else:
                return value
        except ValueError:
            print("Invalid input. Please enter a number.")


def validate_non_negative_integer(prompt):
    """Keep asking until a whole number of zero or greater is entered."""
    while True:
        try:
            value = int(input(prompt).strip())
            if value < 0:
                print("Quantity must be a non-negative integer.")
            else:
                return value
        except ValueError:
            print("Invalid input. Please enter a non-negative integer.")


def find_game(games, game_id):
    """Return the game with the matching ID, or None when not found."""
    for game in games:
        if game["game_id"] == game_id:
            return game
    return None


def edit_game():
    """Display the games, validate new values, and update one game."""
    try:
        games = load_games()
        if games is None:
            return

        display_games(games)
        game_id = validate_game_id()
        game = find_game(games, game_id)

        if game is None:
            print("Game not found.")
            return

        print(f"\nEditing: {game['title']}")
        game["title"] = validate_non_blank("Enter new Title: ", "Title")
        game["genre"] = validate_non_blank("Enter new Genre: ", "Genre")
        game["rental_price"] = validate_positive_number(
            "Enter new Rental Price: "
        )
        game["quantity"] = validate_non_negative_integer("Enter new Quantity: ")

        # Availability must always match the new quantity.
        if game["quantity"] > 0:
            game["availability"] = "Available"
        else:
            game["availability"] = "Unavailable"

        if save_games(games):
            print("Game updated successfully.")

    except (KeyboardInterrupt, EOFError):
        print("\nEdit cancelled.")
    except Exception as error:
        print(f"An unexpected error occurred while editing the game: {error}")


def get_confirmation(prompt):
    """Ask a Y/N question until the user enters a valid response."""
    while True:
        answer = input(prompt).strip().upper()
        if answer == "Y":
            return True
        elif answer == "N":
            return False
        else:
            print("Invalid input. Please enter Y or N.")


def delete_game():
    """Display the games and delete one record after confirmation."""
    try:
        games = load_games()
        if games is None:
            return

        display_games(games)
        game_id = validate_game_id()
        game = find_game(games, game_id)

        if game is None:
            print("Game not found.")
            return

        if get_confirmation("Are you sure? (Y/N): "):
            games.remove(game)
            if save_games(games):
                print("Game deleted successfully.")
        else:
            print("Deletion cancelled.")

    except (KeyboardInterrupt, EOFError):
        print("\nDeletion cancelled.")
    except Exception as error:
        print(f"An unexpected error occurred while deleting the game: {error}")


def main():
    """Run the game-maintenance menu until the user chooses Back."""
    while True:
        print("\n==============================")
        print(" PS5 CD GAME RENTAL SYSTEM")
        print("==============================")
        print("1. Edit Game")
        print("2. Delete Game")
        print("3. Back")

        choice = input("\nChoose: ").strip()

        if choice == "1":
            edit_game()
        elif choice == "2":
            delete_game()
        elif choice == "3":
            print("Returning to the main menu...")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nProgram closed.")
    except Exception as error:
        print(f"An unexpected error occurred: {error}")
    