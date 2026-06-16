from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "marketing_ab.csv"


def build_sample(seed=99, rows=25000):
    rng = np.random.default_rng(seed)
    variant = rng.choice(["Ad Campaign", "Public Service Announcement"], rows, p=[0.88, 0.12])
    total_ads = rng.negative_binomial(2, 0.08, rows) + 1
    base = np.where(variant == "Ad Campaign", 0.027, 0.018)
    ad_effect = np.minimum(total_ads, 80) * 0.00008
    converted = rng.random(rows) < np.clip(base + ad_effect, 0, 0.18)
    return pd.DataFrame(
        {
            "user_id": rng.choice(np.arange(1_000_000, 9_999_999), rows, replace=False),
            "variant": variant,
            "converted": converted.astype(int),
            "total_ads": total_ads,
            "most_ads_day": rng.choice(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], rows),
            "most_ads_hour": rng.integers(0, 24, rows),
        }
    )


def main():
    OUTPUT.parent.mkdir(exist_ok=True)
    build_sample().to_csv(OUTPUT, index=False)
    print(f"Wrote fallback A/B testing sample to {OUTPUT}")


if __name__ == "__main__":
    main()
