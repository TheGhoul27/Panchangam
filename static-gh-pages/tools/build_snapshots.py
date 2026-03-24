import argparse
import json
from datetime import date, timedelta
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.scraper import get_panchangam  # noqa: E402


CITY_MAP = {
    "Atlanta, USA": "Atlanta",
    "Chicago, USA": "Chicago",
    "Houston, USA": "Houston",
    "New Jersey, USA": "New+Jersey",
    "New York, USA": "New+York",
    "Toronto, Ontario, Canada": "Toronto",
    "London, UK": "London",
    "Edinburgh, UK": "Edinburgh",
    "Sydney, Australia": "Sydney",
    "Melbourne, Australia": "Melbourne",
    "Perth, Australia": "Perth",
    "Durban, South Africa": "Durban",
    "Cape Town, South Africa": "Cape+Town",
    "Munich, Germany": "Munich",
    "Singapore, Singapore": "Singapore",
    "Kuala Lumpur, Malaysia": "Kuala+Lumpur",
    "Dubai, UAE": "Dubai",
    "Bangkok, Thailand": "Bangkok",
    "Hongkong, China": "Hongkong",
    "Riyadh, Saudi Arabia": "Riyadh",
    "Doha, Qatar": "Doha",
    "Kuwait City, Kuwait": "Kuwait",
    "Hamilton, New Zealand": "Hamilton",
    "Auckland, New Zealand": "Auckland"
}


def parse_args():
    parser = argparse.ArgumentParser(description="Build pre-generated Panchangam snapshots for static hosting.")
    parser.add_argument("--days", type=int, default=7, help="Number of days from today to generate.")
    parser.add_argument(
        "--cities",
        nargs="*",
        default=["New York, USA", "London, UK"],
        help="City display names from CITY_MAP keys."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    data_root = ROOT / "data"
    snapshots_root = data_root / "snapshots"
    snapshots_root.mkdir(parents=True, exist_ok=True)

    manifest = {
        "generatedAt": date.today().isoformat(),
        "index": {}
    }

    for city_display in args.cities:
        if city_display not in CITY_MAP:
            print(f"Skipping unsupported city: {city_display}")
            continue

        city_token = CITY_MAP[city_display]
        city_dir = snapshots_root / city_token
        city_dir.mkdir(parents=True, exist_ok=True)
        manifest["index"][city_token] = {}

        for i in range(args.days):
            current_date = date.today() + timedelta(days=i)
            date_str = current_date.isoformat()
            try:
                data = get_panchangam(current_date, city_token)
            except Exception as ex:
                print(f"Failed {city_token} {date_str}: {ex}")
                continue

            out_file = city_dir / f"{date_str}.json"
            out_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
            manifest["index"][city_token][date_str] = f"data/snapshots/{city_token}/{date_str}.json"
            print(f"Wrote {out_file}")

    manifest_file = data_root / "manifest.json"
    manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Updated {manifest_file}")


if __name__ == "__main__":
    main()
