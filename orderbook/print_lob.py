# =============================================================
# orderbook/print_lob.py
# =============================================================
import pandas as pd
from orderbook.timestamp import get_values
import orderbook.indicators as ind
    
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
    
    print("\n================ INDICATORS =============================")

    print("--- Midpoint & Spread ---")
    print(f"Midpoint: {ind.midpoint(values_at_ts):.2f} USD")
    print(f"Volume Weighted Midpoint: {ind.VAMP(values_at_ts):.2f} USD")
    print(f"Spread: {ind.spread(values_at_ts):.6f} %")
    print(f"Normalized Spread: {ind.normalized_spread(values_at_ts):.6f} %")

    print("--- VAMP Variance ---")
    print(f"VAMP Var with Midpoint: {ind.VAMP_var_midpoint(values_at_ts):.4f} %, VAMP Ask Var with Midpoint: {ind.VAMP_ask_var_midpoint(ask_values):.4f} %, VAMP Bid Var with Midpoint: {ind.VAMP_bid_var_midpoint(bid_values):.4f} %")

    print("--- Weighted Midpoints ---")
    print(f"Volume Ajusted Midpoint Price: {ind.VAMP_bid(bid_values):.2f} USD, Weighted Ask Midpoint: {ind.VAMP_ask(ask_values):.2f} USD")
    print(f"Microprice: {ind.micro_price(values_at_ts):.9f} USD")

    print("--- Liquidity ---")
    print(f"Best Bid: {ind.best_bid(bid_values):.6f} %, Best Ask: {ind.best_ask(ask_values):.6f} %")
    print(f"Best Bid Size: {ind.best_bid_size(bid_values):.4f} BTC, Best Ask Size: {ind.best_ask_size(ask_values):.4f} BTC")
    print(f"Bid Depth: {ind.bid_depth(bid_values):.4f} USD, Ask Depth: {ind.ask_depth(ask_values):.4f} USD")
    print(f"Liquidity Ratio: {ind.liquidity_ratio(values_at_ts):.4f}")
    print(f"Standard Deviation Bid: {ind.std_side(bid_values):.4f}, Standard Deviation Ask: {ind.std_side(ask_values):.4f}")

    print("--- Deltas ---")
    print(f"Delta Spread: {ind.delta_spread(values_at_ts, values_at_previous_ts):.6f} %")
    print(f"Delta Midpoint: {ind.delta_midpoint(values_at_ts, values_at_previous_ts):.6f} %")
    print(f"Delta VAMP: {ind.delta_VAMP(values_at_ts, values_at_previous_ts):.4f} USD")
    print(f"Delta std Bid: {ind.delta_std_side(bid_values, bid_values_at_previous_ts):.4f}, Delta std Ask: {ind.delta_std_side(ask_values, ask_values_at_previous_ts):.4f}")

    print("---Imbalance of the book---")
    print(f"imbalance Top: {ind.imbalance_top_of_book(values_at_ts)}")
    print(f"Multi level imbalance: {ind.imbalance_multi_levels(values_at_ts,5,0.6)}")
    print(f"Orderflow imbalance: {ind.order_flow_imbalance(values_at_ts,values_at_previous_ts,2,0.05)}")


    print("---Slippage---")
    print(f"Estimated Slippage: {ind.slippage(values_at_ts, quantity_BTC=30, side="buy"):.9f}")

    print("---Slope---")
    print(f"Orderbook Slope: {ind.orderbook_slope(values_at_ts,5)}")

    print("---BPI---")
    print(f"BPI: {ind.book_pressure_index(values_at_ts,5)}")

    print("========================================================\n")

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
