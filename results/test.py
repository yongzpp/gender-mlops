import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score
)

data = pd.read_csv("./target.csv")
data = data.head(50)
print(data.head())

print(accuracy_score(data["prediction"], data["gender"]))
print(recall_score(data["prediction"], data["gender"], average="binary", pos_label="M"))
print(
    precision_score(data["prediction"], data["gender"], average="binary", pos_label="M")
)
print(f1_score(data["prediction"], data["gender"], average="binary", pos_label="M"))
