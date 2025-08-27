# =============================================================
# orderbook/print_lob.py
# =============================================================
import pandas as pd
from orderbook.timestamp import get_values
import orderbook.indicators as ind
import orderbook.print_indicators as pi
    
def show_ts_lob(ts, values_at_ts, values_at_previous_ts):
    """
    Show the order book at a specific timestamp.
    Args:
        ts (int): Timestamp in nanoseconds.
        paths (list[str]): List of paths to the order book data files.
    """
    # Get ASK and BID values at the specified timestamp
    # values_at_ts = get_values(ts, df)
    ask_values = values_at_ts['ask_values']
    bid_values = values_at_ts['bid_values'] 

    # values_at_previous_ts = get_values(ts - 1000000000, df) if ts - 1000000000 in df['timestamp_ns'].values else None
    ask_values_at_previous_ts = values_at_previous_ts['ask_values'] if values_at_previous_ts else []
    bid_values_at_previous_ts = values_at_previous_ts['bid_values'] if values_at_previous_ts else []

    print(f"--------------------------------------------------------\nOrderbook Timestamp: {pd.to_datetime(ts, unit='ns')}\n--------------------------------------------------------")
    print(f"Side | Level | Price (USD) | Midpoint (USD) | Distance (%) | Notional (USD) | Size (BTC)")

    # print ASK
    for ask in ask_values:
        price = ask['midpoint_USD'] * (1 + ask['distance_to_mid'])
        print(f"{ask['side']:4} | {ask['level']:5} | {price:11.2f} | {ask['midpoint_USD']:14.2f} | {ask['distance_to_mid']:12.6f} | {ask['notional_USD']:14.2f} | {ask['size_BTC']:10.4f}")

    # print BID
    for bid in bid_values:
        price = bid['midpoint_USD'] * (1 + bid['distance_to_mid'])
        print(f"{bid['side']:4} | {bid['level']:5} | {price:11.2f} | {bid['midpoint_USD']:14.2f} | {bid['distance_to_mid']:12.6f} | {bid['notional_USD']:14.2f} | {bid['size_BTC']:10.4f}")
    
    # print indicators
    pi.print_indicators(ts, values_at_ts, values_at_previous_ts)

def show_lob(ts_start, nb_ts=5, df=None):
    """
    Show the order book for a specified number of timestamps starting from ts_start.
    Args:
        ts_start (int): Starting timestamp in nanoseconds.
        nb_ts (int): Number of timestamps to show.
        paths (list[str]): List of paths to the order book data files.
    """
    print(f"Showing order book for {nb_ts} timestamps starting from {pd.to_datetime(ts_start, unit='ns')}")
    for i in range(nb_ts):
        ts = ts_start + i * 1000000000  # Each timestamp is 1 second apart, so increment by 1 billion nanoseconds
        values_at_ts = get_values(ts, df)
        values_at_previous_ts = get_values(ts - 1000000000, df) if ts - 1000000000 in df['timestamp_ns'].values else None
        show_ts_lob(ts, values_at_ts, values_at_previous_ts)
