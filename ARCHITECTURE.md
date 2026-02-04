# Zomato AI Restaurant Recommendation Service – Architecture

## Overview

An AI-powered restaurant recommendation system that uses the Zomato dataset and Groq LLM to suggest restaurants based on user preferences: **city**, **price**, and **veg/non-veg** choice.

**Dataset:** [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)  
**Recommendation Engine:** Groq LLM  
**Interface:** CLI (initial) → WebUI (later)

---

## Phase-wise Development Plan

### STEP 1 – Input the Zomato Data
- Load dataset from Hugging Face or local CSV
- Validate schema and basic data quality
- Store/access data for downstream phases

### STEP 2 – User Input
- CLI prompts for: city, price (approx cost for two), veg/non-veg
- Validate and normalize user inputs

### STEP 3 – Integrate
- Connect user input to data pipeline
- Prepare context and filters for recommendation

### STEP 4 – Recommendation (Groq LLM)
- Build prompt with user preferences and filtered restaurant data
- Call Groq API to generate personalized recommendations
- Parse and structure LLM output

### STEP 5 – Display to the User
- Format recommendations (CLI output)
- Show restaurant name, rating, cost, cuisines, etc.

---

## Data Schema (Zomato Dataset)

| Column                    | Type    | Description                     |
|---------------------------|---------|---------------------------------|
| url                       | string  | Restaurant Zomato URL           |
| address                   | string  | Full address                    |
| name                      | string  | Restaurant name                 |
| online_order              | string  | Yes/No                          |
| book_table                | string  | Yes/No                          |
| rate                      | string  | Rating (e.g. 4.1/5)             |
| votes                     | int     | Number of votes                 |
| phone                     | string  | Contact                         |
| location                  | string  | Area/location                   |
| rest_type                 | string  | Type (e.g. Casual Dining)       |
| dish_liked                | string  | Popular dishes                  |
| cuisines                  | string  | Cuisine types                   |
| approx_cost(for two people)| string | Cost for two (₹)               |
| reviews_list              | string  | Reviews                         |
| menu_item                 | string  | Menu items                      |
| listed_in(type)           | string  | Category (e.g. Buffet, Cafes)   |
| listed_in(city)           | string  | City/area for filtering         |

---

## User Input Mapping

| User Input  | Maps To                        |
|-------------|--------------------------------|
| City        | `listed_in(city)` / `location` |
| Price       | `approx_cost(for two people)`  |
| Veg/Non-veg | Inferred from `cuisines` / `dish_liked` or future tagging |

---

## Tech Stack

- **Language:** Python
- **Data:** Hugging Face Datasets / Pandas
- **LLM:** Groq API
- **Interface:** CLI (argparse / click)

---

## Project Structure (Proposed)

```
Zomato_Ai_Recommendation/
├── ARCHITECTURE.md
├── .gitignore
├── requirements.txt
├── phase1/                    # Data ingestion
│   ├── __init__.py
│   ├── data_loader.py
│   ├── tests/
│   │   └── test_data_loader.py
│   └── data/                  # Local data (gitignored)
├── phase2/                    # User input (future)
├── phase3/                    # Integration (future)
├── phase4/                    # Groq LLM recommendation (future)
└── phase5/                    # Display (future)
```

---

## Notes

- No deployment step in this plan.
- Groq API key must be configured via environment variable (e.g. `GROQ_API_KEY`).
- Veg/non-veg inference may require heuristics or extra metadata in later phases.
