from __future__ import annotations

import os
import tempfile
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable


BASE_DIR = Path(__file__).resolve().parent
GAMES_FILE = BASE_DIR / "games.txt"
RENTALS_FILE = BASE_DIR / "rentals.txt"
PAYMENTS_FILE = BASE_DIR / "payments.txt"

MONEY_PLACES = Decimal("0.01")


class StorageError(Exception):
    pass


class DataFormatError(StorageError):
    pass


def validate_text(value, field_name="Value"):
    text = str(value).strip()
    if not text:
        raise ValueError(f"{field_name} cannot be blank.")
    if "|" in text or "\n" in text or "\r" in text:
        raise ValueError(f"{field_name} cannot contain | or a new line.")
    return text


def normalize_money(value, *, positive=True):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("Amount must be a valid number.") from None

    if not amount.is_finite():
        raise ValueError("Amount must be a finite number.")
    if positive and amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    if not positive and amount < 0:
        raise ValueError("Amount cannot be negative.")
    if amount != amount.quantize(MONEY_PLACES):
        raise ValueError("Amount can have at most two decimal places.")
    return amount.quantize(MONEY_PLACES)


def format_amount(value):
    return f"{normalize_money(value, positive=False):.2f}"


def availability_for(quantity):
    return "Available" if quantity > 0 else "Unavailable"


def _read_records(path: Path, expected_fields: int):
    if not path.exists():
        return []

    records = []
    try:
        with path.open("r", encoding="utf-8") as file:
            for line_number, raw_line in enumerate(file, start=1):
                line = raw_line.rstrip("\n\r")
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) != expected_fields:
                    raise DataFormatError(
                        f"Invalid record in {path.name} on line {line_number}: "
                        f"expected {expected_fields} fields."
                    )
                records.append((line_number, parts))
    except UnicodeError as error:
        raise StorageError(f"Unable to decode {path.name}: {error}") from error
    except OSError as error:
        raise StorageError(f"Unable to read {path.name}: {error}") from error
    return records


def load_games(path=None):
    file_path = Path(path) if path is not None else GAMES_FILE
    games = []
    for line_number, parts in _read_records(file_path, 6):
        game_id, title, genre, price_text, quantity_text, _availability = parts
        try:
            game_id = validate_text(game_id, "Game ID")
            if not game_id.isdigit():
                raise ValueError("Game ID must be numeric.")
            title = validate_text(title, "Title")
            genre = validate_text(genre, "Genre")
            rental_price = normalize_money(price_text)
            quantity = int(quantity_text)
            if quantity < 0:
                raise ValueError("Quantity cannot be negative.")
        except (ValueError, InvalidOperation) as error:
            raise DataFormatError(
                f"Invalid game in {file_path.name} on line {line_number}: {error}"
            ) from error

        games.append(
            {
                "game_id": game_id,
                "title": title,
                "genre": genre,
                "rental_price": rental_price,
                "quantity": quantity,
                "availability": availability_for(quantity),
            }
        )
    return games


def load_rentals(path=None):
    file_path = Path(path) if path is not None else RENTALS_FILE
    rentals = []
    for line_number, parts in _read_records(file_path, 7):
        rental_id, game_id, game_title, renter_name, rent_date, return_date, status = parts
        try:
            rental_id = validate_text(rental_id, "Rental ID")
            game_id = validate_text(game_id, "Game ID")
            game_title = validate_text(game_title, "Game title")
            renter_name = validate_text(renter_name, "Renter name")
            rent_date = validate_text(rent_date, "Rent date")
            if status not in {"Rented", "Returned"}:
                raise ValueError("Status must be Rented or Returned.")
            if status == "Returned" and not return_date.strip():
                raise ValueError("Returned rentals require a return date.")
            if return_date:
                validate_text(return_date, "Return date")
        except ValueError as error:
            raise DataFormatError(
                f"Invalid rental in {file_path.name} on line {line_number}: {error}"
            ) from error

        rentals.append(
            {
                "rental_id": rental_id,
                "game_id": game_id,
                "game_title": game_title,
                "renter_name": renter_name,
                "rent_date": rent_date,
                "return_date": return_date.strip(),
                "status": status,
            }
        )
    return rentals


def load_payments(path=None):
    file_path = Path(path) if path is not None else PAYMENTS_FILE
    payments = []
    for line_number, parts in _read_records(file_path, 10):
        (
            payment_id,
            rental_id,
            game_id,
            game_title,
            renter_name,
            amount_due,
            cash_received,
            change,
            paid_at,
            status,
        ) = parts
        try:
            payment_id = validate_text(payment_id, "Payment ID")
            rental_id = validate_text(rental_id, "Rental ID")
            game_id = validate_text(game_id, "Game ID")
            game_title = validate_text(game_title, "Game title")
            renter_name = validate_text(renter_name, "Renter name")
            amount_due = normalize_money(amount_due)
            cash_received = normalize_money(cash_received)
            change = normalize_money(change, positive=False)
            paid_at = validate_text(paid_at, "Payment time")
            if status != "Paid":
                raise ValueError("Payment status must be Paid.")
            if cash_received - amount_due != change:
                raise ValueError("Recorded payment change is inconsistent.")
        except ValueError as error:
            raise DataFormatError(
                f"Invalid payment in {file_path.name} on line {line_number}: {error}"
            ) from error

        payments.append(
            {
                "payment_id": payment_id,
                "rental_id": rental_id,
                "game_id": game_id,
                "game_title": game_title,
                "renter_name": renter_name,
                "amount_due": amount_due,
                "cash_received": cash_received,
                "change": change,
                "paid_at": paid_at,
                "status": status,
            }
        )
    return payments


def _serialize_games(games):
    lines = []
    for game in games:
        game_id = validate_text(game["game_id"], "Game ID")
        if not game_id.isdigit():
            raise ValueError("Game ID must be numeric.")
        title = validate_text(game["title"], "Title")
        genre = validate_text(game["genre"], "Genre")
        price = format_amount(game["rental_price"])
        quantity = int(game["quantity"])
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")
        lines.append(
            "|".join(
                [game_id, title, genre, price, str(quantity), availability_for(quantity)]
            )
        )
    return lines


def _serialize_rentals(rentals):
    lines = []
    for rental in rentals:
        status = rental["status"]
        return_date = str(rental.get("return_date", "")).strip()
        if status not in {"Rented", "Returned"}:
            raise ValueError("Rental status must be Rented or Returned.")
        if status == "Returned" and not return_date:
            raise ValueError("Returned rentals require a return date.")
        fields = [
            validate_text(rental["rental_id"], "Rental ID"),
            validate_text(rental["game_id"], "Game ID"),
            validate_text(rental["game_title"], "Game title"),
            validate_text(rental["renter_name"], "Renter name"),
            validate_text(rental["rent_date"], "Rent date"),
            return_date,
            status,
        ]
        if return_date:
            validate_text(return_date, "Return date")
        lines.append("|".join(fields))
    return lines


def _serialize_payments(payments):
    lines = []
    for payment in payments:
        if payment["status"] != "Paid":
            raise ValueError("Only paid transactions can be stored.")
        amount_due = normalize_money(payment["amount_due"])
        cash_received = normalize_money(payment["cash_received"])
        change = normalize_money(payment["change"], positive=False)
        if cash_received - amount_due != change:
            raise ValueError("Payment change is inconsistent.")
        lines.append(
            "|".join(
                [
                    validate_text(payment["payment_id"], "Payment ID"),
                    validate_text(payment["rental_id"], "Rental ID"),
                    validate_text(payment["game_id"], "Game ID"),
                    validate_text(payment["game_title"], "Game title"),
                    validate_text(payment["renter_name"], "Renter name"),
                    format_amount(amount_due),
                    format_amount(cash_received),
                    format_amount(change),
                    validate_text(payment["paid_at"], "Payment time"),
                    "Paid",
                ]
            )
        )
    return lines


def _text_for(lines: Iterable[str]):
    materialized = list(lines)
    return "" if not materialized else "\n".join(materialized) + "\n"


def _write_temp(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="",
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
        delete=False,
    )
    try:
        with handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        return Path(handle.name)
    except Exception:
        Path(handle.name).unlink(missing_ok=True)
        raise


def _atomic_write_group(files):
    originals = {}
    temporary = {}
    replaced = []
    try:
        for path, text in files.items():
            path = Path(path)
            originals[path] = path.read_bytes() if path.exists() else None
            temporary[path] = _write_temp(path, text)

        for path, temp_path in temporary.items():
            os.replace(temp_path, path)
            replaced.append(path)
        return True
    except (OSError, ValueError) as error:
        rollback_errors = []
        for path in reversed(replaced):
            try:
                original = originals[path]
                if original is None:
                    path.unlink(missing_ok=True)
                else:
                    restore = tempfile.NamedTemporaryFile(
                        mode="wb", prefix=f".{path.name}.restore.", dir=path.parent, delete=False
                    )
                    with restore:
                        restore.write(original)
                        restore.flush()
                        os.fsync(restore.fileno())
                    os.replace(restore.name, path)
            except OSError as rollback_error:
                rollback_errors.append(str(rollback_error))
        detail = f"Unable to save application data: {error}"
        if rollback_errors:
            detail += " Rollback also failed: " + "; ".join(rollback_errors)
        raise StorageError(detail) from error
    finally:
        for temp_path in temporary.values():
            temp_path.unlink(missing_ok=True)


def save_games(games):
    try:
        return _atomic_write_group({GAMES_FILE: _text_for(_serialize_games(games))})
    except ValueError as error:
        raise StorageError(f"Unable to save games.txt: {error}") from error


def save_rentals(rentals):
    try:
        return _atomic_write_group({RENTALS_FILE: _text_for(_serialize_rentals(rentals))})
    except ValueError as error:
        raise StorageError(f"Unable to save rentals.txt: {error}") from error


def save_payments(payments):
    try:
        return _atomic_write_group({PAYMENTS_FILE: _text_for(_serialize_payments(payments))})
    except ValueError as error:
        raise StorageError(f"Unable to save payments.txt: {error}") from error


def save_rental_transaction(games, rentals, payments):
    try:
        return _atomic_write_group(
            {
                GAMES_FILE: _text_for(_serialize_games(games)),
                RENTALS_FILE: _text_for(_serialize_rentals(rentals)),
                PAYMENTS_FILE: _text_for(_serialize_payments(payments)),
            }
        )
    except ValueError as error:
        raise StorageError(f"Unable to complete rental: {error}") from error


def save_return_transaction(games, rentals):
    try:
        return _atomic_write_group(
            {
                GAMES_FILE: _text_for(_serialize_games(games)),
                RENTALS_FILE: _text_for(_serialize_rentals(rentals)),
            }
        )
    except ValueError as error:
        raise StorageError(f"Unable to complete return: {error}") from error


def generate_numeric_game_id(games):
    numeric_ids = [int(game["game_id"]) for game in games if str(game["game_id"]).isdigit()]
    return str(max(numeric_ids, default=100) + 1)


def generate_prefixed_id(prefix, records, key):
    highest = 0
    for record in records:
        value = str(record.get(key, ""))
        if value.startswith(prefix) and value[len(prefix) :].isdigit():
            highest = max(highest, int(value[len(prefix) :]))
    return f"{prefix}{highest + 1:03d}"


def find_game(games, search_value):
    search = str(search_value).strip().casefold()
    for game in games:
        if game["game_id"].casefold() == search or game["title"].casefold() == search:
            return game
    return None
