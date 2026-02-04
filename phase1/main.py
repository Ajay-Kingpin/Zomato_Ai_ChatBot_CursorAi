"""
Phase 1 - CLI entry point for data loading.
Usage:
  python -m phase1.main                    # Load from Hugging Face
  python -m phase1.main --csv path/to.csv  # Load from local CSV
"""

import argparse
from pathlib import Path

from .data_loader import ZomatoDataLoader


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 1: Load Zomato data")
    parser.add_argument(
        "--csv",
        type=Path,
        default=None,
        help="Path to local zomato CSV file",
    )
    parser.add_argument(
        "--prefer-local",
        action="store_true",
        default=True,
        help="Prefer local CSV if path is set (default: True)",
    )
    parser.add_argument(
        "--no-prefer-local",
        action="store_false",
        dest="prefer_local",
        help="Always load from Hugging Face",
    )
    args = parser.parse_args()

    loader = ZomatoDataLoader(data_path=args.csv)
    df = loader.load(prefer_local=args.prefer_local)

    print(f"Loaded {loader.get_row_count():,} restaurants")
    cities = loader.get_unique_cities()
    print(f"Unique cities: {len(cities)}")
    if cities:
        print(f"Sample cities: {cities[:5]}")
    print("Phase 1 data load complete.")


if __name__ == "__main__":
    main()
