# built in
import json

# package
from .commandline import RED, YELLOW, ANSI_RESET

GETTING_STARTED_DOCS_URL = "https://gitlab.com/DrTexx/csv-transaction-history-detective/#getting-started"


def load_config(config_filepath):
    try:
        with open(config_filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    # if config.json file is missing
    except FileNotFoundError:
        # print error message
        print(
            RED
            + "ERROR: Failed to find your `config.json` file at '"
            + config_filepath
            + "'."
            + YELLOW
            + "\n\nFor help and usage instructions, see: "
            + ANSI_RESET
            + GETTING_STARTED_DOCS_URL
        )
        # return non-zero exit code
        exit(1)
    except json.decoder.JSONDecodeError as err:
        # print error message
        print(
            RED
            + "ERROR: Failed to parse your `config.json` file from '"
            + config_filepath
            + "': "
            + str(err)
            + YELLOW
            + "\n\nTip:"
            + ANSI_RESET
            + " If you continue having decoding issues, try using a JSON validator to check your config is structured correctly."
            + YELLOW
            + "\n\nFor help and usage instructions, see: "
            + ANSI_RESET
            + GETTING_STARTED_DOCS_URL
        )
        # return non-zero exit code
        exit(1)
