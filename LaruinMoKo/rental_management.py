from datetime import date

import payment
import receipt
import storage
from game_catalog import display_games, get_safe_text


def generate_rental_id(rentals=None):
    if rentals is None:
        rentals = storage.load_rentals()
    return storage.generate_prefixed_id("R", rentals, "rental_id")


def rent_game():
    try:
        games = storage.load_games()
        rentals = storage.load_rentals()
        payments = storage.load_payments()

        available_games = [game for game in games if game["quantity"] > 0]
        print("\n--- Rent a Game ---")
        display_games(available_games)
        if not available_games:
            print("There are no games available for rent.")
            return

        search_value = get_safe_text(
            "Enter the Game ID or title to rent: ", "Game selection"
        )
        game = storage.find_game(games, search_value)
        if game is None:
            print("Game not found.")
            return
        if game["quantity"] <= 0:
            print(f"{game['title']} is currently unavailable for rent.")
            return

        renter_name = get_safe_text("Enter renter's name: ", "Renter name")
        payment_result = payment.collect_cash(game["rental_price"])
        if payment_result is None:
            return

        rental_id = generate_rental_id(rentals)
        payment_id = payment.generate_payment_id(payments)
        rental = {
            "rental_id": rental_id,
            "game_id": game["game_id"],
            "game_title": game["title"],
            "renter_name": renter_name,
            "rent_date": date.today().isoformat(),
            "return_date": "",
            "status": "Rented",
        }
        payment_record = payment.create_payment(
            payment_id,
            rental_id,
            game,
            renter_name,
            payment_result["cash_received"],
        )

        game["quantity"] -= 1
        game["availability"] = storage.availability_for(game["quantity"])
        rentals.append(rental)
        payments.append(payment_record)
        storage.save_rental_transaction(games, rentals, payments)

        print(f"\n{game['title']} was rented successfully.")
        receipt.print_receipt(payment_record)
    except storage.StorageError as error:
        print(f"Rental could not be completed: {error}")


def return_game():
    try:
        rentals = storage.load_rentals()
        active = [rental for rental in rentals if rental["status"] == "Rented"]
        if not active:
            print("There are no active rentals to return.")
            return

        print("\nActive Rentals")
        print("-" * 82)
        print(f"{'Rental ID':<12}{'Game':<28}{'Renter':<24}{'Date Rented'}")
        print("-" * 82)
        for rental in active:
            print(
                f"{rental['rental_id']:<12}{rental['game_title'][:26]:<28}"
                f"{rental['renter_name'][:22]:<24}{rental['rent_date']}"
            )

        rental_id = get_safe_text(
            "Enter the Rental ID to return: ", "Rental ID"
        ).casefold()
        rental = next(
            (
                item
                for item in active
                if item["rental_id"].casefold() == rental_id
            ),
            None,
        )
        if rental is None:
            print("Invalid Rental ID, or that rental was already returned.")
            return

        games = storage.load_games()
        game = next(
            (item for item in games if item["game_id"] == rental["game_id"]), None
        )
        if game is None:
            print("Return cannot be completed because the game record is missing.")
            return

        rental["status"] = "Returned"
        rental["return_date"] = date.today().isoformat()
        game["quantity"] += 1
        game["availability"] = storage.availability_for(game["quantity"])
        storage.save_return_transaction(games, rentals)
        print(f"\n{rental['game_title']} was returned successfully.")
        print(f"Return Date: {rental['return_date']}")
    except storage.StorageError as error:
        print(f"Return could not be completed: {error}")


def view_rental_records():
    try:
        rentals = storage.load_rentals()
    except storage.StorageError as error:
        print(f"Unable to view rental records: {error}")
        return

    if not rentals:
        print("No rental records found.")
        return

    print("\nRental Records")
    print("-" * 98)
    print(
        f"{'ID':<10}{'Game':<26}{'Renter':<22}"
        f"{'Rented':<14}{'Returned':<14}{'Status'}"
    )
    print("-" * 98)
    for rental in rentals:
        returned = rental["return_date"] or "-"
        print(
            f"{rental['rental_id']:<10}{rental['game_title'][:24]:<26}"
            f"{rental['renter_name'][:20]:<22}{rental['rent_date']:<14}"
            f"{returned:<14}{rental['status']}"
        )
