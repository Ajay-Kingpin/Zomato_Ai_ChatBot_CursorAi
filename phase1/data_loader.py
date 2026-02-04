"""
Phase 1 - Zomato Data Loader
Loads Zomato restaurant data from Hugging Face dataset or local CSV file.
"""

from pathlib import Path
from typing import Optional

import pandas as pd


# Expected columns from Zomato dataset schema
EXPECTED_COLUMNS = [
    "url",
    "address",
    "name",
    "online_order",
    "book_table",
    "rate",
    "votes",
    "phone",
    "location",
    "rest_type",
    "dish_liked",
    "cuisines",
    "approx_cost(for two people)",
    "reviews_list",
    "menu_item",
    "listed_in(type)",
    "listed_in(city)",
]


class ZomatoDataLoader:
    """
    Loads Zomato restaurant recommendation dataset from:
    - Hugging Face: ManikaSaini/zomato-restaurant-recommendation
    - Local CSV file
    """

    def __init__(self, data_path: Optional[Path] = None):
        """
        Args:
            data_path: Optional path to local CSV. If None, uses Hugging Face.
        """
        self.data_path = Path(data_path) if data_path else None
        self._df: Optional[pd.DataFrame] = None

    def load_from_huggingface(self) -> pd.DataFrame:
        """Load dataset from Hugging Face."""
        try:
            from datasets import load_dataset
        except ImportError:
            raise ImportError(
                "Install datasets: pip install datasets huggingface_hub"
            )

        dataset = load_dataset(
            "ManikaSaini/zomato-restaurant-recommendation",
            split="train",
            trust_remote_code=True,
        )
        self._df = dataset.to_pandas()
        return self._validate_schema(self._df)

    def load_from_csv(self, csv_path: Optional[Path] = None) -> pd.DataFrame:
        """
        Load dataset from local CSV file.

        Args:
            csv_path: Path to CSV. Uses self.data_path if not provided.
        """
        path = csv_path or self.data_path
        if not path:
            raise ValueError("No CSV path provided. Set data_path or pass csv_path.")

        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")

        self._df = pd.read_csv(path, low_memory=False)
        return self._validate_schema(self._df)

    def load(self, prefer_local: bool = True) -> pd.DataFrame:
        """
        Load data: tries local CSV first if prefer_local, else Hugging Face.

        Args:
            prefer_local: If True and data_path is set, load from CSV.
                         Otherwise load from Hugging Face.
        """
        if prefer_local and self.data_path and self.data_path.exists():
            return self.load_from_csv()
        return self.load_from_huggingface()

    def _validate_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate that required columns exist. Returns validated DataFrame."""
        missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
        if missing:
            raise ValueError(
                f"Schema validation failed. Missing columns: {missing}"
            )
        return df

    @property
    def data(self) -> pd.DataFrame:
        """Return loaded DataFrame. Loads if not yet loaded."""
        if self._df is None:
            raise RuntimeError(
                "Data not loaded. Call load(), load_from_csv(), or load_from_huggingface() first."
            )
        return self._df

    def get_row_count(self) -> int:
        """Return number of rows in loaded data."""
        return len(self.data)

    def get_unique_cities(self) -> list[str]:
        """Return list of unique cities (from listed_in(city))."""
        col = "listed_in(city)"
        if col not in self.data.columns:
            return []
        return sorted(self.data[col].dropna().unique().tolist())
