"""Write the raw Iris dataset to data/iris.csv (deterministic output).

Run once before `dvc add data/iris.csv`. CI also uses it as a fallback
when the DVC remote is not reachable from GitHub Actions.
"""
from pathlib import Path

from sklearn.datasets import load_iris


def main() -> None:
    out = Path("data/iris.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    df = load_iris(as_frame=True).frame
    df.columns = ["sepal_length", "sepal_width", "petal_length", "petal_width", "target"]
    df.to_csv(out, index=False, lineterminator="\n")
    print(f"Wrote {len(df)} rows to {out}")


if __name__ == "__main__":
    main()
