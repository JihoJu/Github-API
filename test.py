import csv
import pandas as pd

data = pd.read_csv("./member.csv", encoding="cp949")

for i in range(len(data)):
    data.at[i, "Organization_id"] = i + 1

data.to_csv("./member2.csv", index=False, encoding="cp949")