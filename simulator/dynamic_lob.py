# =============================================================
# simulator/dynamic_lob.py
# 
# This file contains an interactive simulator for a limit order book (LOB).
# It allows users to visualize and interact with the LOB data, including
# placing orders and observing their effects on the order book.
# The user starts with a given cash and BTC balance, and he have
# to liquidate his position before the end of the simulation (cash or BTC, depending on the goal).
# =============================================================

import pandas as pd
import numpy as np
from orderbook.timestamp import get_values
from orderbook.orderbook_files import load_orderbook_data  
import orderbook.print_lob as print_lob
import simulator.action as action
from simulator.performance import print_performance_summary, get_performance, slippage
from RL.reward import compute_final_reward, compute_reward_at_t

def run(df, initial_cash=50000000, initial_btc=250, goal='cash', target=0.1, duration=3600):
    print("--------------------------------------------------------")
    print("Starting LOB simulation...")
    targeted_value = initial_cash * target if goal == 'cash' else initial_btc * (1 + target)
    print(f"Your goal is to opportunisticly liquidate (with pnl) your {goal} under the target of {targeted_value:.2f} in {duration} seconds.")
    print("--------------------------------------------------------")

    # Initialize balances and simulation parameters
    current_cash = initial_cash
    current_btc = initial_btc
    ts = df.iloc[40]['timestamp_ns']

    sum_rewards = 0.0 
    previous_pnl = 0.0
    pnl_history = []   # <<< nouvelle variable pour stocker le PnL de chaque étape

    print("--------------------------------------------------------")
    print(f"Initial Cash: {initial_cash} USD, Initial BTC: {initial_btc} BTC")
    print(f"Starting simulation at timestamp: {ts} for a duration of {duration} seconds.")
    print("--------------------------------------------------------")

    for step in range(1, duration):
        ts = df.iloc[step * 40]['timestamp_ns']
        values_at_ts = get_values(ts, df)
        values_at_previous_ts = get_values(ts - 1000000000, df) if ts - 1000000000 in df['timestamp_ns'].values else None
        
        print("--------------------------------------------------------")
        print(f"Cash: {current_cash} USD, BTC: {current_btc} BTC")
        print("--------------------------------------------------------")
        
        print_lob.show_ts_lob(ts, values_at_ts, values_at_previous_ts)
        result = action.choose_action(values_at_ts, current_cash, current_btc)
        
        if result is not None:
            current_cash, current_btc, trade_size, action_side = result
            print("--------------------------------------------------------")
            print(f"Updated Cash: {current_cash} USD, Updated BTC: {current_btc} BTC")
            print("--------------------------------------------------------")
            if (current_cash < targeted_value and goal == 'cash') or (current_btc < targeted_value and goal == 'btc'):
                print(f"Congratulations! You have achieved your goal of liquidating your {goal} under the target of {targeted_value:.2f}.")
                break

              # === SLIPPAGE ===
            if action_side in ["buy", "sell"] and trade_size > 0:
                slip = slippage(values_at_ts, quantity_BTC=trade_size, side=action_side)
                if slip is not None:
                 print(f"Slippage ({action_side}, {trade_size:.4f} BTC) at step {step}: {slip:.4f}%")

        else:
            print("Nothing happened, moving to next timestamp...")

        # === Calcul du PnL à CE step ===
        perf = get_performance(initial_cash, initial_btc, current_cash, current_btc,
                               values_at_ts, goal, target, duration)

        # Enregistrer le PnL dans l’historique
        pnl_history.append({
            "step": step,
            "pnl": perf["pnl"],
            "pnl_percentage": perf["pnl_percentage"],
            "portfolio_value": perf["total_portfolio_value"]
        })

        # Affichage direct du PnL
        print(f"PnL at step {step}: {perf['pnl']} USD ({perf['pnl_percentage']:.2f}%)")

        # === Reward ===
        rw_inter = compute_reward_at_t(perf, sum_rewards, step, previous_pnl)
        reward_at_t = rw_inter[0]
        sum_rewards = rw_inter[1]
        previous_pnl = rw_inter[2]

        print(f"Reward at step {step}: {reward_at_t:.4f}, Cumulative Reward: {sum_rewards:.4f}")

    # Performance finale
    final_performance = get_performance(initial_cash, initial_btc, current_cash, current_btc,
                                        values_at_ts, goal, target, duration)
    print_performance_summary(final_performance)
    print(f"Reward: {compute_final_reward(final_performance, sum_rewards)}")
    print("Simulation ended.")

    # === Récapitulatif complet du PnL à chaque étape ===
    print("\n================ PnL History Recap ================")
    for entry in pnl_history:
        print(f"Step {entry['step']:>4} | PnL: {entry['pnl']:>12.2f} USD | "
              f"{entry['pnl_percentage']:>6.2f}% | Portfolio: {entry['portfolio_value']:>12.2f} USD")
    print("===================================================")

    return pnl_history


        

def main():
    # Load order book data
    paths = ["data/replay/20200101.feather"]
    df = load_orderbook_data(paths)
    
    # Initial parameters
    initial_cash = float(input("Enter your initial cash (USD): ").strip())
    initial_btc = float(input("Enter your initial BTC: ").strip())
    goal = input("Enter your liquidation goal (cash/btc): ").strip().lower()
    target = float(input("Enter your final target of liquidation (ex: 0.1 for 10%, so you want to liquidate 9/10 of your position): ").strip())
    duration = int(input("Enter the duration of the simulation in seconds (default 3600s): ").strip() or 3600)

    # Run the simulation
    run(df, initial_cash, initial_btc, goal, target, duration)


if __name__ == "__main__":
    main()