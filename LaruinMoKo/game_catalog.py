from decimal import Decimal, InvalidOperation

import storage


GENRES = [
    "Adventure",
    "Role-Playing Games (RPGs)",
    "Action/Action-Adventure",
    "Shooter (FPS/TPS)",
    "Simulation",
    "Racing",
    "Fighting",
    "Puzzle",
    "Strategy",
    "Sports",
]


def get_safe_text(prompt, field_name):
    while True:
        value = input(prompt)
        try:
            return storage.validate_text(value, field_name)
        except ValueError as error:
            print(error)


def get_positive_money(prompt):
    while True:
        value = input(prompt).strip()
        try:
            return storage.normalize_money(value)
        except (ValueError, InvalidOperation) as error:
            print(f"Invalid price: {error}")


def get_non_negative_int(prompt):
    while True:
        value = input(prompt).strip()
        try:
            quantity = int(value)
            if quantity < 0 or str(quantity) != value:
                raise ValueError
            return quantity
        except ValueError:
            print("Invalid input. Enter a whole number of zero or greater.")


def get_positive_int(prompt):
    while True:
        quantity = get_non_negative_int(prompt)
        if quantity > 0:
            return quantity
        print("Quantity must be greater than zero.")


def choose_genre():
    print("\nChoose a genre:")
    for index, genre in enumerate(GENRES, start=1):
        print(f"[{index}] {genre}")

    while True:
        choice = input("Enter genre number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(GENRES):
            return GENRES[int(choice) - 1]
        print("Invalid genre. Please choose from the numbered list.")


def display_game(game):
    print("\nGame ID     :", game["game_id"])
    print("Title       :", game["title"])
    print("Genre       :", game["genre"])
    print("Rental Price: ₱" + storage.format_amount(game["rental_price"]))
    print("Quantity    :", game["quantity"])
    print("Availability:", game["availability"])


def display_games(games):
    if not games:
        print("No games found.")
        return

    print("\nAll Games")
    print("-" * 93)
    print(
        f"{'ID':<8}{'Title':<30}{'Genre':<25}{'Price':>11}"
        f"{'Quantity':>10}  {'Availability'}"
    )
    print("-" * 93)
    for game in games:
        price = f"₱{storage.format_amount(game['rental_price'])}"
        print(
            f"{game['game_id']:<8}{game['title'][:28]:<30}{game['genre'][:23]:<25}"
            f"{price:>11}"
            f"{game['quantity']:>10}  {game['availability']}"
        )


def generate_game_id(games=None):
    if games is None:
        games = storage.load_games()
    return storage.generate_numeric_game_id(games)


def find_game_by_id_or_name(search_value, games=None):
    if games is None:
        games = storage.load_games()
    return storage.find_game(games, search_value)


def add_game():
    try:
        games = storage.load_games()
        title = get_safe_text("\nEnter the title of the game: ", "Title")
        existing = storage.find_game(games, title)
        if existing:
            print(f"\n{existing['title']} already exists.")
            existing["quantity"] += get_positive_int("Enter quantity to add: ")
            existing["availability"] = storage.availability_for(existing["quantity"])
            storage.save_games(games)
            print("Quantity updated successfully.")
            return

        game = {
            "game_id": generate_game_id(games),
            "title": title,
            "genre": choose_genre(),
            "rental_price": get_positive_money("Enter the rental price: ₱"),
            "quantity": get_positive_int("Enter the quantity: "),
        }
        game["availability"] = storage.availability_for(game["quantity"])
        games.append(game)
        storage.save_games(games)
        print(f"{title} was added successfully with Game ID {game['game_id']}.")
    except storage.StorageError as error:
        print(f"Unable to add game: {error}")


def view_game():
    try:
        games = storage.load_games()
        search_value = get_safe_text("\nEnter Game ID or title: ", "Search value")
        game = storage.find_game(games, search_value)
        if game:
            display_game(game)
        else:
            print("Game not found.")
    except storage.StorageError as error:
        print(f"Unable to view game: {error}")


def view_all_games():
    try:
        display_games(storage.load_games())
    except storage.StorageError as error:
        print(f"Unable to view games: {error}")


def search_game():
    try:
        games = storage.load_games()
        search = get_safe_text(
            "\nEnter part of a game title or genre: ", "Search value"
        ).casefold()
        matches = [
            game
            for game in games
            if search in game["title"].casefold() or search in game["genre"].casefold()
        ]
        if not matches:
            print("No matching games found.")
            return
        print("\nSearch Results")
        display_games(matches)
    except storage.StorageError as error:
        print(f"Unable to search games: {error}")
