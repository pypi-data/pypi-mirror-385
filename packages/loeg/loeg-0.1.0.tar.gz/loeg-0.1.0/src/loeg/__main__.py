import json
from json import JSONDecodeError
import sys
from colorama import Fore, Style, init

LABELS_TO_SHOW = ("container",)
SKIP_EVERYTHING_BEFORE = "stderr F "
WORDS_TO_COLOURS = {
    "ERROR": Fore.RED,
    "WARNING": Fore.YELLOW,
    "INFO": Fore.GREEN,
    "DEBUG": Style.DIM,
    "TRACE": Style.DIM,
}
COLOUR_FROM = "|"
MAX_LABELS_SIZE = 10


def colour(log: str) -> str:
    for word, colours in WORDS_TO_COLOURS.items():
        if word in log:
            colour_pos = log.find(COLOUR_FROM)
            if colour_pos == -1:
                colour_pos = 0
            return log[:colour_pos] + colours + log[colour_pos:] + Style.RESET_ALL
    return log


def log_cli_jsonl(line: str):
    log_data = json.loads(line)
    log: str = json.loads(log_data["line"])["log"].strip()
    if (skip_before := log.find(SKIP_EVERYTHING_BEFORE)) != -1:
        log = log[skip_before + len(SKIP_EVERYTHING_BEFORE) :]
    log = colour(log)
    log_labels = log_data.get("labels", {})
    for label in LABELS_TO_SHOW:
        if label_info := log_labels.get(label):
            log = log + f" ({label_info})"
    print(log)


def main():
    for line in sys.stdin:
        try:
            log_cli_jsonl(line)
        except (JSONDecodeError, KeyError):
            if line.strip():
                print(line, end="")


if __name__ == "__main__":
    init()
    main()
