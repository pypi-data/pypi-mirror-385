from datetime import datetime

DATE_STRING_FORMAT = "%d/%m/%Y"


def details_include_filter(substrings):
    """Only return transactions matching ALL substrings (case insensitive)."""
    # lowercase all substrings
    substrings = [ss.lower() for ss in substrings]

    def _func(transaction):
        # get lowercase version of transaction details
        _details = transaction["details"].lower()

        # for each substring
        for substring in substrings:
            # if the substring isn't contained in details
            if not substring in _details:
                return False
        # if not substrings haven't matched transaction details
        return True

    return _func


def details_exclude_filter(substrings):
    """Only return transactions that DON'T match ANY substrings (case insensitive)."""
    # lowercase all substrings
    substrings = [ss.lower() for ss in substrings]

    def _func(transaction):
        # get lowercase version of transaction details
        _details = transaction["details"].lower()

        # for each substring
        for substring in substrings:
            # if the substring isn't contained in details
            if substring in _details:
                return False
        # if not substrings haven't matched transaction details
        return True

    return _func


def amount_is_filter(operator, value):
    """Filter out transactions based on amounts.

    Operator is `under`, `over` or `equal`.
    Value is a float.
    """

    value = float(value)

    def _func(transaction):
        # convert amount to float
        _amount = float(transaction["amount"])

        if operator == "under":
            # if amount under zero, flip sign for comparison
            _amount = abs(_amount)
            return _amount < value
        elif operator == "over":
            # if amount under zero, flip sign for comparison
            _amount = abs(_amount)
            return _amount > value
        elif operator == "equal":
            return _amount == value
        else:
            raise ValueError("Operator must by `above`, `below` or `equal`")

    return _func


def date_filter(operator, date_str):
    """Filter out transactions based on dates.

    Operator is `before`, `after` or `on`.
    Date is a string of format DD/MM/YYYY.
    """

    # convert date_str to unix timestamp for simple comparison
    _filter_timestamp = datetime.strptime(
        date_str, DATE_STRING_FORMAT
    ).timestamp()

    def _func(transaction):
        # convert transaction date to timestamp for simple comparison
        _trans_timestamp = datetime.strptime(
            transaction["date"], DATE_STRING_FORMAT
        ).timestamp()

        if operator == "before":
            return _trans_timestamp <= _filter_timestamp
        elif operator == "after":
            return _trans_timestamp >= _filter_timestamp
        elif operator == "on":
            return _trans_timestamp == _filter_timestamp
        else:
            raise ValueError("Operator must by `before`, `after` or `on`")

    return _func


def transaction_type_filter(transaction_type):
    """Only return transactions of a give type (i.e. money sent/recieved)."""

    def _func(transaction):
        # convert amount to float
        _amount = float(transaction["amount"])

        if transaction_type == "out":
            return _amount < 0
        elif transaction_type == "in":
            return _amount >= 0
        else:
            raise ValueError("transaction_type must by `in` or `out`")

    return _func


def account_name_filter(account_name):
    """Only return transactions with account names that contain the provided string."""

    # transform account name to lowercase for comparison
    _account_name = account_name.lower()

    def _func(transaction):
        return _account_name in transaction["account_name"].lower()

    return _func
