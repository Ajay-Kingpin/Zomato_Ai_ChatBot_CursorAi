# Phase 2 – User Input

Collect and validate user preferences: city, price, veg/non-veg.

## Usage

### CLI

```bash
python -m phase2.main --city Banashankari --price 600 --diet veg
```

### Python API

```python
from phase2 import UserInputHandler, UserInput

handler = UserInputHandler()
user_input = handler.parse(
    city="Banashankari",
    price="600",
    diet="veg",
)
# user_input.city, user_input.price, user_input.diet
```

## Run Tests

```bash
pytest phase2/tests/ -v
```
