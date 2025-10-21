import json
import sys

from .ansi_text import (
    RESET,
    UNDERLINE,
    rgb_background,
    rgb_foreground,
)
from .models import ComputedEventModel

BG_BLACK = rgb_background(0, 0, 0)
BG_DARK_GRAY = rgb_background(30, 30, 30)
FG_YELLOW = rgb_foreground(255, 255, 0)

HEADING = " Days"


def _output_json_events(events: list[ComputedEventModel]):
    print(json.dumps([json.loads(event.model_dump_json()) for event in events]))


def _output_color_events(events: list[ComputedEventModel]):
    lines = []
    longest_line = HEADING
    for event in events:
        string_days = (
            f"{abs(event.days):.0f}" if float(int(event.days)) == event.days else f"{abs(event.days):.0f} and a butt"
        )
        match event.days:
            case 0:
                string_days = "Today is"
            case 1:
                string_days += " day until"
            case -1:
                string_days += " day since"
            case days if days > 0:
                string_days += " days until"
            case days if days < 0:
                string_days += " days since"
        line = f"{string_days} {event.title}."
        if len(line) > len(longest_line):
            longest_line = line
        lines.append(line)

    max_len = len(longest_line)
    sys.stdout.write(f"{FG_YELLOW}{UNDERLINE}{HEADING:<{max_len}}{RESET}\n")
    for i, line in enumerate(lines):
        bg = BG_BLACK if i % 2 != 0 else BG_DARK_GRAY
        sys.stdout.write(f"{bg}{line:<{max_len}}{RESET}")
        sys.stdout.write("\n")


def output_events(events: list[ComputedEventModel]):
    if sys.stdout.isatty():
        _output_color_events(events)
    else:
        _output_json_events(events)
