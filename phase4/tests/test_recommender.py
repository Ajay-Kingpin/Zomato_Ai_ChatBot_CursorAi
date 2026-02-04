"""Phase 4 - Tests for Recommender (Groq LLM)."""

import importlib.util
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

HAS_GROQ = importlib.util.find_spec("groq") is not None

from phase2.user_input import UserInput
from phase3.integrator import IntegrationContext
from phase4.recommender import (
    MAX_RESTAURANTS_IN_PROMPT,
    RecommendationResult,
    Recommender,
    _build_prompt,
    _build_restaurant_summary,
    _call_groq_api,
    _parse_recommendations,
)


@pytest.fixture
def sample_context() -> IntegrationContext:
    """Sample IntegrationContext for tests."""
    df = pd.DataFrame(
        {
            "name": ["Restaurant A", "Restaurant B"],
            "rate": ["4.5/5", "4.2/5"],
            "approx_cost(for two people)": ["600", "500"],
            "cuisines": ["North Indian", "South Indian"],
            "dish_liked": ["Pasta", "Dosa"],
            "rest_type": ["Casual Dining", "Cafe"],
        }
    )
    user_input = UserInput(city="Banashankari", price=600, diet="veg")
    return IntegrationContext(filtered_df=df, user_input=user_input, total_matches=2)


@pytest.fixture
def empty_context() -> IntegrationContext:
    """Empty IntegrationContext."""
    user_input = UserInput(city="X", price=500, diet="veg")
    return IntegrationContext(filtered_df=pd.DataFrame(), user_input=user_input, total_matches=0)


class TestBuildRestaurantSummary:
    """Tests for _build_restaurant_summary."""

    def test_builds_summary_from_df(self, sample_context):
        summary = _build_restaurant_summary(sample_context.filtered_df)
        assert "Restaurant A" in summary
        assert "Restaurant B" in summary
        assert "4.5/5" in summary or "Rating" in summary
        assert "600" in summary or "₹" in summary

    def test_empty_df_returns_message(self, empty_context):
        summary = _build_restaurant_summary(empty_context.filtered_df)
        assert "No restaurants found" in summary

    def test_respects_max_rows(self):
        df = pd.DataFrame({"name": [f"R{i}" for i in range(100)]})
        summary = _build_restaurant_summary(df, max_rows=5)
        assert "R0" in summary
        assert "R4" in summary
        assert "R99" not in summary


class TestBuildPrompt:
    """Tests for _build_prompt."""

    def test_prompt_contains_user_preferences(self, sample_context):
        prompt = _build_prompt(sample_context)
        assert "Banashankari" in prompt
        assert "600" in prompt
        assert "veg" in prompt

    def test_prompt_contains_restaurant_data(self, sample_context):
        prompt = _build_prompt(sample_context)
        assert "Restaurant A" in prompt
        assert "Restaurant B" in prompt

    def test_prompt_with_empty_context(self, empty_context):
        prompt = _build_prompt(empty_context)
        assert "No restaurants found" in prompt or "No restaurants" in prompt
        assert "X" in prompt


class TestParseRecommendations:
    """Tests for _parse_recommendations."""

    def test_parses_numbered_list(self):
        raw = """1. Restaurant A - Great food and ambience
2. Restaurant B - Best biryani in town"""
        result = _parse_recommendations(raw)
        assert len(result) >= 1
        assert any("Restaurant" in str(r) for r in result)

    def test_parses_bullet_list(self):
        raw = """- Restaurant A: Amazing pasta
- Restaurant B: Great dosa"""
        result = _parse_recommendations(raw)
        assert len(result) >= 1

    def test_fallback_single_block(self):
        raw = "Try Restaurant X, they have the best North Indian food."
        result = _parse_recommendations(raw)
        assert len(result) == 1
        assert "Restaurant" in result[0].get("raw_text", "")

    def test_empty_string_returns_empty(self):
        result = _parse_recommendations("")
        assert result == []


class TestCallGroqApi:
    """Tests for _call_groq_api (no API key required - tests validation)."""

    @patch.dict("os.environ", {"GROQ_API_KEY": ""}, clear=False)
    def test_raises_without_api_key(self):
        with pytest.raises(ValueError, match="GROQ_API_KEY"):
            _call_groq_api("test prompt", api_key=None)

    def test_raises_with_empty_key(self):
        with pytest.raises(ValueError, match="GROQ_API_KEY"):
            _call_groq_api("test prompt", api_key="")

    @pytest.mark.skipif(not HAS_GROQ, reason="groq package not installed")
    @patch("groq.Groq")
    def test_calls_groq_with_valid_key(self, mock_groq_class):
        mock_client = mock_groq_class.return_value
        mock_msg = MagicMock()
        mock_msg.content = "Test response"
        mock_choice = MagicMock()
        mock_choice.message = mock_msg
        mock_client.chat.completions.create.return_value.choices = [mock_choice]
        result = _call_groq_api("prompt", api_key="fake-key")
        assert result == "Test response"
        mock_client.chat.completions.create.assert_called_once()


class TestRecommender:
    """Tests for Recommender class (mocked Groq API)."""

    @patch("phase4.recommender._call_groq_api")
    def test_get_recommendations_returns_result(self, mock_call, sample_context):
        mock_call.return_value = "1. Restaurant A - Great choice for veg food."
        recommender = Recommender(api_key="fake-key")
        result = recommender.get_recommendations(sample_context)
        assert isinstance(result, RecommendationResult)
        assert result.raw_response == "1. Restaurant A - Great choice for veg food."
        assert len(result.recommendations) >= 1

    @patch("phase4.recommender._call_groq_api")
    def test_get_recommendations_calls_api_with_prompt(self, mock_call, sample_context):
        mock_call.return_value = "Recommendation text"
        recommender = Recommender(api_key="fake-key")
        recommender.get_recommendations(sample_context)
        mock_call.assert_called_once()
        call_args = mock_call.call_args
        assert "Banashankari" in call_args[0][0]
        assert "600" in call_args[0][0]

    @patch("phase4.recommender._call_groq_api")
    def test_get_recommendations_with_empty_context(self, mock_call, empty_context):
        mock_call.return_value = "No restaurants match. Try different filters."
        recommender = Recommender(api_key="fake-key")
        result = recommender.get_recommendations(empty_context)
        assert result.raw_response == "No restaurants match. Try different filters."
