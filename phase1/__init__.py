"""
Phase 1: Zomato Data Ingestion
Load and validate Zomato restaurant dataset from Hugging Face or local CSV.
"""

from .data_loader import ZomatoDataLoader

__all__ = ["ZomatoDataLoader"]
