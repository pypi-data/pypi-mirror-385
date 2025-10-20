from .commandline import YELLOW, ANSI_RESET

BLANK_STRING_REPLACEMENT = YELLOW + "[blank]" + ANSI_RESET


def sum_transaction_amount(acc, cur):
    # append transaction to acc so it isn't eaten after being provided by filter
    acc[0].append(cur)
    # add transaction amount to sum
    acc[1] += cur["amount"]
    # return accumulator
    return acc


def concat_details(acc, cur):
    # if item is an integer (column index), get the value from the column (ensure it's a string)
    if isinstance(cur, int):
        _details_segment = str(acc["row"][cur])
        if _details_segment == "":
            _details_segment = BLANK_STRING_REPLACEMENT
    # if item is already a string
    elif isinstance(cur, str):
        _details_segment = cur
    else:
        raise ValueError("unsupported type for item in detailsIdx array")

    # append the details segment to the end of the details string
    acc["out"] = acc["out"] + _details_segment

    return acc
