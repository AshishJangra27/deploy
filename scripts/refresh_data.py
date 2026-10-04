"""Fetch and validate the public NIFTY 50 CSV used by the dashboard."""

from __future__ import annotations

import csv
import io
import math
import argparse
import urllib.request
from datetime import date
from pathlib import Path

SOURCE_URL = "https://raw.githubusercontent.com/AshishJangra27/datasets/main/Nifty-50/data.csv"
EXPECTED = ["Date", "Open", "High", "Low", "Close"]
ROOT = Path(__file__).resolve().parents[1]
LOCAL_SOURCE = ROOT / "data.csv"
OUTPUT = ROOT / "src" / "public" / "nifty50.csv"


def validate(content: bytes) -> tuple[int, date, date]:
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames != EXPECTED:
        raise ValueError(f"Expected columns {EXPECTED}; received {reader.fieldnames}")

    count = 0
    first_date: date | None = None
    last_date: date | None = None
    seen: set[date] = set()
    for row_number, row in enumerate(reader, start=2):
        try:
            current_date = date.fromisoformat(row["Date"])
            open_, high, low, close = (float(row[key]) for key in EXPECTED[1:])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid date or OHLC value on CSV row {row_number}") from exc
        if current_date in seen:
            raise ValueError(f"Duplicate trading date: {current_date.isoformat()}")
        if not all(math.isfinite(value) for value in (open_, high, low, close)):
            raise ValueError(f"Non-finite OHLC value on {current_date.isoformat()}")
        if min(open_, high, low, close) <= 0:
            raise ValueError(f"Non-positive OHLC value on {current_date.isoformat()}")
        if low > min(open_, close) or high < max(open_, close) or low > high:
            raise ValueError(f"Invalid OHLC range on {current_date.isoformat()}")
        seen.add(current_date)
        first_date = current_date if first_date is None else min(first_date, current_date)
        last_date = current_date if last_date is None else max(last_date, current_date)
        count += 1

    if count == 0 or first_date is None or last_date is None:
        raise ValueError("The source CSV contains no observations")
    if count != len(seen):
        raise ValueError("Duplicate dates found")
    return count, first_date, last_date


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="refresh from the public source instead of using the checked-in data.csv",
    )
    args = parser.parse_args()
    if LOCAL_SOURCE.exists() and not args.fetch:
        content = LOCAL_SOURCE.read_bytes()
        source_label = str(LOCAL_SOURCE)
    else:
        request = urllib.request.Request(
            SOURCE_URL, headers={"User-Agent": "NiftyScope-dashboard/1.0"}
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            content = response.read()
        source_label = SOURCE_URL
    count, first_date, last_date = validate(content)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(content)
    print(
        f"Validated {count:,} observations ({first_date} to {last_date}) from "
        f"{source_label}; saved to {OUTPUT}"
    )


if __name__ == "__main__":
    main()
