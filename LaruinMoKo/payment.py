from datetime import datetime
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo

import storage


PHILIPPINE_TIME = ZoneInfo("Asia/Manila")


def collect_cash(amount_due):
    due = storage.normalize_money(amount_due)
    while True:
        try:
            raw_value = input(
                f"Amount due: ₱{storage.format_amount(due)}\n"
                "Enter cash received or C to cancel: "
            ).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nPayment cancelled.")
            return None

        if raw_value.casefold() == "c":
            print("Payment cancelled.")
            return None

        try:
            cash = storage.normalize_money(raw_value)
        except (ValueError, InvalidOperation) as error:
            print(f"Invalid payment: {error}")
            continue

        if cash < due:
            shortage = due - cash
            print(f"Insufficient cash. Add ₱{storage.format_amount(shortage)} or cancel.")
            continue

        return {"cash_received": cash, "change": cash - due}


def generate_payment_id(payments):
    return storage.generate_prefixed_id("P", payments, "payment_id")


def current_payment_time():
    return datetime.now(PHILIPPINE_TIME).replace(microsecond=0).isoformat()


def create_payment(
    payment_id,
    rental_id,
    game,
    renter_name,
    cash_received,
    *,
    paid_at=None,
):
    amount_due = storage.normalize_money(game["rental_price"])
    cash = storage.normalize_money(cash_received)
    if cash < amount_due:
        raise ValueError("Cash received cannot be less than the amount due.")
    return {
        "payment_id": payment_id,
        "rental_id": rental_id,
        "game_id": game["game_id"],
        "game_title": game["title"],
        "renter_name": storage.validate_text(renter_name, "Renter name"),
        "amount_due": amount_due,
        "cash_received": cash,
        "change": cash - amount_due,
        "paid_at": paid_at or current_payment_time(),
        "status": "Paid",
    }


def view_payment_records():
    try:
        payments = storage.load_payments()
    except storage.StorageError as error:
        print(f"Unable to view payment records: {error}")
        return

    if not payments:
        print("No payment records found.")
        return

    print("\nPayment Records")
    print("-" * 112)
    print(
        f"{'Payment':<10}{'Rental':<10}{'Game':<24}{'Renter':<20}"
        f"{'Due':>10}{'Cash':>10}{'Change':>10}  {'Paid At'}"
    )
    print("-" * 112)
    for item in payments:
        due = f"₱{storage.format_amount(item['amount_due'])}"
        cash = f"₱{storage.format_amount(item['cash_received'])}"
        change = f"₱{storage.format_amount(item['change'])}"
        print(
            f"{item['payment_id']:<10}{item['rental_id']:<10}"
            f"{item['game_title'][:22]:<24}{item['renter_name'][:18]:<20}"
            f"{due:>10}{cash:>10}{change:>10}  {item['paid_at']}"
        )
