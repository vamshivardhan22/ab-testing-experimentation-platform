from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT = DATA_DIR / "landing_page_experiment.csv"


def build_experiment(seed=99, visitors=50000):
    rng = np.random.default_rng(seed)
    DATA_DIR.mkdir(exist_ok=True)
    variants = rng.choice(["Old Landing Page", "New Landing Page"], size=visitors, p=[0.5, 0.5])
    base_ctr = np.where(variants == "Old Landing Page", 0.118, 0.132)
    base_conversion = np.where(variants == "Old Landing Page", 0.048, 0.056)
    clicked = rng.random(visitors) < base_ctr
    converted = clicked & (rng.random(visitors) < base_conversion / base_ctr)
    revenue = np.where(converted, rng.gamma(3.0, 34.0, visitors), 0)

    data = pd.DataFrame(
        {
            "visitor_id": [f"VIS-{i:06d}" for i in range(1, visitors + 1)],
            "visit_date": pd.Timestamp("2026-01-01") + pd.to_timedelta(rng.integers(0, 45, visitors), unit="D"),
            "variant": variants,
            "clicked": clicked.astype(int),
            "converted": converted.astype(int),
            "revenue": revenue.round(2),
            "device": rng.choice(["Desktop", "Mobile", "Tablet"], visitors, p=[0.45, 0.44, 0.11]),
            "traffic_source": rng.choice(["Paid Search", "Organic", "Social", "Email"], visitors, p=[0.32, 0.29, 0.24, 0.15]),
        }
    )
    return data.sort_values("visit_date")


def main():
    experiment = build_experiment()
    experiment.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(experiment):,} experiment rows to {OUTPUT}")


if __name__ == "__main__":
    main()
