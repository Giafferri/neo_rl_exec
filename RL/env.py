# =============================================================
# RL/env.py
#
# This file defines the environment for a reinforcement learning (RL) agent
# to interact with a limit order book (LOB) simulation. It includes functions
# to reset the environment, take actions, and compute rewards based on the
# agent's performance.
# =============================================================

from __future__ import annotations
import gymnasium as gym
import numpy as np
from gymnasium import spaces

from orderbook.timestamp import get_values
from simulator.performance import get_performance
from RL.reward import compute_reward_at_t, compute_final_reward
import simulator.action as sim_action
import orderbook.indicators as ind

class RLExecEnv(gym.Env):
    """
    Custom Environment for Reinforcement Learning in a Limit Order Book (LOB) simulation.
    The agent interacts with the environment by taking actions to buy/sell BTC
    and receives rewards based on its performance.
    """
    metadata = {"render_modes": []}

    def __init__(self, df, initial_cash=50000000, initial_btc=250, goal='btc', target=0.1, duration=3600, start_idx=40, use_builder=False):
        super(RLExecEnv, self).__init__()

        self.df = df
        self.initial_cash = float(initial_cash)
        self.initial_btc = float(initial_btc)
        self.goal = goal
        self.target = float(target)
        self.duration = int(duration)
        self.base_idx = int(start_idx)
        self.use_builder = use_builder
        self.N_LEVELS = 5

        # Discrete actions
        # Actions: 0 = Hold, 1 = Buy, 2 = Sell
        self.action_space = spaces.Discrete(3)

        # Observation space: [cash, btc, ask_price, bid_price, spread, mid_price, ask_volume, bid_volume]
        self.observation_dim = 8
        self.observation_space = spaces.Box(
            low=0, high=np.inf, shape=(8,), dtype=np.float32
        )