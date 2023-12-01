#!/usr/bin/env python3

import os
import requests
import time
from datetime import date


OUTPUT_DIR = "data"


def download_year(year, max_day=25):
    year_dir = os.path.join(OUTPUT_DIR, str(year))
    os.makedirs(year_dir, exist_ok=True)
    print("Downloading year", year)

    for day in range(1, max_day + 1):
        file = os.path.join(year_dir, f"day{day:02}.html")
        if os.path.isfile(file):
            print(" > Day", day, "exists")
            continue

        print(" > Day", day, "Downloading... ", end="", flush=True)
        content = requests.get(f"https://adventofcode.com/{year}/leaderboard/day/{day}")

        if not content.ok:
            print("Error", content.status_code)
            print(" >>", content.text)
            exit(-1)
        else:
            content.encoding = "utf-8"
            with open(file, "w") as f:
                f.write(content.text)
            print("Done.")

        time.sleep(1)


def main():
    today = date.today()
    for year in range(2015, today.year):
        download_year(year)

    if today.month == 12:
        download_year(today.year, min(today.day, 25))


if __name__ == "__main__":
    main()
