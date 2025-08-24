import pandas as pd
from orderbook.print_lob import show_lob, show_ts_lob
from orderbook.timestamp import get_values
from orderbook.orderbook_files import load_orderbook_data

pd.set_option("display.max_rows", 100)
paths = ["data/replay/20200101.feather", 
         "data/replay/20200102.feather", 
         "data/replay/20200103.feather"]

nb_timestamps = 50

df = load_orderbook_data(paths)
ts = 1577822404279921920
values_at_ts = get_values(ts, df)
values_at_previous_ts = get_values(ts - 1000000000, df) if ts - 1000000000 in df['timestamp_ns'].values else None

# show_lob(nb_timestamps)
# show_ts_lob(ts, values_at_ts, values_at_previous_ts)
show_lob(ts, nb_timestamps, df)
# print(get_values(1577822404279921920))