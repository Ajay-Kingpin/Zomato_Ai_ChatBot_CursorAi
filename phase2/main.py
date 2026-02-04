"""
Phase 2 - CLI entry point for user input.
Usage:
  python -m phase2.main
  python -m phase2.main --city Banashankari --price 600 --diet veg
"""

import argparse
from pathlib import Path

from .user_input import UserInputHandler


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Phase 2: Collect user preferences (city, price, veg/non-veg)"
    )
    parser.add_argument("--city", required=True, help="City/area name")
    parser.add_argument(
        "--price",
        required=True,
        help="Approx cost for two people (₹)",
    )
    parser.add_argument(
        "--diet",
        required=True,
        choices=["veg", "non-veg", "vegetarian", "nonveg", "non-vegetarian"],
        help="Diet preference: veg or non-veg",
    )
    args = parser.parse_args()

    handler = UserInputHandler()
    user_input = handler.parse(args.city, args.price, args.diet)

    print("User preferences collected:")
    print(f"  City: {user_input.city}")
    print(f"  Price (approx for two): ₹{user_input.price}")
    print(f"  Diet: {user_input.diet}")
    print("Phase 2 complete.")


if __name__ == "__main__":
    main()
