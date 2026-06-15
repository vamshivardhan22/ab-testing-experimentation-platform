# A/B Testing & Experimentation Platform

A business-facing experimentation dashboard for comparing an old landing page against a new landing page. It includes hypothesis testing, conversion analysis, CTR analysis, revenue impact, and an executive recommendation.

## What It Demonstrates

- Experiment design and variant comparison.
- Click-through rate and conversion rate analysis.
- Two-proportion z-test with p-value and confidence interval.
- Revenue per visitor and projected business impact.
- SQL, Python, statistics, and business decision making.

## Run Locally

```powershell
pip install -r requirements.txt
python .\scripts\seed_data.py
streamlit run app.py
```

The app automatically creates `data/landing_page_experiment.csv` if it does not exist.

## Business Question

Should the company ship the new landing page?

The dashboard answers this with:

- Control vs treatment conversion rate.
- Statistical significance.
- Confidence interval.
- Revenue impact.
- Segment-level performance.

## Files

- `app.py` - Streamlit experimentation platform.
- `scripts/seed_data.py` - deterministic experiment dataset generator.
- `sql/experiment_queries.sql` - reusable SQL experiment queries.
- `data/landing_page_experiment.csv` - generated visitor-level experiment data.

