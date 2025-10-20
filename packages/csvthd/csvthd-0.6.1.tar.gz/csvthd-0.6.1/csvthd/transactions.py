# built in
import csv
from functools import reduce

# package
from .reducers import concat_details
from .exceptions import EmptyTransactionFile, AmountColumnUnparsable


def _get_amount_as_float(_file, idx, row):
    _amount_raw = row[_file["amountIdx"]]
    _amount_parsable = (
        _amount_raw.replace(_file["currencyPrefix"], "")
        if "currencyPrefix" in _file
        else _amount_raw
    )
    try:
        return float(_amount_parsable)
    except ValueError as err:
        if err.args[0].startswith("could not convert string to float: "):
            raise AmountColumnUnparsable(
                str(_amount_parsable), _file["filepath"], idx
            ) from err
    except Exception as err:
        raise err


def get_transactions(files):
    transactions = []
    for _file in files:
        # set initial transaction count to 0
        transaction_count = 0

        with open(_file["filepath"], "r", newline="", encoding="utf-8") as f:
            rowreader = csv.reader(f)
            for idx, row in enumerate(rowreader):
                # skip header row if it has one
                if _file["hasHeaderRow"] is True and idx == 0:
                    continue

                # TODO: only do this when printing transactions, otherwise wasting
                # ... time concatenating transactions that are going to be filtered
                # ... out later
                # if detailsIdx is an array, perform concatenation
                _details_idx = _file["detailsIdx"]
                if type(_details_idx) is list:
                    # TODO: reflect on if this benefits enough from being a reducer
                    # ... to justify the reduction in code readability
                    _details = reduce(
                        concat_details, _details_idx, {"out": "", "row": row}
                    )["out"]
                else:
                    _details = row[_details_idx]

                _amount_float = _get_amount_as_float(_file, idx, row)

                # append transaction to array
                transactions.append(
                    {
                        "date": row[_file["dateIdx"]],
                        "amount": _amount_float,
                        "details": _details,
                        "balance_at_time_of_transaction": row[
                            _file["balanceIdx"]
                        ],
                        "account_name": _file["accountName"],
                    }
                )

                # increment transaction count
                transaction_count += 1

        # if no transactions found in CSV file
        if transaction_count < 1:
            raise EmptyTransactionFile(_file["filepath"])

    return transactions
