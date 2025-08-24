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