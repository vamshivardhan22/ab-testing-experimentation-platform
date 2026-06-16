# A/B Testing & Experimentation Platform

A professional experimentation dashboard built on a real marketing A/B testing dataset. It compares ad campaign exposure against public service announcement exposure and turns statistical results into a business recommendation.

## Dataset

Source: Kaggle Marketing A/B Testing dataset.

The dataset contains user-level experiment assignment, conversion outcome, total ads seen, most active ad day, and most active ad hour.

## Features

- Control vs treatment conversion rates.
- Relative lift and incremental conversions.
- Two-proportion z-test.
- p-value and 95% confidence interval.
- Segment analysis by day and hour.
- SQL-backed experiment summaries.

## Run Locally

```powershell
pip install -r requirements.txt
streamlit run app.py
```

## Business Question

Should the company ship or scale the ad campaign?

The dashboard answers with:

- Conversion lift versus control.
- Statistical significance.
- Confidence interval.
- Segment-level performance.
- Executive decision callout.

## Project Files

- `app.py` - Streamlit experimentation platform.
- `data/marketing_ab.csv` - cleaned real A/B testing data.
- `sql/experiment_queries.sql` - SQL experiment queries.
- `scripts/seed_data.py` - fallback synthetic generator kept for reproducibility.

