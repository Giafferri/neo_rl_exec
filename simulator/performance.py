# =============================================================
# simulator/performance.py
#
# This file contains functions to evaluate and print the performance
# in the limit order book (LOB) simulation.
# =============================================================

def get_performance(initial_cash, initial_btc, current_cash, current_btc, values_at_ts, goal, target, duration):
    
    total_value = current_cash + current_btc * values_at_ts['ask_values'][0]['midpoint_USD']
    initial_value = initial_cash + initial_btc * values_at_ts['ask_values'][0]['midpoint_USD']
    
    pnl = total_value - initial_value
    pnl_percentage = (pnl / initial_value) * 100 if initial_value != 0 else 0

    # Determine if the goal was achieved
    if goal == 'cash':
        achieved = current_cash <= (initial_cash * target)
    else:  # goal == 'btc'
        achieved = current_btc <= (initial_btc * target)
    
    return {
        'cash_at_t': current_cash,
        'btc_at_t': current_btc,
        'initial_cash': initial_cash,
        'initial_btc': initial_btc,
        'total_portfolio_value': total_value,
        'pnl': pnl,
        'pnl_percentage': pnl_percentage,
        'achieved_goal': achieved,
        'duration': duration,
        'target': target,
        'goal': goal
    }

def slippage(values, quantity_BTC=None, quantity_USD=None, side="buy"):
    """
    Estimate slippage of a market order using order book levels.
    Supports input in BTC or USD.
    
    Args:
        values (dict): snapshot of orderbook values.
        quantity_BTC (float, optional): order size in BTC.
        quantity_USD (float, optional): order size in USD.
        side (str): "buy" or "sell".
    
    Returns:
        float: slippage in % relative to midpoint, or None if not enough depth.
    """
    bid_values = values.get('bid_values', [])
    ask_values = values.get('ask_values', [])

    # Get midpoint
    midpoint_val = None
    if ask_values:
        midpoint_val = ask_values[0].get('midpoint_USD')
    elif bid_values:
        midpoint_val = bid_values[0].get('midpoint_USD')

    if midpoint_val is None or midpoint_val == 0:
        return None

    # Convert USD -> BTC if needed
    if quantity_BTC is None and quantity_USD is not None:
        quantity_BTC = quantity_USD / midpoint_val
    elif quantity_BTC is None:
        raise ValueError("You must provide either quantity_BTC or quantity_USD")

    # Select depth side
    depth = ask_values if side == "buy" else bid_values
    if not depth:
        return None

    filled = 0.0
    cost = 0.0
    levels = depth if side == "buy" else reversed(depth)

    for lvl in levels:
        size = lvl['size_BTC']
        price = lvl['midpoint_USD'] + lvl['distance_to_mid']  # approx actual price
        if filled + size >= quantity_BTC:
            cost += (quantity_BTC - filled) * price
            filled = quantity_BTC
            break
        else:
            cost += size * price
            filled += size

    if filled < quantity_BTC:
        return None  # not enough depth

    exec_price = cost / quantity_BTC
    return (exec_price - midpoint_val) / midpoint_val * 100 if side == "buy" else (midpoint_val - exec_price) / midpoint_val * 100


def print_performance_summary(performance):
    print("--------------------------------------------------------")
    print("Performance Summary:")
    print(f"Final Cash: {performance['cash_at_t']} USD")
    print(f"Final BTC: {performance['btc_at_t']} BTC")
    print(f"Total Portfolio Value: {performance['total_portfolio_value']} USD")
    print(f"Profit and Loss (PnL): {performance['pnl']} USD")
    print(f"PnL Percentage: {performance['pnl_percentage']:.2f}%")
    print(f"Achieved Goal: {'Yes' if performance['achieved_goal'] else 'No'}")
    print("--------------------------------------------------------")