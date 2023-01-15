import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

PROB_M = 0.8
PROB_F = 0.2


def add_numerical(row):
    if row["gender"] == "M":
        return np.random.binomial(1, PROB_M)
    return np.random.binomial(1, PROB_F)


if __name__ == "__main__":
    data = pd.read_csv("./data/name_gender.csv")
    data["numerical"] = data.apply(add_numerical, axis=1)
    data.to_csv("./data/name_gender_revised.csv")

    df_train, df_val = train_test_split(data, test_size=0.33, random_state=1)
    df_train["prediction"] = df_train["gender"]
    df_train.to_csv("./data/train_revised.csv", index=False)
    df_val.to_csv("./data/val_revised.csv", index=False)
