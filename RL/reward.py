# =============================================================
# RL/reward.py
#
# This file contains functions to compute rewards for the RL agent
# based on its performance in the limit order book (LOB) simulation.
# The reward is calculated based on profit and loss (PnL) and other
# performance metrics.
# =============================================================

from simulator.performance import get_performance
from math import sqrt

# Weights to tune the importance of PnL terms
PNL_WEIGHT_STEP = 100   # weight for per-step PnL (including t=1 and deltas)
PNL_WEIGHT_FINAL = 5  # weight for final PnL component

def compute_reward_at_t(performance, sum_rewards=0.0, step=1, previous_pnl=0.0):
    """
    Compute the reward based on pnl of the current step.
    Args:
        performance (dict): Performance metrics including 'pnl' and 'pnl_percentage'.
    Returns:
        float: Computed reward.
    """
    if step == 1:
        reward_at_t = PNL_WEIGHT_STEP * ((1 + performance['pnl_percentage']) ** 2 - 1)
        # Progress ratio in [0,1]
        progress_ratio = min(1.0, max(0.0, step / max(1, performance['duration'])))

        # Compute target inventory / cash ratio depending on goal
        if performance['goal'] == 'cash':
            target_ratio = performance['cash_at_t'] / max(1e-9, (performance['initial_cash'] * performance['target']))
            over = max(0.0, target_ratio - 1.0)
            under = max(0.0, 1.0 - target_ratio)
            # Asymmetry adapted to cash: stronger penalty if under target (behind schedule)
            penalty = (1.0 * over**2 + 2.0 * under**2) * (progress_ratio ** 2)
        else:
            target_ratio = performance['btc_at_t'] / max(1e-9, (performance['initial_btc'] * performance['target']))
            over = max(0.0, target_ratio - 1.0)
            under = max(0.0, 1.0 - target_ratio)
            # Asymmetry adapted to btc: stronger penalty if over target (too much inventory)
            penalty = (2.0 * over**2 + 1.0 * under**2) * (progress_ratio ** 2)

        reward_at_t = reward_at_t - penalty
        sum_rewards = reward_at_t
    else:
        # Base pnl reward increment
        reward_at_t = PNL_WEIGHT_STEP * ((1 + (performance['pnl_percentage'] - previous_pnl)) ** 2 - 1)
        print(f"PnL: {performance['pnl_percentage']:.6f} Previous Pnl: {previous_pnl:.6f}")

        # Progress ratio in [0,1]
        progress_ratio = min(1.0, max(0.0, step / max(1, performance['duration'])))

        # Compute target inventory / cash ratio depending on goal
        if performance['goal'] == 'cash':
            target_ratio = performance['cash_at_t'] / max(1e-9, (performance['initial_cash'] * performance['target']))
        else:
            target_ratio = performance['btc_at_t'] / max(1e-9, (performance['initial_btc'] * performance['target']))

        # Penalty grows near the end if far from target (goal-aware asymmetry)
        over = max(0.0, target_ratio - 1.0)
        under = max(0.0, 1.0 - target_ratio)
        if performance['goal'] == 'cash':
            # Behind schedule on cash => under should be penalized more
            penalty = (1.0 * over**2 + 2.0 * under**2) * (progress_ratio ** 2)
        else:
            # Behind schedule on inventory => over should be penalized more
            penalty = (2.0 * over**2 + 1.0 * under**2) * (progress_ratio ** 2)

        reward_at_t = reward_at_t - penalty
        sum_rewards += reward_at_t

    return [reward_at_t, sum_rewards, performance['pnl_percentage']]

def compute_final_reward(performance, sum_rewards=0.0):
    """
    Compute the overall reward based on performance metrics.
    Args:
        performance (dict): Performance metrics including 'pnl' and 'pnl_percentage'.
        sum_rewards (float): Cumulative reward over time.
    Returns:
        float: Computed reward.
    """
    final_reward = PNL_WEIGHT_FINAL * (((1 + performance['pnl_percentage']) ** 2 - 1) / 2)

    if performance['goal'] == 'cash':
        target_ratio = performance['cash_at_t'] / max(1e-9, (performance['initial_cash'] * performance['target']))
    else:
        target_ratio = performance['btc_at_t'] / max(1e-9, (performance['initial_btc'] * performance['target']))

    # Terminal penalty based on final distance to target (goal-aware, negative contribution)
    over = max(0.0, target_ratio - 1.0)
    under = max(0.0, 1.0 - target_ratio)
    if performance['goal'] == 'cash':
        # Cash below target is worse at the end
        final_reward -= (5.0 * over**2 + 50.0 * under**2)
    else:
        # Inventory above target is worse at the end
        final_reward -= (50.0 * over**2 + 5.0 * under**2)

    if not performance['achieved_goal']:
        final_reward -= 10  # Large penalty if goal not achieved

    return final_reward