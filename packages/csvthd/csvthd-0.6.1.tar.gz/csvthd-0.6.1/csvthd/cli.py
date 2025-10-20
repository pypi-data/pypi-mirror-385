# built in
from datetime import datetime
from functools import reduce
import os

# site
import click

# package
from .filters import (
    details_include_filter,
    details_exclude_filter,
    amount_is_filter,
    date_filter,
    transaction_type_filter,
    account_name_filter,
)
from .commandline import (
    print_transaction,
    style_amount,
    RED,
    ANSI_RESET,
    YELLOW,
)
from .transactions import get_transactions
from .config import load_config
from .reducers import sum_transaction_amount
from .exceptions import EmptyTransactionFile, AmountColumnUnparsable

# TODO: consider looking into (odx?) other formats because someone mentioned apparently there
# ... are some other commons ones that are standardized.

DEFAULT_CONFIG_FILEPATH = "./config.json"


@click.command()
@click.option(
    "-i",
    "--include",
    multiple=True,
    help="Only show transactions that contain the given substring in their details.",
)
@click.option(
    "-E",
    "--exclude",
    multiple=True,
    help="Only show transactions that don't contain the given substring in their details.",
)
@click.option(
    "-a",
    "--amount",
    multiple=True,
    nargs=2,
    help="Only show transactions with amounts under/over/equal to value.",
)
@click.option(
    "-d",
    "--date",
    multiple=True,
    nargs=2,
    help="Only show transactions before/after/on given date",
)
@click.option(
    "-t",
    "--transaction-type",
    type=click.Choice(["out", "in"]),
    help="Only show transactions where money is sent/received.",
)
@click.option(
    "-A",
    "--account-name",
    help="Only show transactions from account names that include this text.",
)
@click.option(
    "-s",
    "--sort-by",
    type=click.Choice(["date", "amount"]),
    default="date",
    help="Sort transactions by given property.",
)
@click.option(
    "-r", "--reverse-sort", is_flag=True, help="Reverse sorting order."
)
@click.option(
    "-S",
    "--sum",
    is_flag=True,
    help="Give a sum of all transaction amounts after filtering.",
)
def cli(
    include,
    exclude,
    amount,
    date,
    transaction_type,
    account_name,
    sort_by,
    reverse_sort,
    sum,
):
    # set config filepath based on env var if defined, otherwise use default
    config_filepath = os.environ.get(
        "CSVTHD_CONFIG_FILEPATH", DEFAULT_CONFIG_FILEPATH
    )

    filters = []

    # create transaction type filter
    if transaction_type is not None:
        filters.append(transaction_type_filter(transaction_type))

    # create account name filter
    if account_name is not None:
        filters.append(account_name_filter(account_name))

    # create date filters
    [filters.append(date_filter(_d[0], _d[1])) for _d in date]

    # create include filters
    filters.append(details_include_filter(include))

    # create exclude filters
    filters.append(details_exclude_filter(exclude))

    # create amount filters
    [filters.append(amount_is_filter(_amt[0], _amt[1])) for _amt in amount]

    config = load_config(config_filepath)

    try:
        transactions = get_transactions(config["files"])
    except EmptyTransactionFile as err:
        print(
            f"{RED}ERROR: Transaction file doesn't contain any transactions: {err.filepath}{ANSI_RESET}"
        )
        exit(1)
    except AmountColumnUnparsable as err:
        print(
            RED
            + "ERROR: Failed to convert this into a number: '"
            + str(err._input)
            + "'\n  File: '"
            + str(err.filepath)
            + "'\n  Row number: #"
            + str(err.row_index + 1)
            + "   (1-based index)\n\n"
            + YELLOW
            + "TIP: You may need to set a 'currencyPrefix'"
            + " for this file if there's a $ or € in the amount column values."
            + ANSI_RESET
        )
        exit(1)

    # sort transactions
    if sort_by == "date":
        transactions.sort(
            key=lambda t: datetime.strptime(t["date"], "%d/%m/%Y").timestamp(),
            reverse=reverse_sort,
        )
    elif sort_by == "amount":
        transactions.sort(key=lambda t: t["amount"], reverse=reverse_sort)
    else:
        raise ValueError("Invalid 'sort_by' type")

    # apply all filters
    for _filter in filters:
        transactions = filter(_filter, transactions)

    # calculate sum
    sum_amount = None
    if sum:
        transactions, sum_amount = reduce(
            sum_transaction_amount, transactions, [[], 0]
        )

    print("---[ TRANSACTIONS ]---")
    for transaction in transactions:
        print_transaction(transaction)

    # if sum calculated, print it
    if sum_amount is not None:
        print("---[ REPORTS ]---")
        print(f" | SUM AMT: {style_amount(sum_amount)} |")

    if len(filters) == 0:
        print("\nHint: Use `--help` to learn how to filter transactions.")
