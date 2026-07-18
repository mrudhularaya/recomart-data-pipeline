"""Generate required EDA figures from validated recommendation data."""

import sys
from pathlib import Path

import matplotlib

# This pipeline renders files only; an interactive Tk backend breaks headless execution.
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)


def generate_eda_plots():
    root = Path(src_dir).parent
    validated = root / "data" / "validated"
    output = root / "reports" / "eda"
    output.mkdir(parents=True, exist_ok=True)
    reviews = pd.read_csv(validated / "reviews" / "reviews.csv")
    clickstream = pd.read_csv(validated / "clickstream" / "clickstream.csv")

    plt.figure(figsize=(7, 4))
    reviews["rating"].plot(kind="hist", bins=5, edgecolor="white", color="#1F77B4")
    plt.title("Distribution of Product Ratings")
    plt.xlabel("Rating")
    plt.ylabel("Review count")
    plt.tight_layout()
    plt.savefig(output / "rating_distribution.png", dpi=160)
    plt.close()

    popularity = reviews.groupby("product_id").size().sort_values(ascending=False).head(15)
    plt.figure(figsize=(9, 5))
    popularity.sort_values().plot(kind="barh", color="#2CA02C")
    plt.title("Top 15 Products by Review Interactions")
    plt.xlabel("Interaction count")
    plt.tight_layout()
    plt.savefig(output / "item_popularity.png", dpi=160)
    plt.close()

    users, products = reviews["user_id"].nunique(), reviews["product_id"].nunique()
    sparsity = 1 - len(reviews) / (users * products)
    summary = output / "eda_summary.md"
    summary.write_text(
        f"# EDA Summary\n\n- Reviews: {len(reviews):,}\n- Clickstream events: {len(clickstream):,}\n"
        f"- Unique users with reviews: {users:,}\n- Unique reviewed products: {products:,}\n"
        f"- User-item matrix sparsity: {sparsity:.2%}\n",
        encoding="utf-8",
    )
    return {"output_dir": str(output), "sparsity": sparsity}


if __name__ == "__main__":
    print(generate_eda_plots())
