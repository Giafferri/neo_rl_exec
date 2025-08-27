# =============================================================
# simulator/action.py
#
# This file contains functions to choose and execute actions
# in the limit order book (LOB) simulation.
# =============================================================

import pandas as pd
import numpy as np
from orderbook.timestamp import get_values

def transaction_cost(amount, is_maker=False):
    """
    Calculate the transaction cost in USD or BTC depending on the action.
    buy BTC with USD -> USD cost
    sell BTC for USD -> BTC cost
    
    Args:
        price (float): Execution price in USD.
        size (float): Trade size in BTC.
        is_maker (bool): True if order was maker, False if taker.
    
    Returns:
        float: Transaction cost in USD.
    """
    maker_fee_bps = 2.5   # 0.025%
    taker_fee_bps = 7.0   # 0.07%
    min_ticket_usd = 50.0  # minimum fee per order (USD), not realistic but useful for RL training to avoid micro choppy trades

    fee_rate_bps = maker_fee_bps if is_maker else taker_fee_bps
    fee = amount * (fee_rate_bps / 1e4)

    return max(fee, min_ticket_usd)

def buy(amount, ask_values, current_cash, current_btc):
    print("You chose to buy BTC.")
    tx_cost = transaction_cost(amount, is_maker=False) # in USD

    if amount + tx_cost > current_cash or amount <= 0:
        print("Insufficient cash balance.")
        return [current_cash, current_btc]
    
    # Track total cost in USD and BTC acquired
    total_cost = 0 
    total_btc = 0
    print(f"Transaction cost for buying {amount} USD worth of BTC: {tx_cost} USD")

    # Execute buy order using available ask levels
    for ask in reversed(ask_values):
        price = ask['midpoint_USD'] * (1 + ask['distance_to_mid'])
        notional = ask['notional_USD']
        # If we can afford the entire notional at this level
        if total_cost + notional <= amount:
            print(f"Level {ask['level']}: Buying {ask['size_BTC']} BTC at {price} USD/BTC for {notional} USD")
            total_cost += notional
            total_btc += ask['size_BTC']
        # If we can only afford part of the notional at this level
        else:
            print(f"Level {ask['level']}: Buying partial BTC at {price} USD/BTC")
            remaining = amount - total_cost
            btc_to_buy = remaining / price
            total_cost += remaining
            total_btc += btc_to_buy
            break

    # Update balances
    current_cash -= total_cost + tx_cost  # Deduct transaction cost in USD
    current_btc += total_btc

    average_buy_price = total_cost / total_btc if total_btc > 0 else 0
    print(f"Average buy price: {average_buy_price} USD/BTC")
    average_buy_price_distance_to_mid = (average_buy_price - ask_values[0]['midpoint_USD']) / ask_values[0]['midpoint_USD'] if total_btc > 0 else 0
    print(f"Average buy price distance to mid: {average_buy_price_distance_to_mid:.6f} %")

    return [current_cash, current_btc, total_btc, "buy"]

def sell(amount, bid_values, current_cash, current_btc):
    print("You chose to sell BTC.")
    tx_cost = transaction_cost(amount, is_maker=False) # in BTC

    if amount + tx_cost > current_btc or amount <= 0:
        print("Insufficient BTC balance.")
        return [current_cash, current_btc]
    
    # Track total revenue in USD and BTC sold
    total_revenue = 0 
    total_btc_sold = 0
    print(f"Transaction cost for selling {amount} BTC: {tx_cost} BTC")

    # Execute sell order using available bid levels
    for bid in bid_values:
        price = bid['midpoint_USD'] * (1 + bid['distance_to_mid'])
        size = bid['size_BTC']
        # If we can sell the entire size at this level
        if total_btc_sold + size <= amount:
            print(f"Level {bid['level']}: Selling {size} BTC at {price} USD/BTC for {size * price} USD")
            total_btc_sold += size
            total_revenue += size * price
        # If we can only sell part of the size at this level
        else:
            print(f"Level {bid['level']}: Selling partial BTC at {price} USD/BTC")
            remaining = amount - total_btc_sold
            total_btc_sold += remaining
            total_revenue += remaining * price
            break
    
    # Update balances
    current_cash += total_revenue
    current_btc -= total_btc_sold + tx_cost  # Deduct transaction cost in BTC

    average_sell_price = total_revenue / total_btc_sold if total_btc_sold > 0 else 0
    print(f"Average sell price: {average_sell_price} USD/BTC")
    average_sell_price_distance_to_mid = (average_sell_price - bid_values[0]['midpoint_USD']) / bid_values[0]['midpoint_USD'] if total_btc_sold > 0 else 0
    print(f"Average sell price distance to mid: {average_sell_price_distance_to_mid:.6f} %")

    return [current_cash, current_btc, total_btc_sold, "sell"]


def choose_action(values, current_cash, current_btc):
    print("Choose an action:")
    input_action = input("Enter 'b' to buy BTC with USD, 's' to sell BTC for USD, 'h' to hold, or 'q' to quit: ").strip().lower()

    # Get order book values at the given timestamp
    ask_values = values['ask_values']
    bid_values = values['bid_values']

    if input_action == 'b':
        amount = float(input("Enter the amount of USD to spend: "))
        return buy(amount, ask_values, current_cash, current_btc)
    elif input_action == 's':
        amount = float(input("Enter the amount of BTC to sell: "))
        return sell(amount, bid_values, current_cash, current_btc)
    elif input_action == 'h':
        print("You chose to hold.")
        return [current_cash, current_btc, 0, "hold"]
    elif input_action == 'q':
        print("Exiting the simulation.")
        exit()
    else:
        print("Invalid action. Please try again.")