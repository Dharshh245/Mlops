"""Stage 3: evaluate the model on the test split and write metrics + plots."""
import json
import pickle
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, f1_score

CLASS_NAMES = ["setosa", "versicolor", "virginica"]


def main() -> None:
    test = pd.read_csv("data/prepared/test.csv")
    X, y = test.drop(columns="target"), test["target"]

    with open("models/model.pkl", "rb") as f:
        model = pickle.load(f)
    preds = model.predict(X)

    metrics = {
        "accuracy": round(accuracy_score(y, preds), 4),
        "f1_macro": round(f1_score(y, preds, average="macro"), 4),
    }
    with open("metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(metrics)

    Path("plots").mkdir(exist_ok=True)
    disp = ConfusionMatrixDisplay.from_predictions(y, preds, display_labels=CLASS_NAMES, cmap="Blues")
    disp.ax_.set_title("Confusion matrix (test set)")
    plt.tight_layout()
    plt.savefig("plots/confusion_matrix.png", dpi=120)


if __name__ == "__main__":
    main()
