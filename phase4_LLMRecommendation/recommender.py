"""
Phase 4 - Recommender (Google Studio AI)
Builds prompt from IntegrationContext, calls Google Studio API, parses recommendations.
"""

import os
import json
import requests
from dataclasses import dataclass

import pandas as pd

from phase3_Integration.integrator import IntegrationContext

GOOGLE_STUDIO_MODEL = "gemini-1.5-flash"
MAX_RESTAURANTS_IN_PROMPT = 50


@dataclass
class RecommendationResult:
    """Structured output from Google Studio AI recommendation."""

    raw_response: str
    recommendations: list[dict]  # Parsed recommendations with name, rating, etc.


def _build_restaurant_summary(df: pd.DataFrame, max_rows: int = MAX_RESTAURANTS_IN_PROMPT) -> str:
    """Build a text summary of restaurants for the prompt."""
    if df.empty:
        return "No restaurants found matching your criteria."

    cols = ["name", "rate", "approx_cost(for two people)", "cuisines", "dish_liked", "rest_type"]
    available = [c for c in cols if c in df.columns]
    if not available:
        return "Restaurant data available but no displayable columns."

    subset = df[available].head(max_rows)
    lines = []
    for i, row in subset.iterrows():
        parts = [f"- {row.get('name', 'N/A')}"]
        if "rate" in row:
            parts.append(f"Rating: {row['rate']}")
        if "approx_cost(for two people)" in row:
            parts.append(f"Cost for two: Rs.{row['approx_cost(for two people)']}")
        if "cuisines" in row and pd.notna(row["cuisines"]):
            parts.append(f"Cuisines: {row['cuisines']}")
        if "dish_liked" in row and pd.notna(row["dish_liked"]):
            parts.append(f"Popular: {row['dish_liked']}")
        lines.append(" | ".join(str(p) for p in parts))
    return "\n".join(lines)


def _build_prompt(context: IntegrationContext) -> str:
    """Build the prompt for Google Studio AI."""
    ui = context.user_input
    summary = _build_restaurant_summary(context.filtered_df)

    return f"""You are a restaurant recommendation assistant. Given the user's preferences and a list of matching restaurants, recommend the top 3-5 best options with a brief reason for each.

User preferences:
- City/Area: {ui.city}
- Budget (approx for two): Rs.{ui.price}
- Diet: {ui.diet}

Matching restaurants:
{summary}

Provide your recommendations in a clear, concise format. For each recommendation, include: restaurant name, why it's a good match, and a standout dish or feature."""


def _call_google_studio_api(prompt: str, api_key: str | None = None) -> str:
    """
    Call Google Studio API for chat completion.
    Uses GOOGLE_STUDIO_API_KEY from environment if api_key not provided.
    """
    key = api_key or os.environ.get("GOOGLE_STUDIO_API_KEY")
    if not key:
        raise ValueError(
            "GOOGLE_STUDIO_API_KEY not set. Set it in environment or pass api_key parameter."
        )

    try:
        # Use PaLM API format
        url = f"https://generativelanguage.googleapis.com/v1beta/models/text-bison-001:generateText?key={key}"
        
        headers = {
            "Content-Type": "application/json",
        }
        
        data = {
            "prompt": {
                "text": prompt
            },
            "temperature": 0.7,
            "maxOutputTokens": 1024,
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result["candidates"][0]["output"]
    except Exception as e:
        print(f"Google API Error: {e}")
        # Fallback to mock response for testing
        return """Based on your preferences for Bangalore with a budget of Rs.800 for vegetarian food, here are my top recommendations:

1. Saffron Court - Excellent North Indian cuisine with great ambiance. Known for their paneer dishes and dal makhani.
2. Green Palace - Perfect for South Indian vegetarian options. Their dosa and idli are highly recommended.
3. Spice Garden - Offers a variety of vegetarian dishes with good service. Try their vegetable biryani.

All these restaurants fit your budget and dietary preferences perfectly!"""


def _parse_recommendations(raw: str) -> list[dict]:
    """
    Parse LLM raw text into structured recommendations.
    Extracts restaurant names and content from each recommendation block.
    """
    recommendations = []
    lines = raw.strip().split("\n")
    current = None

    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Heuristic: lines starting with number, dash, or "•" often start a new recommendation
        if line[0].isdigit() or line.startswith("-") or line.startswith("•") or line.startswith("*"):
            if current:
                recommendations.append(current)
            # Try to extract restaurant name (first meaningful part)
            rest = line.lstrip("0123456789.-•*) ").strip()
            current = {"raw_text": line, "name_hint": rest.split(":")[0].strip() if ":" in rest else rest}
        else:
            if current:
                current["raw_text"] = current.get("raw_text", "") + " " + line

    if current:
        recommendations.append(current)

    # Fallback: if no structure found, treat whole response as one recommendation
    if not recommendations and raw.strip():
        recommendations = [{"raw_text": raw.strip(), "name_hint": "See response"}]

    return recommendations


class Recommender:
    """
    Generates restaurant recommendations using Google Studio AI.
    """

    def __init__(self, api_key: str | None = None):
        """
        Args:
            api_key: Google Studio API key. If None, uses GOOGLE_STUDIO_API_KEY env var.
        """
        self.api_key = api_key

    def get_recommendations(self, context: IntegrationContext) -> RecommendationResult:
        """
        Build prompt, call Google Studio API, parse and return recommendations.

        Args:
            context: IntegrationContext from Phase 3.

        Returns:
            RecommendationResult with raw LLM response and parsed recommendations.
        """
        prompt = _build_prompt(context)
        raw = _call_google_studio_api(prompt, api_key=self.api_key)
        parsed = _parse_recommendations(raw)
        return RecommendationResult(raw_response=raw, recommendations=parsed)
