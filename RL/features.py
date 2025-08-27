# ======================================================================
# RL/features.py
# 
# This file contains functions to extract features from the order book
# data for use in a reinforcement learning (RL) environment.
# ======================================================================

import numpy as np
from orderbook.timestamp import get_values
import orderbook.indicators as ind
from RL.env import RLExecEnv

N_LEVELS = 20

def _depth_features(ts, df):
        """
        Returns the depth features: (ask_dpb, ask_v, bid_dpb, bid_v)
        """
        values = get_values(ts, df)
        ask_values = values['ask_values'][N_LEVELS]
        bid_values = values['bid_values'][N_LEVELS]

        ask_dpb = _pad_truncate([ask['distance_to_mid'] for ask in ask_values], N_LEVELS)
        ask_v = _pad_truncate([ask['notional_USD'] for ask in ask_values], N_LEVELS)
        bid_dpb = _pad_truncate([bid['distance_to_mid'] for bid in bid_values], N_LEVELS)
        bid_v = _pad_truncate([bid['notional_USD'] for bid in bid_values], N_LEVELS)

        return np.concatenate([ask_dpb, ask_v, bid_dpb, bid_v])

def _indicator_features(values_now, values_prev):
    """
     Returns a vector of indicators.
    """
    indicators = ind.get_rl_values(values_now, values_prev)
    return np.array([
        indicators["best_bid"],
        indicators["best_ask"],
        indicators["best_bid_size"],
        indicators["best_ask_size"],
        indicators["midpoint"],
        indicators["spread"],
        indicators["normalized_spread"],
        indicators["micro_price"],
        indicators["bid_depth"],
        indicators["ask_depth"],
        indicators["liquidity_ratio"],
        indicators["orderbook_slope"],
        indicators["book_pressure_index"],
        indicators["VAMP"],
        indicators["VAMP_var_midpoint"],
        indicators["VAMP_ask"],
        indicators["VAMP_ask_var_midpoint"],
        indicators["VAMP_bid"],
        indicators["VAMP_bid_var_midpoint"],
        indicators["std_bid"],
        indicators["std_ask"],
        indicators["imbalance_top_of_book"],
        indicators["imbalance_multi_levels"],
        indicators["delta_spread"],
        indicators["delta_midpoint"],
        indicators["delta_VAMP"],
        indicators["delta_std_bid"],
        indicators["delta_std_ask"],
        indicators["orderflow_imbalance"]
    ], dtype=np.float32)

def _pad_truncate(x, n, pad_value=0.0):
        """
        Pads or truncates a 1D array to a fixed length n.
        """
        x = np.asarray(list(x), dtype=np.float32)
        if x.shape[0] >= n:
            return x[:n]
        out = np.full((n,), pad_value, dtype=np.float32)
        out[:x.shape[0]] = x
        return out