"""
Phase 3 - Integrator
Connects user input to data pipeline and prepares filtered context for recommendation.
"""

import re
from dataclasses import dataclass
from typing import Any

import pandas as pd

from phase2.user_input import UserInput

CITY_COL = "listed_in(city)"
PRICE_COL = "approx_cost(for two people)"
NON_VEG_KEYWORDS = {"chicken", "mutton", "fish", "prawn", "egg", "meat", "lamb", "seafood"}


def _parse_cost(value: Any) -> int | None:
    """Parse cost string to int. Handles '600', '1,000', '300-400'. Returns None if unparseable."""
    if pd.isna(value):
        return None
    s = str(value).strip().replace(",", "").replace("₹", "")
    match = re.search(r"\d+", s)
    if match:
        return int(match.group())
    return None


def _has_non_veg_content(text: str) -> bool:
    """Check if text contains non-veg keywords."""
    if pd.isna(text) or not text:
        return False
    lower = str(text).lower()
    return any(kw in lower for kw in NON_VEG_KEYWORDS)


@dataclass
class IntegrationContext:
    """Filtered context ready for Phase 4 recommendation."""

    filtered_df: pd.DataFrame
    user_input: UserInput
    total_matches: int


class Integrator:
    """
    Integrates Phase 1 (data) and Phase 2 (user input).
    Filters restaurants by city, price, and diet; prepares context for Phase 4.
    """

    def filter_by_user_input(self, df: pd.DataFrame, user_input: UserInput) -> pd.DataFrame:
        """
        Filter dataframe by user preferences.

        Args:
            df: Restaurant dataframe from Phase 1.
            user_input: User preferences from Phase 2.

        Returns:
            Filtered DataFrame.
        """
        if df.empty:
            return df.copy()

        result = df.copy()

        # Filter by city (case-insensitive)
        if CITY_COL in result.columns:
            result = result[
                result[CITY_COL].fillna("").str.strip().str.lower()
                == user_input.city.strip().lower()
            ]

        # Filter by price (cost <= user price)
        if PRICE_COL in result.columns:
            result = result.copy()
            result["_parsed_cost"] = result[PRICE_COL].apply(_parse_cost)
            result = result[
                (result["_parsed_cost"].notna())
                & (result["_parsed_cost"] <= user_input.price)
            ].drop(columns=["_parsed_cost"], errors="ignore")

        # Filter by diet
        if user_input.diet == "veg":
            # Exclude rows with non-veg keywords in cuisines or dish_liked
            def is_veg(row: pd.Series) -> bool:
                cuisines = row.get("cuisines", "")
                dishes = row.get("dish_liked", "")
                return not (_has_non_veg_content(cuisines) or _has_non_veg_content(dishes))

            result = result[result.apply(is_veg, axis=1)]

        return result.reset_index(drop=True)

    def prepare_context(self, df: pd.DataFrame, user_input: UserInput) -> IntegrationContext:
        """
        Filter data and build context for Phase 4 recommendation.

        Args:
            df: Restaurant dataframe from Phase 1.
            user_input: User preferences from Phase 2.

        Returns:
            IntegrationContext with filtered DataFrame and metadata.
        """
        filtered = self.filter_by_user_input(df, user_input)
        return IntegrationContext(
            filtered_df=filtered,
            user_input=user_input,
            total_matches=len(filtered),
        )
