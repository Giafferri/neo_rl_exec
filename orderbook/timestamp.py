# =============================================================
# orderbook/timestamp.py
# =============================================================
import pandas as pd
from orderbook.orderbook_files import load_orderbook_data

def get_values(ts, df):
    """
    Get the ASK and BID values at a specific timestamp from the order book data using the midpoint/distance schema.
    Args:
        ts (int): Timestamp in nanoseconds.
        paths (list[str]): List of paths to the order book data files.
    Returns:
        dict: A dictionary containing 'ask_values' and 'bid_values', each a list of dictionaries with order book details including 'midpoint_USD' and 'distance_to_mid' fields instead of 'price_USD'.
    """
    # Check if the timestamp exists in the DataFrame
    if ts not in df['timestamp_ns'].values:
        raise ValueError(f"Timestamp {ts} not found in the order book data.")
    
    index = df.index[df['timestamp_ns'] == ts].tolist()[0] 
    ask_values = []
    bid_values = []

    # Collect ASK side values
    for lvl in reversed(range(20, 40)):
        if index + lvl < len(df):
            row = df.iloc[index + lvl]
            ask_values.append({
                'side': row['side'],
                'level': row['level'],
                'midpoint_USD': row['midpoint_USD'],
                'distance_to_mid': row['distance_to_mid'],
                'notional_USD': row['notional_USD'],
                'size_BTC': row['size_BTC'],
                'cancel_notional_USD': row['cancel_notional_USD'],
                'limit_notional_USD': row['limit_notional_USD'],
                'market_notional_USD': row['market_notional_USD']
            })

    # Collect BID side values
    for lvl in range(0, 20):
        if index + lvl < len(df):
            row = df.iloc[index + lvl]
            bid_values.append({
                'side': row['side'],
                'level': row['level'],
                'midpoint_USD': row['midpoint_USD'],
                'distance_to_mid': row['distance_to_mid'],
                'notional_USD': row['notional_USD'],
                'size_BTC': row['size_BTC'],
                'cancel_notional_USD': row['cancel_notional_USD'],
                'limit_notional_USD': row['limit_notional_USD'],
                'market_notional_USD': row['market_notional_USD']
            })

    return {
        'ask_values': ask_values,
        'bid_values': bid_values
    }