import json
import pandas as pd
data = json.load(open("qanta.train.2018.04.18.json"))
df = pd.json_normalize(data["questions"])
df = df[df["difficulty"] == "MS"]
print(df[df["page"] == "Osmosis"])