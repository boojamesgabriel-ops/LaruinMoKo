from datetime import date

GAMES_FILE = "games.txt"
RENTALS_FILE = "rentals.txt"  # NEW: stores every rental transaction (Drew's part)

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


# ======================================================
# GAME FILE HANDLING (Member 1's original functions)
# ======================================================
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
    # This is the "Update Game Availability" logic. It is called automatically
    # every time a game's quantity changes (after a rent or a return), so the
    # Available / Not Available status is always kept accurate.
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


def find_game_by_id_or_name(search_value):
    # NEW helper: rentals need to look games up by either ID or name.
    for game in load_games():
        if game["id"].lower() == search_value.lower() or game["name"].lower() == search_value.lower():
            return game
    return None


def view_game():
    search_value = input("\nEnter Game ID or game name: ").strip()
    game = find_game_by_id_or_name(search_value)
    if game:
        display_game(game)
    else:
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


# ======================================================
# RENTAL FILE HANDLING (Drew's part)
# rentals.txt row format:
# rental_id,game_id,game_name,renter_name,rent_date,return_date,status
# return_date is left blank while a game is still rented out.
# ======================================================
def load_rentals():
    rentals = []
    try:
        with open(RENTALS_FILE, "r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                data = line.split(",")
                if len(data) != 7:
                    continue
                rental_id, game_id, game_name, renter_name, rent_date, return_date, status = data
                rentals.append(
                    {
                        "rental_id": rental_id.strip(),
                        "game_id": game_id.strip(),
                        "game_name": game_name.strip(),
                        "renter_name": renter_name.strip(),
                        "rent_date": rent_date.strip(),
                        "return_date": return_date.strip(),
                        "status": status.strip(),
                    }
                )
    except FileNotFoundError:
        pass
    return rentals


def save_rentals(rentals):
    with open(RENTALS_FILE, "w") as file:
        for rental in rentals:
            file.write(
                f"{rental['rental_id']},{rental['game_id']},{rental['game_name']},"
                f"{rental['renter_name']},{rental['rent_date']},"
                f"{rental['return_date']},{rental['status']}\n"
            )


def generate_rental_id():
    # Same pattern as generate_game_id(), but with an "R" prefix so rental IDs
    # are easy to tell apart from game IDs (e.g. R001, R002, ...).
    highest_id = 0
    for rental in load_rentals():
        rental_id = rental["rental_id"]
        if rental_id.startswith("R") and rental_id[1:].isdigit():
            number = int(rental_id[1:])
            if number > highest_id:
                highest_id = number
    return f"R{highest_id + 1:03d}"


def get_non_blank_text(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be blank.")


def rent_game():
    print("\n--- Rent a Game ---")
    view_all_games()  # lets the renter see what's available before choosing
    search_value = input("\nEnter the Game ID or name to rent: ").strip()
    game = find_game_by_id_or_name(search_value)

    if not game:
        print("Game not found.")
        return

    if game["quantity"] <= 0:
        print(f"Sorry, {game['name']} is currently Not Available for rent.")
        return

    renter_name = get_non_blank_text("Enter renter's name: ")

    # Reduce the quantity of the rented game and refresh its availability status.
    games = load_games()
    for g in games:
        if g["id"] == game["id"]:
            g["quantity"] -= 1
            update_status(g)  # Update Game Availability happens right here
    save_games(games)

    # Log the transaction in rentals.txt.
    rental_id = generate_rental_id()
    rent_date = date.today().isoformat()
    with open(RENTALS_FILE, "a") as file:
        file.write(
            f"{rental_id},{game['id']},{game['name']},{renter_name},"
            f"{rent_date},,Rented\n"
        )

    print(f"\n{game['name']} has been rented out to {renter_name}.")
    print(f"Rental ID: {rental_id} | Date Rented: {rent_date}")


def return_game():
    print("\n--- Return a Game ---")
    rentals = load_rentals()
    active_rentals = [r for r in rentals if r["status"] == "Rented"]

    if not active_rentals:
        print("There are no active rentals to return.")
        return

    print("\nActive Rentals")
    print("-" * 70)
    print(f"{'Rental ID':<12}{'Game':<25}{'Renter':<20}{'Date Rented'}")
    print("-" * 70)
    for rental in active_rentals:
        print(
            f"{rental['rental_id']:<12}{rental['game_name']:<25}"
            f"{rental['renter_name']:<20}{rental['rent_date']}"
        )

    rental_id = input("\nEnter the Rental ID to mark as returned: ").strip()
    matched_rental = None
    for rental in rentals:
        if rental["rental_id"].lower() == rental_id.lower() and rental["status"] == "Rented":
            matched_rental = rental
            break

    if not matched_rental:
        print("Invalid Rental ID, or that rental was already returned.")
        return

    # Update the rental record: mark it Returned and stamp today's date.
    matched_rental["status"] = "Returned"
    matched_rental["return_date"] = date.today().isoformat()
    save_rentals(rentals)

    # Give the returned copy back to the games list and refresh its status.
    games = load_games()
    for g in games:
        if g["id"] == matched_rental["game_id"]:
            g["quantity"] += 1
            update_status(g)  # Update Game Availability happens right here
    save_games(games)

    print(f"\n{matched_rental['game_name']} has been returned by {matched_rental['renter_name']}.")
    print(f"Return Date: {matched_rental['return_date']}")


def view_rental_records():
    # Useful both for testing and as a screenshot for the documentation.
    rentals = load_rentals()
    if not rentals:
        print("No rental records found.")
        return
    print("\nRental Records")
    print("-" * 90)
    print(f"{'ID':<10}{'Game':<20}{'Renter':<18}{'Rented':<12}{'Returned':<12}{'Status'}")
    print("-" * 90)
    for rental in rentals:
        returned = rental["return_date"] if rental["return_date"] else "-"
        print(
            f"{rental['rental_id']:<10}{rental['game_name']:<20}{rental['renter_name']:<18}"
            f"{rental['rent_date']:<12}{returned:<12}{rental['status']}"
        )


# ======================================================
# MAIN MENU
# ======================================================
def menu():
    while True:
        print("\nGame Rental System (LaruinMoKo)")
        print("[1] Add Game")
        print("[2] View Game")
        print("[3] View All Games")
        print("[4] Search Game")
        print("[5] Rent Game")
        print("[6] Return Game")
        print("[7] View Rental Records")
        print("[8] Exit")
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
            rent_game()
        elif choice == "6":
            return_game()
        elif choice == "7":
            view_rental_records()
        elif choice == "8":
            print("Thank you for using the Game Rental System (LaruinMoKo).")
            break
        else:
            print("Invalid choice. Please select from 1 to 8.")


addGame = add_game

if __name__ == "__main__":
    menu()