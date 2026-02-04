"""Phase 2 - Tests for UserInputHandler and UserInput."""

import pytest

from phase2.user_input import UserInput, UserInputHandler


class TestUserInputHandlerValidateCity:
    """Tests for validate_city()."""

    def test_valid_city_returns_stripped(self):
        handler = UserInputHandler()
        assert handler.validate_city("  Banashankari  ") == "Banashankari"

    def test_empty_city_raises(self):
        handler = UserInputHandler()
        with pytest.raises(ValueError, match="non-empty"):
            handler.validate_city("")
        with pytest.raises(ValueError, match="blank"):
            handler.validate_city("   ")

    def test_none_city_raises(self):
        handler = UserInputHandler()
        with pytest.raises(ValueError, match="non-empty"):
            handler.validate_city(None)

    def test_allowed_cities_valid_passes(self):
        handler = UserInputHandler(allowed_cities=["Banashankari", "Indiranagar"])
        assert handler.validate_city("Banashankari") == "Banashankari"
        assert handler.validate_city("indiranagar") == "indiranagar"

    def test_allowed_cities_invalid_raises(self):
        handler = UserInputHandler(allowed_cities=["Banashankari"])
        with pytest.raises(ValueError, match="not in allowed"):
            handler.validate_city("UnknownCity")


class TestUserInputHandlerValidatePrice:
    """Tests for validate_price()."""

    def test_valid_int_price(self):
        handler = UserInputHandler()
        assert handler.validate_price(600) == 600
        assert handler.validate_price(0) == 0

    def test_valid_string_price(self):
        handler = UserInputHandler()
        assert handler.validate_price("600") == 600
        assert handler.validate_price("  800  ") == 800
        assert handler.validate_price("1,000") == 1000
        assert handler.validate_price("₹500") == 500

    def test_invalid_price_raises(self):
        handler = UserInputHandler()
        with pytest.raises(ValueError, match="number"):
            handler.validate_price("abc")
        with pytest.raises(ValueError, match="empty"):
            handler.validate_price("  ")
        with pytest.raises(ValueError, match="non-negative"):
            handler.validate_price(-100)
        with pytest.raises(ValueError, match="str or int"):
            handler.validate_price(3.14)


class TestUserInputHandlerValidateDiet:
    """Tests for validate_diet()."""

    @pytest.mark.parametrize(
        "input_val,expected",
        [
            ("veg", "veg"),
            ("VEG", "veg"),
            ("vegetarian", "veg"),
            ("non-veg", "non-veg"),
            ("nonveg", "non-veg"),
            ("non-vegetarian", "non-veg"),
        ],
    )
    def test_valid_diet_normalizes(self, input_val: str, expected: str):
        handler = UserInputHandler()
        assert handler.validate_diet(input_val) == expected

    def test_invalid_diet_raises(self):
        handler = UserInputHandler()
        with pytest.raises(ValueError, match="Diet must be one of"):
            handler.validate_diet("vegan")
        with pytest.raises(ValueError, match="non-empty"):
            handler.validate_diet("")
        with pytest.raises(ValueError, match="blank"):
            handler.validate_diet("   ")


class TestUserInputHandlerParse:
    """Tests for parse()."""

    def test_parse_success(self):
        handler = UserInputHandler()
        result = handler.parse("Banashankari", "600", "veg")
        assert result.city == "Banashankari"
        assert result.price == 600
        assert result.diet == "veg"

    def test_parse_with_allowed_cities(self):
        handler = UserInputHandler(allowed_cities=["Banashankari"])
        result = handler.parse("Banashankari", 800, "non-veg")
        assert result.city == "Banashankari"
        assert result.price == 800
        assert result.diet == "non-veg"

    def test_parse_invalid_city_raises(self):
        handler = UserInputHandler()
        with pytest.raises(ValueError):
            handler.parse("", "600", "veg")

    def test_parse_invalid_price_raises(self):
        handler = UserInputHandler()
        with pytest.raises(ValueError):
            handler.parse("Banashankari", "invalid", "veg")

    def test_parse_invalid_diet_raises(self):
        handler = UserInputHandler()
        with pytest.raises(ValueError):
            handler.parse("Banashankari", "600", "vegan")


class TestUserInputDataclass:
    """Tests for UserInput dataclass validation."""

    def test_valid_user_input(self):
        ui = UserInput(city="Koramangala", price=500, diet="veg")
        assert ui.city == "Koramangala"
        assert ui.price == 500
        assert ui.diet == "veg"

    def test_empty_city_raises(self):
        with pytest.raises(ValueError, match="City cannot be empty"):
            UserInput(city="", price=500, diet="veg")

    def test_negative_price_raises(self):
        with pytest.raises(ValueError, match="Price must be non-negative"):
            UserInput(city="Koramangala", price=-1, diet="veg")

    def test_invalid_diet_raises(self):
        with pytest.raises(ValueError, match="Diet must be"):
            UserInput(city="Koramangala", price=500, diet="vegan")
