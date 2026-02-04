"""
Phase 2 - User Input Handler
Collects, validates, and normalizes user preferences: city, price, veg/non-veg.
"""

from dataclasses import dataclass
from typing import Optional


VALID_DIET_VALUES = {"veg", "non-veg", "nonveg", "vegetarian", "non-vegetarian"}
DIET_NORMALIZE = {
    "veg": "veg",
    "vegetarian": "veg",
    "non-veg": "non-veg",
    "nonveg": "non-veg",
    "non-vegetarian": "non-veg",
}


@dataclass
class UserInput:
    """Validated user preferences for restaurant recommendation."""

    city: str
    price: int  # Approx cost for two people (₹)
    diet: str  # "veg" or "non-veg"

    def __post_init__(self) -> None:
        if not self.city or not self.city.strip():
            raise ValueError("City cannot be empty")
        if self.price < 0:
            raise ValueError("Price must be non-negative")
        if self.diet not in ("veg", "non-veg"):
            raise ValueError(f"Diet must be 'veg' or 'non-veg', got: {self.diet}")


class UserInputHandler:
    """Validates and normalizes user input for city, price, and diet."""

    def __init__(self, allowed_cities: Optional[list[str]] = None):
        """
        Args:
            allowed_cities: Optional list of valid city names. If provided,
                           city input is validated against this list.
        """
        self.allowed_cities = (
            [c.strip().lower() for c in allowed_cities] if allowed_cities else None
        )

    def validate_city(self, city: str) -> str:
        """Validate and normalize city name."""
        if not city or not isinstance(city, str):
            raise ValueError("City must be a non-empty string")
        normalized = city.strip()
        if not normalized:
            raise ValueError("City cannot be blank")
        if self.allowed_cities and normalized.lower() not in self.allowed_cities:
            raise ValueError(
                f"City '{city}' not in allowed list: {self.allowed_cities}"
            )
        return normalized

    def validate_price(self, price: str | int) -> int:
        """Validate and normalize price (approx cost for two in ₹)."""
        if isinstance(price, int):
            value = price
        elif isinstance(price, str):
            cleaned = price.strip().replace(",", "").replace("₹", "")
            if not cleaned:
                raise ValueError("Price cannot be empty")
            try:
                value = int(cleaned)
            except ValueError:
                raise ValueError(f"Price must be a number, got: {price}")
        else:
            raise ValueError(f"Price must be str or int, got: {type(price)}")

        if value < 0:
            raise ValueError("Price must be non-negative")
        return value

    def validate_diet(self, diet: str) -> str:
        """Validate and normalize diet preference to 'veg' or 'non-veg'."""
        if not diet or not isinstance(diet, str):
            raise ValueError("Diet must be a non-empty string")
        normalized = diet.strip().lower()
        if not normalized:
            raise ValueError("Diet cannot be blank")
        if normalized not in VALID_DIET_VALUES:
            raise ValueError(
                f"Diet must be one of {list(VALID_DIET_VALUES)}, got: {diet}"
            )
        return DIET_NORMALIZE[normalized]

    def parse(
        self,
        city: str,
        price: str | int,
        diet: str,
    ) -> UserInput:
        """Parse and validate all inputs, returning UserInput."""
        return UserInput(
            city=self.validate_city(city),
            price=self.validate_price(price),
            diet=self.validate_diet(diet),
        )
