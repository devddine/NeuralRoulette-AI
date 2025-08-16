"""
NeuralRoulette-AI Configuration Settings
Central configuration management for all strategies and system parameters
"""

import os
from dataclasses import dataclass
from typing import Dict, Any

# WebSocket Configuration
WS_URL = "wss://dga.pragmaticplaylive.net/ws"
CASINO_ID = "ppcds00000003709"
TABLE_ID = "236"
CURRENCY = "USD"

# Model Configuration
MODEL_DIR = "models"
SEQUENCE_LENGTH = 10
ROULETTE_RANGE = 37
EPOCHS = 50
BATCH_SIZE = 32

# Betting Configuration
STARTING_BALANCE = 10.00
MIN_BET_AMOUNT = 0.01
PAYOUT_RATIO = 35

@dataclass
class StrategyConfig:
    """Configuration for each betting strategy"""
    name: str
    model_file: str
    description: str
    risk_level: str
    numbers_to_predict: int
    bet_multiplier: float
    target_win_rate: float

# Strategy configurations
STRATEGIES = {
    "top1": StrategyConfig(
        name="Top-1 Single Number",
        model_file="top1_model.keras",
        description="Highest risk/reward - predicts single most likely number",
        risk_level="High",
        numbers_to_predict=1,
        bet_multiplier=1.0,
        target_win_rate=2.71
    ),
    "top3": StrategyConfig(
        name="Top-3 Numbers",
        model_file="top3_model.keras",
        description="Medium risk - predicts top 3 most likely numbers",
        risk_level="Medium",
        numbers_to_predict=3,
        bet_multiplier=0.33,
        target_win_rate=8.11
    ),
    "top18": StrategyConfig(
        name="Top-18 Numbers",
        model_file="top18_model.keras",
        description="Lower risk - covers half the wheel",
        risk_level="Low",
        numbers_to_predict=18,
        bet_multiplier=0.055,
        target_win_rate=48.65
    ),
    "topm": StrategyConfig(
        name="Top-M Dynamic",
        model_file="topm_model.keras",
        description="Adaptive strategy based on confidence levels",
        risk_level="Variable",
        numbers_to_predict=0,  # Dynamic
        bet_multiplier=0.0,    # Dynamic
        target_win_rate=0.0    # Dynamic
    )
}

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_FILE = "logs/neuralroulette.log"

# Performance Tracking
MAX_HISTORY_LENGTH = 1000
SAVE_INTERVAL = 100  # Save model every 100 spins
