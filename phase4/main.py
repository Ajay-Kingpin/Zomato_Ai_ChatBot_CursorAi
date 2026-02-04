"""
Phase 4 - CLI entry point for recommendations.
Usage:
  set GROQ_API_KEY=your_key
  python -m phase4.main --csv path/to/zomato.csv --city Banashankari --price 600 --diet veg
"""

import argparse
from pathlib import Path

from phase1.data_loader import ZomatoDataLoader
from phase2.user_input import UserInputHandler
from phase3.integrator import Integrator
from phase4.recommender import Recommender


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Phase 4: Get restaurant recommendations via Groq LLM"
    )
    parser.add_argument("--csv", type=Path, required=True, help="Path to zomato CSV")
    parser.add_argument("--city", required=True, help="City/area name")
    parser.add_argument("--price", required=True, help="Approx cost for two (₹)")
    parser.add_argument(
        "--diet",
        required=True,
        choices=["veg", "non-veg", "vegetarian", "nonveg", "non-vegetarian"],
        help="Diet preference",
    )
    args = parser.parse_args()

    loader = ZomatoDataLoader(data_path=args.csv)
    loader.load_from_csv()

    handler = UserInputHandler()
    user_input = handler.parse(args.city, args.price, args.diet)

    integrator = Integrator()
    context = integrator.prepare_context(loader.data, user_input)

    recommender = Recommender()
    result = recommender.get_recommendations(context)

    print("\n--- Recommendations ---\n")
    print(result.raw_response)
    print(f"\n(Parsed {len(result.recommendations)} recommendation(s))")


if __name__ == "__main__":
    main()
