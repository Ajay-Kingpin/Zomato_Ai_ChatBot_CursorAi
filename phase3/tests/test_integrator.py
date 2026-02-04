"""Phase 3 - Tests for Integrator."""

from pathlib import Path

import pandas as pd
import pytest

from phase2.user_input import UserInput
from phase3.integrator import (
    IntegrationContext,
    Integrator,
    _has_non_veg_content,
    _parse_cost,
)


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Sample restaurant dataframe."""
    return pd.DataFrame(
        {
            "name": ["Restaurant A", "Restaurant B", "Restaurant C", "Restaurant D"],
            "listed_in(city)": ["Banashankari", "Indiranagar", "Banashankari", "Koramangala"],
            "approx_cost(for two people)": ["600", "800", "400", "1000"],
            "cuisines": ["North Indian", "North Indian, Chinese", "South Indian", "Chinese"],
            "dish_liked": ["Pasta", "Biryani, Chicken", "Dosa", "Fish Fry"],
        }
    )


class TestParseCost:
    """Tests for _parse_cost helper."""

    def test_simple_int(self):
        assert _parse_cost("600") == 600
        assert _parse_cost("400") == 400

    def test_with_comma(self):
        assert _parse_cost("1,000") == 1000

    def test_with_rupee(self):
        assert _parse_cost("₹500") == 500

    def test_range_takes_first(self):
        assert _parse_cost("300-400") == 300

    def test_nan_returns_none(self):
        assert _parse_cost(float("nan")) is None
        assert _parse_cost(pd.NA) is None

    def test_invalid_returns_none(self):
        assert _parse_cost("N/A") is None
        assert _parse_cost("") is None


class TestHasNonVegContent:
    """Tests for _has_non_veg_content helper."""

    def test_contains_chicken(self):
        assert _has_non_veg_content("Biryani, Chicken") is True

    def test_contains_fish(self):
        assert _has_non_veg_content("Fish Fry") is True

    def test_veg_only(self):
        assert _has_non_veg_content("Dosa, Idli") is False

    def test_empty_or_nan(self):
        assert _has_non_veg_content("") is False
        assert _has_non_veg_content(pd.NA) is False


class TestIntegratorFilterByUserInput:
    """Tests for filter_by_user_input."""

    def test_filter_by_city(self, sample_df):
        integrator = Integrator()
        user_input = UserInput(city="Banashankari", price=1000, diet="non-veg")
        result = integrator.filter_by_user_input(sample_df, user_input)
        assert len(result) == 2
        assert list(result["name"]) == ["Restaurant A", "Restaurant C"]

    def test_filter_by_price(self, sample_df):
        integrator = Integrator()
        user_input = UserInput(city="Banashankari", price=500, diet="non-veg")
        result = integrator.filter_by_user_input(sample_df, user_input)
        assert len(result) == 1
        assert result.iloc[0]["name"] == "Restaurant C"

    def test_filter_by_city_and_price(self, sample_df):
        integrator = Integrator()
        user_input = UserInput(city="Banashankari", price=600, diet="non-veg")
        result = integrator.filter_by_user_input(sample_df, user_input)
        assert len(result) == 2
        names = set(result["name"])
        assert names == {"Restaurant A", "Restaurant C"}

    def test_filter_veg_excludes_non_veg(self, sample_df):
        integrator = Integrator()
        user_input = UserInput(city="Indiranagar", price=1000, diet="veg")
        result = integrator.filter_by_user_input(sample_df, user_input)
        # Restaurant B has Chicken/Biryani - should be excluded for veg
        assert len(result) == 0

    def test_filter_veg_includes_veg_only(self, sample_df):
        integrator = Integrator()
        user_input = UserInput(city="Banashankari", price=1000, diet="veg")
        result = integrator.filter_by_user_input(sample_df, user_input)
        # A (Pasta) and C (Dosa) are veg
        assert len(result) == 2
        assert set(result["name"]) == {"Restaurant A", "Restaurant C"}

    def test_filter_non_veg_includes_all_matching_city_price(self, sample_df):
        integrator = Integrator()
        user_input = UserInput(city="Indiranagar", price=1000, diet="non-veg")
        result = integrator.filter_by_user_input(sample_df, user_input)
        assert len(result) == 1
        assert result.iloc[0]["name"] == "Restaurant B"

    def test_empty_df_returns_empty(self):
        integrator = Integrator()
        user_input = UserInput(city="X", price=500, diet="veg")
        result = integrator.filter_by_user_input(pd.DataFrame(), user_input)
        assert len(result) == 0

    def test_no_matches_returns_empty(self, sample_df):
        integrator = Integrator()
        user_input = UserInput(city="UnknownCity", price=500, diet="veg")
        result = integrator.filter_by_user_input(sample_df, user_input)
        assert len(result) == 0


class TestIntegratorPrepareContext:
    """Tests for prepare_context."""

    def test_prepare_context_returns_integration_context(self, sample_df):
        integrator = Integrator()
        user_input = UserInput(city="Banashankari", price=600, diet="veg")
        context = integrator.prepare_context(sample_df, user_input)
        assert isinstance(context, IntegrationContext)
        assert context.user_input == user_input
        assert context.total_matches == len(context.filtered_df)

    def test_prepare_context_filtered_correctly(self, sample_df):
        integrator = Integrator()
        user_input = UserInput(city="Koramangala", price=1500, diet="non-veg")
        context = integrator.prepare_context(sample_df, user_input)
        assert context.total_matches == 1
        assert context.filtered_df.iloc[0]["name"] == "Restaurant D"
