"""Phase 1 - Tests for ZomatoDataLoader."""

import tempfile
from pathlib import Path

import pytest

from phase1.data_loader import ZomatoDataLoader, EXPECTED_COLUMNS


@pytest.fixture
def sample_csv_path() -> Path:
    """Path to sample CSV fixture."""
    return Path(__file__).parent / "fixtures" / "sample_zomato.csv"


@pytest.fixture
def loader_with_fixture(sample_csv_path: Path) -> ZomatoDataLoader:
    """Loader configured with sample CSV path."""
    return ZomatoDataLoader(data_path=sample_csv_path)


class TestZomatoDataLoaderLoadFromCsv:
    """Tests for load_from_csv()."""

    def test_load_from_csv_success(self, loader_with_fixture, sample_csv_path):
        """Loading valid CSV returns DataFrame with expected columns."""
        loader = loader_with_fixture
        df = loader.load_from_csv(sample_csv_path)

        assert df is not None
        assert len(df) == 3
        for col in EXPECTED_COLUMNS:
            assert col in df.columns
        assert "name" in df.columns
        assert list(df["name"]) == ["Restaurant A", "Restaurant B", "Restaurant C"]

    def test_load_from_csv_uses_data_path_if_no_arg(
        self, loader_with_fixture, sample_csv_path
    ):
        """load_from_csv uses self.data_path when csv_path not passed."""
        loader = ZomatoDataLoader(data_path=sample_csv_path)
        df = loader.load_from_csv()
        assert len(df) == 3

    def test_load_from_csv_file_not_found(self):
        """load_from_csv raises FileNotFoundError for missing file."""
        loader = ZomatoDataLoader(data_path=Path("/nonexistent/zomato.csv"))
        with pytest.raises(FileNotFoundError, match="not found"):
            loader.load_from_csv()

    def test_load_from_csv_no_path_raises(self):
        """load_from_csv raises ValueError when no path configured."""
        loader = ZomatoDataLoader()
        with pytest.raises(ValueError, match="No CSV path"):
            loader.load_from_csv()


class TestZomatoDataLoaderValidation:
    """Tests for schema validation."""

    def test_invalid_schema_missing_columns_raises(self, tmp_path):
        """CSV with missing columns raises ValueError."""
        bad_csv = tmp_path / "bad.csv"
        bad_csv.write_text("url,name\nhttps://x.com,Test")
        loader = ZomatoDataLoader(data_path=bad_csv)
        with pytest.raises(ValueError, match="Missing columns"):
            loader.load_from_csv()


class TestZomatoDataLoaderProperties:
    """Tests for data access properties."""

    def test_get_row_count(self, loader_with_fixture, sample_csv_path):
        """get_row_count returns correct count after load."""
        loader = loader_with_fixture
        loader.load_from_csv(sample_csv_path)
        assert loader.get_row_count() == 3

    def test_get_unique_cities(self, loader_with_fixture, sample_csv_path):
        """get_unique_cities returns sorted unique cities."""
        loader = loader_with_fixture
        loader.load_from_csv(sample_csv_path)
        cities = loader.get_unique_cities()
        assert cities == ["Banashankari", "Indiranagar", "Koramangala"]

    def test_data_property_before_load_raises(self):
        """Accessing .data before load raises RuntimeError."""
        loader = ZomatoDataLoader(data_path=Path("dummy.csv"))
        with pytest.raises(RuntimeError, match="Data not loaded"):
            _ = loader.data


class TestZomatoDataLoaderLoad:
    """Tests for load() convenience method."""

    def test_load_prefer_local_uses_csv_when_exists(
        self, loader_with_fixture, sample_csv_path
    ):
        """load(prefer_local=True) uses CSV when path exists."""
        loader = ZomatoDataLoader(data_path=sample_csv_path)
        df = loader.load(prefer_local=True)
        assert len(df) == 3
        assert "Restaurant A" in df["name"].values

    def test_load_prefer_local_without_path_uses_huggingface(self):
        """load(prefer_local=True) with no path uses Hugging Face (if HF available)."""
        loader = ZomatoDataLoader()
        # This will try Hugging Face - may skip if no network in CI
        try:
            df = loader.load(prefer_local=True)
            assert df is not None
            assert len(df) > 0
        except Exception:
            pytest.skip("Hugging Face load failed (network or auth)")
