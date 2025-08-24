import pandas as pd

pd.set_option("display.max_rows", 100)
df = pd.read_feather("data/replay/20200102.feather")

print(df.iloc[1:40].head(40))