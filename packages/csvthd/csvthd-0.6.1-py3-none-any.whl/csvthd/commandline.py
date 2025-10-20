RED = "\033[31m"
YELLOW = "\033[33m"
RED_BACK = "\033[41m"
GREEN_BACK = "\033[42m"
ANSI_RESET = "\033[0m"


def style_amount(amount):
    AMOUNT_COLOUR = RED_BACK if amount < 0 else GREEN_BACK
    return f"{AMOUNT_COLOUR}{amount:>8.2f}{ANSI_RESET}"


def print_transaction(transaction):
    _amount = transaction["amount"]

    print(
        # TODO: find the longest account name string and use it change string formatting padding size
        f"[{transaction['account_name']:^25}] "
        + transaction["date"]
        + " | AMT: "
        + style_amount(_amount)
        + " | "
        + transaction["details"]
    )
