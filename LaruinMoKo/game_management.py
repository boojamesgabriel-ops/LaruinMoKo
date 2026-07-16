import storage
from game_catalog import display_games, get_non_negative_int, get_positive_money, get_safe_text


def get_confirmation(prompt):
    while True:
        answer = input(prompt).strip().casefold()
        if answer == "y":
            return True
        if answer == "n":
            return False
        print("Invalid input. Please enter Y or N.")


def edit_game():
    try:
        games = storage.load_games()
        display_games(games)
        if not games:
            return

        game_id = get_safe_text("Enter Game ID: ", "Game ID")
        game = next((item for item in games if item["game_id"] == game_id), None)
        if game is None:
            print("Game not found.")
            return

        print(f"\nEditing: {game['title']}")
        game["title"] = get_safe_text("Enter new title: ", "Title")
        game["genre"] = get_safe_text("Enter new genre: ", "Genre")
        game["rental_price"] = get_positive_money("Enter new rental price: ₱")
        game["quantity"] = get_non_negative_int("Enter new quantity: ")
        game["availability"] = storage.availability_for(game["quantity"])
        storage.save_games(games)
        print("Game updated successfully.")
    except storage.StorageError as error:
        print(f"Unable to edit game: {error}")


def delete_game():
    try:
        games = storage.load_games()
        display_games(games)
        if not games:
            return

        game_id = get_safe_text("Enter Game ID: ", "Game ID")
        game = next((item for item in games if item["game_id"] == game_id), None)
        if game is None:
            print("Game not found.")
            return

        rentals = storage.load_rentals()
        has_active_rental = any(
            rental["game_id"] == game_id and rental["status"] == "Rented"
            for rental in rentals
        )
        if has_active_rental:
            print("This game cannot be deleted while it has an active rental.")
            return

        if not get_confirmation(f"Delete {game['title']}? (Y/N): "):
            print("Deletion cancelled.")
            return

        games.remove(game)
        storage.save_games(games)
        print("Game deleted successfully.")
    except storage.StorageError as error:
        print(f"Unable to delete game: {error}")
