#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "files/voter_responses_exit_polls_voteabroad_info_russia_presidential_election_20240317_v3.csv"
OUTPUT = ROOT / "files/results-summary-2024.json"


COUNTRIES = {
    32: "Argentina",
    36: "Australia",
    40: "Austria",
    51: "Armenia",
    56: "Belgium",
    124: "Canada",
    188: "Costa Rica",
    191: "Croatia",
    196: "Cyprus",
    203: "Czechia",
    208: "Denmark",
    233: "Estonia",
    246: "Finland",
    250: "France",
    276: "Germany",
    300: "Greece",
    348: "Hungary",
    372: "Ireland",
    376: "Israel",
    380: "Italy",
    392: "Japan",
    398: "Kazakhstan",
    417: "Kyrgyzstan",
    440: "Lithuania",
    442: "Luxembourg",
    498: "Moldova",
    499: "Montenegro",
    528: "Netherlands",
    554: "New Zealand",
    578: "Norway",
    616: "Poland",
    620: "Portugal",
    688: "Serbia",
    703: "Slovakia",
    704: "Vietnam",
    724: "Spain",
    752: "Sweden",
    756: "Switzerland",
    764: "Thailand",
    784: "UAE",
    792: "Turkey",
    826: "Great Britain",
    840: "USA",
    860: "Uzbekistan",
}


CITIES = {
    32001: "Buenos Aires",
    36001: "Sydney",
    40001: "Salzburg",
    40002: "Vienna",
    51001: "Yerevan",
    51002: "Gyumri",
    56001: "Brussels",
    124001: "Toronto",
    124002: "Montreal",
    124003: "Ottawa",
    188001: "San Jose",
    191001: "Zagreb",
    194001: "Nicosia",
    203001: "Prague",
    208001: "Copenhagen",
    233001: "Tallinn",
    246001: "Helsinki",
    250001: "Paris",
    250002: "Strasbourg",
    276001: "Berlin",
    276002: "Bonn",
    300001: "Athens",
    348001: "Budapest",
    372001: "Dublin",
    376001: "Haifa / Jerusalem",
    376002: "Tel Aviv",
    380001: "Rome",
    380002: "Milan",
    380003: "Genoa",
    392001: "Tokyo",
    398001: "Almaty",
    417001: "Bishkek",
    440001: "Vilnius",
    442001: "Luxembourg",
    498001: "Chisinau",
    499001: "Podgorica",
    528001: "The Hague",
    554002: "Wellington",
    578001: "Oslo",
    616001: "Warsaw",
    616002: "Krakow",
    616003: "Gdansk",
    616004: "Poznan",
    620001: "Lisbon",
    688001: "Belgrade",
    703001: "Bratislava",
    704001: "Hanoi",
    724001: "Barcelona",
    724002: "Madrid",
    752001: "Stockholm",
    756001: "Bern",
    756002: "Geneva",
    764001: "Bangkok",
    784001: "Dubai",
    792001: "Ankara",
    792002: "Istanbul",
    792003: "Antalya",
    792004: "Trabzon",
    826001: "London",
    840001: "New York",
    860001: "Tashkent",
    860002: "Samarkand",
}


CANDIDATES = [
    {"key": "no_answer", "code": 0, "name_ru": "Не хочу отвечать", "name_en": "No answer"},
    {"key": "davankov", "code": 1, "name_ru": "В. А. Даванков", "name_en": "V. A. Davankov"},
    {"key": "putin", "code": 2, "name_ru": "В. В. Путин", "name_en": "V. V. Putin"},
    {"key": "slutsky", "code": 3, "name_ru": "Л. В. Слуцкий", "name_en": "L. V. Slutsky"},
    {"key": "kharitonov", "code": 4, "name_ru": "Н. М. Харитонов", "name_en": "N. M. Kharitonov"},
    {"key": "invalid", "code": 5, "name_ru": "Недействительный бюллетень", "name_en": "Invalid ballot"},
    {"key": "removed", "code": 6, "name_ru": "Бюллетень унесен/выброшен/порван", "name_en": "Ballot removed"},
]


CANDIDATE_BY_CODE = {item["code"]: item for item in CANDIDATES}
CANDIDATE_KEYS = [item["key"] for item in CANDIDATES]


def empty_counts():
    return {key: 0 for key in CANDIDATE_KEYS}


def add_response(bucket, candidate_key):
    bucket["responses"] += 1
    bucket["candidates"][candidate_key] += 1


def sorted_items(mapping):
    return sorted(mapping.values(), key=lambda item: (-item["responses"], item["name"], item.get("code", 0)))


def main():
    totals = {
        "responses": 0,
        "countries": 0,
        "cities": 0,
        "stations": 0,
        "candidates": empty_counts(),
    }
    latest_timestamp = 0
    countries = {}
    cities = {}
    stations = {}

    with SOURCE.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        for row in reader:
            country_code = int(row["country"])
            city_code = int(row["city"])
            station_code = int(row["voting_station"])
            latest_timestamp = max(latest_timestamp, int(row["timestamp"]))
            candidate_code = int(row["candidate"])
            candidate = CANDIDATE_BY_CODE.get(candidate_code, CANDIDATE_BY_CODE[0])
            candidate_key = candidate["key"]

            totals["responses"] += 1
            totals["candidates"][candidate_key] += 1

            country_name = COUNTRIES.get(country_code, f"Country {country_code}")
            city_name = CITIES.get(city_code, f"City {city_code}")

            country_bucket = countries.setdefault(
                country_code,
                {
                    "code": country_code,
                    "name": country_name,
                    "responses": 0,
                    "candidates": empty_counts(),
                },
            )
            add_response(country_bucket, candidate_key)

            city_bucket = cities.setdefault(
                city_code,
                {
                    "code": city_code,
                    "name": city_name,
                    "country_code": country_code,
                    "country_name": country_name,
                    "responses": 0,
                    "candidates": empty_counts(),
                },
            )
            add_response(city_bucket, candidate_key)

            station_bucket = stations.setdefault(
                station_code,
                {
                    "code": station_code,
                    "name": str(station_code),
                    "city_code": city_code,
                    "city_name": city_name,
                    "country_code": country_code,
                    "country_name": country_name,
                    "responses": 0,
                    "candidates": empty_counts(),
                },
            )
            add_response(station_bucket, candidate_key)

    totals["countries"] = len(countries)
    totals["cities"] = len(cities)
    totals["stations"] = len(stations)

    summary = {
        "generated_at": datetime.fromtimestamp(latest_timestamp, timezone.utc).replace(microsecond=0).isoformat(),
        "election": {
            "name_ru": "Выборы Президента Российской Федерации",
            "name_en": "Russian presidential election",
            "date": "2024-03-17",
        },
        "source": {
            "csv": "files/voter_responses_exit_polls_voteabroad_info_russia_presidential_election_20240317_v3.csv",
            "notes": "files/voter_responses_exit_polls_voteabroad_info_russia_presidential_election_20240317_v3.txt",
        },
        "candidates": CANDIDATES,
        "totals": totals,
        "countries": sorted_items(countries),
        "cities": sorted_items(cities),
        "stations": sorted_items(stations),
    }

    OUTPUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
