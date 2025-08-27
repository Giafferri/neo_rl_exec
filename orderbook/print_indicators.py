# ===================================================================
# orderbook/print_indicators.py
#
# This file contains a function to print various indicators for the
# order book at a specific timestamp.
# ===================================================================

def print_indicators(ts, values_at_ts, values_at_previous_ts):
    """
    Print various indicators for the order book at a specific timestamp.

    Args:
        ts (int): Timestamp in nanoseconds.
        values_at_ts (dict): Dictionary containing ASK and BID values at the specified timestamp.
        values_at_previous_ts (dict or None): Dictionary containing ASK and BID values at the previous timestamp, or None if not available.
    """
    import pandas as pd
    import orderbook.indicators as ind

    rl_values = ind.get_rl_values(values_at_ts, values_at_previous_ts)
    print(f"--------------------------------------------------------\nIndicators at Timestamp: {pd.to_datetime(ts, unit='ns')}\n--------------------------------------------------------")
    print("Top of Book:")
    print(f"Best Bid: {rl_values['best_bid']:.6f} %, Best Ask: {rl_values['best_ask']:.6f} %")
    print(f"Best Bid Size: {rl_values['best_bid_size']:.4f} BTC, Best Ask Size: {rl_values['best_ask_size']:.4f} BTC")
    print("Prices & Spread:")
    print(f"Midpoint: {rl_values['midpoint']:.2f} USD")
    print(f"Spread: {rl_values['spread']:.6f} %, Normalized Spread: {rl_values['normalized_spread']:.6f} %")
    print(f"Microprice: {rl_values['micro_price']:.9f} USD")
    print("Depth & Liquidity:")
    print(f"Bid Depth: {rl_values['bid_depth']:.4f} USD, Ask Depth: {rl_values['ask_depth']:.4f} USD")
    print(f"Liquidity Ratio: {rl_values['liquidity_ratio']:.4f}")
    print(f"Book Pressure Index: {rl_values['book_pressure_index']:.6f}")
    print("Volume Weighted Midpoints family:")
    print(f"VAMP: {rl_values['vamp']:.2f} USD, VAMP Var with Midpoint: {rl_values['vamp_var_midpoint']:.4f} %")
    print(f"VAMP Ask: {rl_values['vamp_ask']:.2f} USD, VAMP Ask Var with Midpoint: {rl_values['vamp_ask_var_midpoint']:.4f} %")
    print(f"VAMP Bid: {rl_values['vamp_bid']:.2f} USD, VAMP Bid Var with Midpoint: {rl_values['vamp_bid_var_midpoint']:.4f} %")
    print("Volatility:")
    print(f"Standard Deviation Bid: {rl_values['std_bid']:.4f}, Standard Deviation Ask: {rl_values['std_ask']:.4f}")
    print("Imbalances:")
    print(f"Imbalance Top of Book: {rl_values['imbalance_top_of_book']:.6f}, Imbalance Multi Levels: {rl_values['imbalance_multi_levels']:.6f}")
    print(f"Order Flow Imbalance: {rl_values['orderflow_imbalance'] if rl_values['orderflow_imbalance'] is not None else 0.0:.6f}")
    print("Deltas:")
    print(f"Delta Spread: {rl_values['delta_spread']:.6f} %, Delta Midpoint: {rl_values['delta_midpoint']:.6f} %")
    print(f"Delta VAMP: {rl_values['delta_vamp']:.4f} USD")
    print(f"Delta Standard Deviation Bid: {rl_values['delta_std_bid']:.4f}, Delta Standard Deviation Ask: {rl_values['delta_std_ask']:.4f}")
    print("--------------------------------------------------------")