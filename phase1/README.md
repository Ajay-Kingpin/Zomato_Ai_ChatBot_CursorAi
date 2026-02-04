# Phase 1 – Zomato Data Ingestion

Load and validate Zomato restaurant dataset from Hugging Face or local CSV.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

### CLI

```bash
# Load from Hugging Face
python -m phase1.main --no-prefer-local

# Load from local CSV
python -m phase1.main --csv path/to/zomato.csv
```

### Python API

```python
from phase1 import ZomatoDataLoader

# From local CSV
loader = ZomatoDataLoader(data_path=Path("data/zomato.csv"))
df = loader.load_from_csv()

# From Hugging Face
loader = ZomatoDataLoader()
df = loader.load_from_huggingface()

print(loader.get_row_count())
print(loader.get_unique_cities())
```

## Run Tests

```bash
pytest phase1/tests/ -v
```
