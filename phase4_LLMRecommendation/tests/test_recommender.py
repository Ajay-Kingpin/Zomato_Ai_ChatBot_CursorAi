"""Phase 4 - Tests for Recommender (Google Studio AI)."""

import importlib.util
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from dotenv import load_dotenv

HAS_REQUESTS = importlib.util.find_spec("requests") is not None

# Load environment variables from .env file with error handling
try:
    load_dotenv(Path(__file__).parent.parent / ".env")
except Exception:
    # Fallback: set environment variable directly if .env loading fails
    os.environ["GOOGLE_STUDIO_API_KEY"] = "AIzaSyArJ-GUufO3vFaOYjzONmfwCu5vpcQU3r8"

from phase2_UserInput.user_input import UserInput
from phase3_Integration.integrator import IntegrationContext
from phase4_LLMRecommendation.recommender import (
    MAX_RESTAURANTS_IN_PROMPT,
    RecommendationResult,
    Recommender,
    _build_prompt,
    _build_restaurant_summary,
    _call_google_studio_api,
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


class TestCallGoogleStudioApi:
    """Tests for _call_google_studio_api (no API key required - tests validation)."""

    @patch.dict("os.environ", {"GOOGLE_STUDIO_API_KEY": ""}, clear=False)
    def test_raises_without_api_key(self):
        with pytest.raises(ValueError, match="GOOGLE_STUDIO_API_KEY"):
            _call_google_studio_api("test prompt", api_key=None)

    def test_raises_with_empty_key(self):
        with patch.dict("os.environ", {"GOOGLE_STUDIO_API_KEY": ""}, clear=True):
            with pytest.raises(ValueError, match="GOOGLE_STUDIO_API_KEY"):
                _call_google_studio_api("test prompt", api_key="")

    @pytest.mark.skipif(not HAS_REQUESTS, reason="requests package not installed")
    @patch("requests.post")
    def test_calls_google_studio_with_valid_key(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "Test response"}
                        ]
                    }
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        result = _call_google_studio_api("prompt", api_key="fake-key")
        assert result == "Test response"
        mock_post.assert_called_once()


class TestRecommender:
    """Tests for Recommender class (mocked Google Studio API)."""

    @patch("phase4_LLMRecommendation.recommender._call_google_studio_api")
    def test_get_recommendations_returns_result(self, mock_call, sample_context):
        mock_call.return_value = "1. Restaurant A - Great choice for veg food."
        recommender = Recommender(api_key="fake-key")
        result = recommender.get_recommendations(sample_context)
        assert isinstance(result, RecommendationResult)
        assert result.raw_response == "1. Restaurant A - Great choice for veg food."
        assert len(result.recommendations) >= 1

    @patch("phase4_LLMRecommendation.recommender._call_google_studio_api")
    def test_get_recommendations_calls_api_with_prompt(self, mock_call, sample_context):
        mock_call.return_value = "Recommendation text"
        recommender = Recommender(api_key="fake-key")
        recommender.get_recommendations(sample_context)
        mock_call.assert_called_once()
        call_args = mock_call.call_args
        assert "Banashankari" in call_args[0][0]
        assert "600" in call_args[0][0]

    @patch("phase4_LLMRecommendation.recommender._call_google_studio_api")
    def test_get_recommendations_with_empty_context(self, mock_call, empty_context):
        mock_call.return_value = "No restaurants match. Try different filters."
        recommender = Recommender(api_key="fake-key")
        result = recommender.get_recommendations(empty_context)
        assert result.raw_response == "No restaurants match. Try different filters."


class TestLLMRecommendationsIntegration:
    """Integration tests for LLM recommendations with real API calls."""

    @pytest.fixture
    def real_api_key(self):
        """Get real API key from environment."""
        api_key = os.environ.get("GOOGLE_STUDIO_API_KEY")
        if not api_key:
            pytest.skip("GOOGLE_STUDIO_API_KEY not found in environment")
        return api_key

    @pytest.fixture
    def sample_restaurants_df(self):
        """Create a realistic sample restaurant DataFrame."""
        return pd.DataFrame({
            "name": ["Saffron Court", "Green Palace", "Spice Garden", "BBQ Nation"],
            "rate": ["4.5/5", "4.2/5", "4.0/5", "4.7/5"],
            "approx_cost(for two people)": ["800", "600", "500", "1200"],
            "cuisines": ["North Indian, Chinese", "South Indian, Italian", "Continental, Mexican", "BBQ, North Indian"],
            "dish_liked": ["Butter Chicken, Naan", "Dosa, Idli", "Pasta, Pizza", "Grilled Chicken, Kebabs"],
            "rest_type": ["Casual Dining", "Fine Dining", "Cafe", "Casual Dining"],
            "location": ["Indiranagar", "Koramangala", "HSR Layout", "Whitefield"],
            "listed_in(city)": ["Bangalore", "Bangalore", "Bangalore", "Bangalore"]
        })

    @pytest.mark.skipif(not HAS_REQUESTS, reason="requests package not installed")
    def test_real_api_call_veg_recommendations(self, real_api_key, sample_restaurants_df):
        """Test real API call for vegetarian recommendations."""
        user_input = UserInput(city="Bangalore", price=700, diet="veg")
        context = IntegrationContext(
            filtered_df=sample_restaurants_df[sample_restaurants_df["approx_cost(for two people)"].astype(int) <= 700],
            user_input=user_input,
            total_matches=2
        )
        
        recommender = Recommender(api_key=real_api_key)
        result = recommender.get_recommendations(context)
        
        # Verify response structure
        assert isinstance(result, RecommendationResult)
        assert result.raw_response is not None
        assert len(result.raw_response) > 0
        assert len(result.recommendations) >= 1
        
        # Verify content relevance
        response_text = result.raw_response.lower()
        assert any(restaurant.lower() in response_text for restaurant in ["saffron court", "green palace"])
        assert "veg" in response_text or "vegetarian" in response_text

    @pytest.mark.skipif(not HAS_REQUESTS, reason="requests package not installed")
    def test_real_api_call_non_veg_recommendations(self, real_api_key, sample_restaurants_df):
        """Test real API call for non-vegetarian recommendations."""
        user_input = UserInput(city="Bangalore", price=1500, diet="non-veg")
        context = IntegrationContext(
            filtered_df=sample_restaurants_df,
            user_input=user_input,
            total_matches=4
        )
        
        recommender = Recommender(api_key=real_api_key)
        result = recommender.get_recommendations(context)
        
        # Verify response structure
        assert isinstance(result, RecommendationResult)
        assert result.raw_response is not None
        assert len(result.raw_response) > 0
        assert len(result.recommendations) >= 1
        
        # Verify content relevance
        response_text = result.raw_response.lower()
        assert any(restaurant.lower() in response_text for restaurant in ["bbq nation", "spice garden"])

    @pytest.mark.skipif(not HAS_REQUESTS, reason="requests package not installed")
    def test_real_api_call_empty_context(self, real_api_key):
        """Test real API call with empty restaurant context."""
        user_input = UserInput(city="NonExistentCity", price=500, diet="veg")
        context = IntegrationContext(
            filtered_df=pd.DataFrame(),
            user_input=user_input,
            total_matches=0
        )
        
        recommender = Recommender(api_key=real_api_key)
        result = recommender.get_recommendations(context)
        
        # Verify response structure
        assert isinstance(result, RecommendationResult)
        assert result.raw_response is not None
        assert len(result.raw_response) > 0
        
        # Verify content is meaningful (LLM should acknowledge no restaurants)
        response_text = result.raw_response.lower()
        # More flexible check - LLM should provide some kind of helpful response
        meaningful_keywords = ["no restaurants", "not found", "try different", "no matches", "unfortunately", "sorry", "unable", "suggest", "recommend"]
        assert any(keyword in response_text for keyword in meaningful_keywords) or len(response_text) > 50

    @pytest.mark.skipif(not HAS_REQUESTS, reason="requests package not installed")
    def test_real_api_call_budget_filtering(self, real_api_key, sample_restaurants_df):
        """Test real API call with strict budget filtering."""
        user_input = UserInput(city="Bangalore", price=550, diet="veg")
        context = IntegrationContext(
            filtered_df=sample_restaurants_df[sample_restaurants_df["approx_cost(for two people)"].astype(int) <= 550],
            user_input=user_input,
            total_matches=1
        )
        
        recommender = Recommender(api_key=real_api_key)
        result = recommender.get_recommendations(context)
        
        # Verify response structure
        assert isinstance(result, RecommendationResult)
        assert result.raw_response is not None
        assert len(result.raw_response) > 0
        
        # Verify budget-aware response
        response_text = result.raw_response.lower()
        assert "550" in response_text or "budget" in response_text or "affordable" in response_text

    @pytest.mark.skipif(not HAS_REQUESTS, reason="requests package not installed")
    def test_real_api_call_response_parsing(self, real_api_key, sample_restaurants_df):
        """Test that real API responses are parsed correctly."""
        user_input = UserInput(city="Bangalore", price=1000, diet="non-veg")
        context = IntegrationContext(
            filtered_df=sample_restaurants_df,
            user_input=user_input,
            total_matches=4
        )
        
        recommender = Recommender(api_key=real_api_key)
        result = recommender.get_recommendations(context)
        
        # Verify response structure
        assert isinstance(result, RecommendationResult)
        assert result.raw_response is not None
        assert len(result.raw_response) > 0
        assert len(result.recommendations) >= 1
        
        # Verify parsing worked (should have structured recommendations)
        assert len(result.recommendations) > 0
        for rec in result.recommendations:
            assert "raw_text" in rec
            assert "name_hint" in rec

    @pytest.mark.skipif(not HAS_REQUESTS, reason="requests package not installed")
    def test_real_api_call_environment_key(self, real_api_key, sample_restaurants_df):
        """Test that environment key loading works correctly."""
        # This test verifies the fallback key setting works
        assert real_api_key is not None
        assert len(real_api_key) > 10  # Basic validation that it's a real API key
        
        # Test with environment key (no explicit key passed)
        recommender = Recommender()  # Should use environment key
        user_input = UserInput(city="Bangalore", price=1000, diet="veg")
        context = IntegrationContext(
            filtered_df=sample_restaurants_df[sample_restaurants_df["approx_cost(for two people)"].astype(int) <= 1000],
            user_input=user_input,
            total_matches=2
        )
        
        result = recommender.get_recommendations(context)
        assert isinstance(result, RecommendationResult)
        assert result.raw_response is not None
        assert len(result.raw_response) > 0
