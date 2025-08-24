# =============================================================
# orderbook/indicators.py
#
# These indicators are used to calculate various metrics from the order book data.
# They will help the agent to make informed decisions based on the order book state.
# =============================================================

import pandas as pd
from orderbook.timestamp import get_values

# =============================================================
# Best bids and asks
# =============================================================

def best_bid(bid_values):
    """
    Get the best bid distance-to-mid at a specific timestamp.
    Args:
        ts (int): Timestamp in nanoseconds.
        paths (list[str]): List of paths to the order book data files.
    Returns:
        float: Best bid distance-to-mid or None if no valid bid is found.
    """
    if not bid_values:
        return None
    
    # Get the best bid (highest bid price with non-zero size)
    best_bid = None
    for lvl in bid_values:
        if lvl['size_BTC'] == 0:
            continue
        else:
            best_bid = lvl['distance_to_mid']
            break
    
    return best_bid

def best_ask(ask_values):
    """
    Get the best ask distance-to-mid at a specific timestamp.
    Args:
        ts (int): Timestamp in nanoseconds.
        paths (list[str]): List of paths to the order book data files.
    Returns:
        float: Best ask distance-to-mid or None if no valid ask is found.
    """
    if not ask_values:
        return None
    
    # Get the best ask (lowest ask price with non-zero size)
    best_ask = None
    for lvl in reversed(ask_values):
        if lvl['size_BTC'] == 0:
            continue
        else:
            best_ask = lvl['distance_to_mid']
            break
    
    return best_ask

def best_bid_size(bid_values):
    """
    Get the size of the best bid at a specific timestamp.
    Args:
        ts (int): Timestamp in nanoseconds.
        paths (list[str]): List of paths to the order book data files.
    Returns:
        float: Size of the best bid or None if no valid bid is found.
    """
    if not bid_values:
        return None
    
    # Get the size of the best bid (highest bid price with non-zero size)
    best_bid_size = None
    for lvl in bid_values:
        if lvl['size_BTC'] == 0:
            continue
        else:
            best_bid_size = lvl['size_BTC']
            break
    
    return best_bid_size

def best_ask_size(ask_values):
    """
    Get the size of the best ask at a specific timestamp.
    Args:
        ts (int): Timestamp in nanoseconds.
        paths (list[str]): List of paths to the order book data files.
    Returns:
        float: Size of the best ask or None if no valid ask is found.
    """
    if not ask_values:
        return None
    
    # Get the size of the best ask (lowest ask price with non-zero size)
    best_ask_size = None
    for lvl in reversed(ask_values):
        if lvl['size_BTC'] == 0:
            continue
        else:
            best_ask_size = lvl['size_BTC']
            break
    
    return best_ask_size

# =============================================================
# Midpoints & spreads
# =============================================================

def midpoint(values):
    """
    Calculate the midpoint price at a specific timestamp using the provided midpoint field.
    Args:
        ts (int): Timestamp in nanoseconds.
        paths (list[str]): List of paths to the order book data files.
    Returns:
        float: Midpoint price or None if no valid bid and ask are found.
    """
    ask_values = values['ask_values']
    bid_values = values['bid_values']
    if ask_values:
        return ask_values[0]['midpoint_USD']
    if bid_values:
        return bid_values[0]['midpoint_USD']
    return None

def VAMP(values):
    """
    Calculate the volume adjusted midprice (VAMP) at a specific timestamp.
    Args:
        ts (int): Timestamp in nanoseconds.
        paths (list[str]): List of paths to the order book data files.
    Returns:
        float: Volume weighted midpoint or None if no valid bid and ask are found.
    """
    ask_values = values['ask_values']
    bid_values = values['bid_values']

    # Check if there are valid ask and bid values
    if not ask_values or not bid_values:
        return None

    # Ensure that there are non-zero sizes for both asks and bids
    if sum(ask['size_BTC'] for ask in ask_values) == 0 or sum(bid['size_BTC'] for bid in bid_values) == 0:
        return None
    
    # Calculate the volume weighted midpoint
    weighted_total_ask = sum(ask['notional_USD'] for ask in ask_values) / sum(ask['size_BTC'] for ask in ask_values)
    weighted_total_bid = sum(bid['notional_USD'] for bid in bid_values) / sum(bid['size_BTC'] for bid in bid_values)
    
    return (weighted_total_ask + weighted_total_bid) / 2

def VAMP_var_midpoint(values):
    """
    Calculate the volume adjusted midprice (VAMP) in percentage terms at a specific timestamp.
    Args:
        ts (int): Timestamp in nanoseconds.
        paths (list[str]): List of paths to the order book data files.
    Returns:
        float: Volume weighted midpoint in percentage or None if no valid bid and ask are found.
    """
    vamp = VAMP(values)
    midpoint_price = midpoint(values)

    if vamp is None or midpoint_price is None or midpoint_price == 0:
        return None
    
    return (vamp - midpoint_price) / midpoint_price * 100

def VAMP_ask(ask_values):
    """
    Calculate the weighted ask midpoint at a specific timestamp.
    Args:
        ts (int): Timestamp in nanoseconds.
        paths (list[str]): List of paths to the order book data files.
    Returns:
        float: Weighted ask midpoint or None if no valid ask is found.
    """
    if not ask_values:
        return None

    return sum(ask['notional_USD'] for ask in ask_values) / sum(ask['size_BTC'] for ask in ask_values)

def VAMP_ask_var_midpoint(ask_values):
    """
    Calculate the weighted ask midpoint in percentage terms at a specific timestamp.
    Args:
        ts (int): Timestamp in nanoseconds.
        paths (list[str]): List of paths to the order book data files.
    Returns:
        float: Weighted ask midpoint in percentage or None if no valid ask is found.
    """
    vamp_ask = VAMP_ask(ask_values)
    if not ask_values or ask_values[0]['midpoint_USD'] == 0:
        return None
    midpoint_price = ask_values[0]['midpoint_USD']

    if vamp_ask is None or midpoint_price is None or midpoint_price == 0:
        return None
    
    return (vamp_ask - midpoint_price) / midpoint_price * 100

def VAMP_bid(bid_values):
    """
    Calculate the weighted bid midpoint at a specific timestamp.
    Args:
        ts (int): Timestamp in nanoseconds.
        paths (list[str]): List of paths to the order book data files.
    Returns:
        float: Weighted bid midpoint or None if no valid bid is found.
    """
    return sum(bid['notional_USD'] for bid in bid_values) / sum(bid['size_BTC'] for bid in bid_values)

def VAMP_bid_var_midpoint(bid_values):
    """
    Calculate the weighted bid midpoint in percentage terms at a specific timestamp.
    Args:
        ts (int): Timestamp in nanoseconds.
        paths (list[str]): List of paths to the order book data files.
    Returns:
        float: Weighted bid midpoint in percentage or None if no valid bid is found.
    """
    vamp_bid = VAMP_bid(bid_values)
    if not bid_values or bid_values[0]['midpoint_USD'] == 0:
        return None
    midpoint_price = bid_values[0]['midpoint_USD']

    if vamp_bid is None or midpoint_price is None or midpoint_price == 0:
        return None
    
    return (vamp_bid - midpoint_price) / midpoint_price * 100

def spread(values):
    """
    Calculate the spread between the best bid and best ask in distance-to-mid terms.
    Args:
        df (pd.DataFrame): DataFrame containing order book data.
    Returns:
        float: Spread distance or None if no valid bid and ask are found.
    """
    ask_values = values['ask_values']
    bid_values = values['bid_values']
    return (best_ask(ask_values) - best_bid(bid_values)) if (best_ask(ask_values) is not None and best_bid(bid_values) is not None) else None

# =============================================================
# Depths, Imbalances, and Ratios
# =============================================================

def bid_depth(bid_values):
    """
    Calculate the total depth of bids in the order book at a specific timestamp.
    Args:
        bid_values (list[dict]): List of bid values at a specific timestamp.
    Returns:
        float: Total bid depth or None if no valid bids are found.
    """
    if not bid_values:
        return None
    return sum(bid['notional_USD'] for bid in bid_values) if any(bid['notional_USD'] > 0 for bid in bid_values) else None

def ask_depth(ask_values):
    """
    Calculate the total depth of asks in the order book at a specific timestamp.
    Args:
        ask_values (list[dict]): List of ask values at a specific timestamp.
    Returns:
        float: Total ask depth or None if no valid asks are found.
    """
    if not ask_values:
        return None
    return sum(ask['notional_USD'] for ask in ask_values) if any(ask['notional_USD'] > 0 for ask in ask_values) else None
    

def imbalance(df):
    pass

def liquidity_ratio(values):
    """
    Calculate the liquidity ratio at a specific timestamp.
    Args:
        df (pd.DataFrame): DataFrame containing order book data.
    Returns:
        float: Liquidity ratio or None if no valid bids and asks are found.
    """
    ask_values = values['ask_values']
    bid_values = values['bid_values']
    return bid_depth(bid_values) / ask_depth(ask_values) if (bid_depth(bid_values) is not None and ask_depth(ask_values) is not None) else None

# =============================================================
# Standard Deviations
# =============================================================

def std_side(values):
    """
    Calculate the standard deviation of notional on a specific side (bid or ask).
    Args:
        values (list[dict]): List of values on a specific side (bid or ask).
    Returns:
        float: Standard deviation of notional or None if no valid values are found.
    """
    if not values:
        return None
    
    notional = [lvl['notional_USD'] for lvl in values]
    if not notional:
        return None
    
    return pd.Series(notional).std()

# =============================================================
# Temporal Dynamics (t & t-1)
# =============================================================

def delta_spread(values, previous_values):
    """
    Calculate the change in spread between two timestamps.
    Args:
        values (dict): Current values containing 'ask_values' and 'bid_values'.
        previous_values (dict): Previous values containing 'ask_values' and 'bid_values'.
    Returns:
        float: Change in spread or None if no valid bids and asks are found.
    """
    current_spread = spread(values)
    previous_spread = spread(previous_values)

    if current_spread is None or previous_spread is None:
        return None
    
    return current_spread - previous_spread

def delta_midpoint(values, previous_values):
    """
    Calculate the change in midpoint between two timestamps.
    Args:
        values (dict): Current values containing 'ask_values' and 'bid_values'.
        previous_values (dict): Previous values containing 'ask_values' and 'bid_values'.
    Returns:
        float: Change in midpoint or None if no valid bids and asks are found.
    """
    current_midpoint = midpoint(values)
    previous_midpoint = midpoint(previous_values)

    if current_midpoint is None or previous_midpoint is None:
        return None
    
    return current_midpoint - previous_midpoint

def delta_VAMP(values, previous_values):
    """
    Calculate the change in volume weighted midpoint between two timestamps.
    Args:
        values (dict): Current values containing 'ask_values' and 'bid_values'.
        previous_values (dict): Previous values containing 'ask_values' and 'bid_values'.
    Returns:
        float: Change in volume weighted midpoint or None if no valid bids and asks are found.
    """
    current_vamp = VAMP(values)
    previous_vamp = VAMP(previous_values)

    if current_vamp is None or previous_vamp is None:
        return None
    
    return current_vamp - previous_vamp

def delta_std_side(side_values, previous_side_values):
    """
    Calculate the change in standard deviation of prices on a specific side (bid or ask) between two timestamps.
    Args:
        side_values (list[dict]): Current values on a specific side (bid or ask).
        previous_side_values (list[dict]): Previous values on a specific side (bid or ask).
    Returns:
        float: Change in standard deviation of prices or None if no valid values are found.
    """
    current_std = std_side(side_values)
    previous_std = std_side(previous_side_values)

    if current_std is None or previous_std is None:
        return None
    
    return current_std - previous_std

# =============================================================
# Others
# =============================================================

def micro_price(values):
    """
    Calculate the micro-price-like metric using distance-to-mid (dimensionless) at the top of book.

    Formula (using top-of-book levels):
        micro_metric = (d_ask * Q_bid + d_bid * Q_ask) / (Q_bid + Q_ask)

    Where:
        d_bid = best bid distance-to-mid (negative)
        d_ask = best ask distance-to-mid (positive)
        Q_bid = size at best bid
        Q_ask = size at best ask
    """
    ask_values = values['ask_values']
    bid_values = values['bid_values']

    # Basic presence checks
    if not ask_values or not bid_values:
        return None

    # Extract best distances and sizes
    p_bid = best_bid(bid_values)
    p_ask = best_ask(ask_values)
    q_bid = best_bid_size(bid_values)
    q_ask = best_ask_size(ask_values)

    # Validate extracted values
    if (p_bid is None or p_ask is None or q_bid is None or q_ask is None):
        return None

    denom = q_bid + q_ask
    if denom == 0:
        return None

    return (p_ask * q_bid + p_bid * q_ask) / denom