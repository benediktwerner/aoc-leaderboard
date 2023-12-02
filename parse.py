#!/usr/bin/env python3

import html
import json
import os
import re
import time
from collections import defaultdict


DATA_DIR = "data"
OUT_DIR = "docs/json"

NO_POINTS = [(2020, 1), (2018, 6)]


def parse_year(year, users):
    points = defaultdict(int)
    ranks = defaultdict(list)

    year_dir = os.path.join(DATA_DIR, str(year))

    for day_file in os.listdir(year_dir):
        day = int(re.fullmatch(r"^day(\d\d).html$", day_file)[1])
        with open(os.path.join(year_dir, day_file)) as f:
            content = f.read()
            start = content.find(
                '<p>First hundred users to get <span class="leaderboard-daydesc-both">both stars</span>'
            )
            middle = content.find(
                '<p>First hundred users to get the <span class="leaderboard-daydesc-first">first star</span>'
            )
            end = content.find("</main>")

            assert start > 0
            assert middle > 0
            assert end > 0

            first = content[start:middle].split("\n")
            second = content[middle:end].split("\n")[:-1]

            for i, line in enumerate(first):
                user_id = re.findall(r'data-user-id="(\d+)"', line)[0]
                if (year, day) not in NO_POINTS:
                    points[user_id] += 100 - i
                ranks[user_id].append((day, 2, i + 1))

                start = line.rfind("anonymous user")
                if start != -1:
                    end = line.find(")", start)
                else:
                    start = line.rfind("</span>") + len("</span>")
                    end = line.find("<", start)
                users[user_id]["name"] = html.unescape(line[start:end])
                img = re.search(r'<img src="(.+?)"', line)
                if img:
                    users[user_id]["img"] = img[1]

            for i, line in enumerate(second):
                user_id = re.findall(r'data-user-id="(\d+)"', line)[0]
                if (year, day) not in NO_POINTS:
                    points[user_id] += 100 - i
                ranks[user_id].append((day, 1, i + 1))

                start = line.rfind("anonymous user")
                if start != -1:
                    end = line.find(")", start)
                else:
                    start = line.rfind("</span>") + len("</span>")
                    end = line.find("<", start)
                users[user_id]["name"] = html.unescape(line[start:end])
                img = re.search(r'<img src="(.+?)"', line)
                if img:
                    users[user_id]["img"] = img[1]

    people = {}
    for user_id in points.keys():
        people[user_id] = {
            "points": points[user_id],
            "ranks": ranks[user_id],
        }

    path = os.path.join(OUT_DIR, f"{year}.json")
    with open(path, "w") as f:
        json.dump(people, f)

    print(f"Written to '{path}'")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    years = sorted(os.listdir(DATA_DIR))
    users = defaultdict(dict)

    for year in years:
        print("Parsing year", year)
        parse_year(int(year), users)

    path = os.path.join(OUT_DIR, "meta.json")
    with open(path, "w") as f:
        json.dump(
            {
                "years": list(map(int, years)),
                "updated": int(time.time() * 1000),
                "no_points": NO_POINTS,
                "users": users,
            },
            f,
        )

    print(f"Written metadata to '{path}'")


if __name__ == "__main__":
    main()
