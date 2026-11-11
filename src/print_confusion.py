"""Print the test-set confusion matrix as a text table (used in the CML report)."""
import pickle

import pandas as pd
from sklearn.metrics import confusion_matrix

CLASS_NAMES = ["setosa", "versicolor", "virginica"]

test = pd.read_csv("data/prepared/test.csv")
with open("models/model.pkl", "rb") as f:
    model = pickle.load(f)
cm = confusion_matrix(test["target"], model.predict(test.drop(columns="target")))
print(pd.DataFrame(cm, index=CLASS_NAMES, columns=CLASS_NAMES))
