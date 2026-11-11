"""Stage 2: train a RandomForest classifier on the training split."""
import pickle
from pathlib import Path

import pandas as pd
import yaml
from sklearn.ensemble import RandomForestClassifier


def main() -> None:
    params = yaml.safe_load(open("params.yaml"))["train"]

    train = pd.read_csv("data/prepared/train.csv")
    X, y = train.drop(columns="target"), train["target"]

    model = RandomForestClassifier(
        n_estimators=params["n_estimators"],
        max_depth=params["max_depth"],
        random_state=params["random_state"],
    )
    model.fit(X, y)

    Path("models").mkdir(exist_ok=True)
    with open("models/model.pkl", "wb") as f:
        pickle.dump(model, f)
    print("Saved models/model.pkl")


if __name__ == "__main__":
    main()
