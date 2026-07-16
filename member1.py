GAMES_FILE = "games.txt"

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


def load_games():
    games = []

    try:
        with open(GAMES_FILE, "r") as file:
            for line in file:
                line = line.strip()

                if not line:
                    continue

                data = line.split(",")

                if len(data) == 6:
                    game_id, name, genre, price, quantity, status = data
                elif len(data) == 5:
                    # Supports older records that were saved without quantity.
                    game_id, name, genre, price, status = data
                    quantity = "0"
                else:
                    continue

                price = price.replace("₱", "").strip()
                quantity = quantity.strip()

                if not price.replace(".", "", 1).isdigit() or not quantity.isdigit():
                    continue

                game = {
                    "id": game_id.strip(),
                    "name": name.strip(),
                    "genre": genre.strip(),
                    "price": float(price),
                    "quantity": int(quantity),
                    "status": status.strip(),
                }
                update_status(game)
                games.append(game)
    except FileNotFoundError:
        pass

    return games


def save_games(games):
    with open(GAMES_FILE, "w") as file:
        for game in games:
            file.write(
                f"{game['id']},{game['name']},{game['genre']},"
                f"{format_price(game['price'])},{game['quantity']},{game['status']}\n"
            )


def format_price(price):
    if price == int(price):
        return str(int(price))

    return f"{price:.2f}"


def update_status(game):
    if game["quantity"] > 0:
        game["status"] = "Available"
    else:
        game["status"] = "Not Available"


def display_game(game):
    print("\nGame ID :", game["id"])
    print("Name    :", game["name"])
    print("Genre   :", game["genre"])
    print("Price   : ₱" + format_price(game["price"]))
    print("Quantity:", game["quantity"])
    print("Status  :", game["status"])


def check_quantity(game_name, game_quantity):
    games = load_games()

    for game in games:
        if game["name"].lower() == game_name.lower():
            game["quantity"] += game_quantity
            update_status(game)
            save_games(games)
            return True

    return False


def generate_game_id():
    highest_id = 0

    for game in load_games():
        game_id = game["id"]

        if game_id.startswith("G") and game_id[1:].isdigit():
            number = int(game_id[1:])

            if number > highest_id:
                highest_id = number

    return f"G{highest_id + 1:03d}"


def get_positive_float(prompt):
    while True:
        value = input(prompt).strip()

        try:
            number = float(value)

            if number > 0:
                return number
        except ValueError:
            pass

        print("Invalid input. Please enter a positive number.")


def get_positive_int(prompt):
    while True:
        value = input(prompt).strip()

        if value.isdigit() and int(value) > 0:
            return int(value)

        print("Invalid input. Please enter a positive whole number.")


def choose_genre():
    print("\nChoose a genre:")

    for index, genre in enumerate(GENRES, start=1):
        print(f"[{index}] {genre}")

    while True:
        choice = input("Enter genre number: ").strip()

        if choice.isdigit():
            choice = int(choice)

            if 1 <= choice <= len(GENRES):
                return GENRES[choice - 1]

        print("Invalid genre. Please choose from the numbered list.")


def add_game():
    game_name = input("\nEnter the name of the game: ").strip()

    while not game_name:
        print("Game name cannot be blank.")
        game_name = input("Enter the name of the game: ").strip()

    existing_game = find_game_by_name(game_name)

    if existing_game:
        print(f"\n{existing_game['name']} already exists.")
        game_quantity = get_positive_int("Enter quantity to add: ")

        if check_quantity(existing_game["name"], game_quantity):
            print("Quantity updated successfully!")
        else:
            print("Unable to update quantity.")

        return

    game_id = generate_game_id()
    selected_genre = choose_genre()
    game_price = get_positive_float("\nEnter the price of the game: ₱")
    game_quantity = get_positive_int("Enter the quantity: ")

    game = {
        "id": game_id,
        "name": game_name,
        "genre": selected_genre,
        "price": game_price,
        "quantity": game_quantity,
        "status": "Available",
    }
    update_status(game)

    with open(GAMES_FILE, "a") as file:
        file.write(
            f"{game['id']},{game['name']},{game['genre']},"
            f"{format_price(game['price'])},{game['quantity']},{game['status']}\n"
        )

    print(f"The game {game_name} has been added successfully with ID {game_id}!")


def find_game_by_name(game_name):
    for game in load_games():
        if game["name"].lower() == game_name.lower():
            return game

    return None


def view_game():
    search_value = input("\nEnter Game ID or game name: ").strip()

    for game in load_games():
        if game["id"].lower() == search_value.lower() or game["name"].lower() == search_value.lower():
            display_game(game)
            return

    print("Game not found.")


def view_all_games():
    games = load_games()

    if not games:
        print("No games found.")
        return

    print("\nAll Games")
    print("-" * 78)
    print(f"{'ID':<6}{'Name':<25}{'Genre':<28}{'Price':<10}{'Qty':<6}{'Status'}")
    print("-" * 78)

    for game in games:
        print(
            f"{game['id']:<6}{game['name']:<25}{game['genre']:<28}"
            f"₱{format_price(game['price']):<9}{game['quantity']:<6}{game['status']}"
        )


def search_game():
    search_value = input("\nEnter partial game name or genre: ").strip().lower()

    while not search_value:
        print("Search value cannot be blank.")
        search_value = input("Enter partial game name or genre: ").strip().lower()

    matches = []

    for game in load_games():
        if search_value in game["name"].lower() or search_value in game["genre"].lower():
            matches.append(game)

    if not matches:
        print("No matching games found.")
        return

    print("\nSearch Results")
    print("-" * 78)

    for game in matches:
        display_game(game)


def menu():
    while True:
        print("\nGame Rental System (LaruinMoKo)")
        print("[1] Add Game")
        print("[2] View Game")
        print("[3] View All Games")
        print("[4] Search Game")
        print("[5] Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_game()
        elif choice == "2":
            view_game()
        elif choice == "3":
            view_all_games()
        elif choice == "4":
            search_game()
        elif choice == "5":
            print("Thank you for using the Game Rental System (LaruinMoKo).")
            break
        else:
            print("Invalid choice. Please select from 1 to 5.")


addGame = add_game


if __name__ == "__main__":
    menu()
