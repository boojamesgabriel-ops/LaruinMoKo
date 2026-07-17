# This module creates and prints the terminal receipt for a successful payment.
import storage


# This function converts a payment record into a formatted receipt string.
def format_receipt(payment):
    width = 48
    lines = [
        "=" * width,
        "LARUINMOKO PS5 CD GAME RENTAL".center(width),
        "PAYMENT RECEIPT".center(width),
        "=" * width,
        f"Payment ID   : {payment['payment_id']}",
        f"Rental ID    : {payment['rental_id']}",
        f"Paid At      : {payment['paid_at']}",
        f"Renter       : {payment['renter_name']}",
        f"Game ID      : {payment['game_id']}",
        f"Game Title   : {payment['game_title']}",
        "-" * width,
        f"Amount Due   : ₱{storage.format_amount(payment['amount_due'])}",
        f"Cash Received: ₱{storage.format_amount(payment['cash_received'])}",
        f"Change       : ₱{storage.format_amount(payment['change'])}",
        f"Status       : {payment['status']}",
        "=" * width,
        "Thank you for renting with LaruinMoKo!".center(width),
        "=" * width,
    ]
    return "\n".join(lines)


# This function prints the completed payment receipt in the terminal.
def print_receipt(payment):
    print("\n" + format_receipt(payment))
