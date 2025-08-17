#!/usr/bin/env python3
"""
NeuralRoulette-AI Main Entry Point
Unified execution script for all roulette prediction strategies

Usage:
    python main.py --strategy top1
    python main.py --strategy top3 --balance 50.0
    python main.py --strategy top18 --auto-train
    python main.py --list-strategies
"""

import argparse
import asyncio
import sys
import os
import logging
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import STRATEGIES, WS_URL, CASINO_ID, TABLE_ID, CURRENCY
from src.data.websocket_client import RouletteWebSocketClient
from src.strategies.strategy_manager import StrategyManager

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="NeuralRoulette-AI: Advanced AI Roulette Prediction System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --strategy top1                    # Run top-1 strategy
  python main.py --strategy top3 --balance 100    # Run with $100 balance
  python main.py --strategy top18 --auto-train    # Auto-train on new data
  python main.py --list-strategies                # Show available strategies
        """
    )
    
    parser.add_argument(
        '--strategy',
        choices=['top1', 'top3', 'top18', 'topm'],
        default='top1',
        help='Prediction strategy to use (default: top1)'
    )
    
    parser.add_argument(
        '--balance',
        type=float,
        default=10.0,
        help='Starting balance for simulation (default: 10.0)'
    )
    
    parser.add_argument(
        '--auto-train',
        action='store_true',
        help='Enable automatic model training on new data'
    )
    
    parser.add_argument(
        '--list-strategies',
        action='store_true',
        help='List available strategies and exit'
    )
    
    parser.add_argument(
        '--simulate',
        action='store_true',
        help='Use simulated data instead of live WebSocket connection'
    )
    
    return parser.parse_args()

def list_strategies():
    """List all available strategies"""
    print("\n🎰 NeuralRoulette-AI Available Strategies")
    print("=" * 50)
    
    for key, config in STRATEGIES.items():
        print(f"\n{key.upper()} - {config.name}")
        print(f"  Description: {config.description}")
        print(f"  Risk Level: {config.risk_level}")
        print(f"  Numbers to Predict: {config.numbers_to_predict}")
        print(f"  Target Win Rate: {config.target_win_rate}%")
        print(f"  Model File: {config.model_file}")
    
    print("\n" + "=" * 50)

def setup_logging():
    """Set up logging configuration"""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[
            logging.FileHandler("logs/roulette.log"),
            logging.StreamHandler()
        ]
    )

async def run_strategy(strategy_name, balance, auto_train, simulate=False):
    """Run the selected strategy with WebSocket data"""
    # Create strategy manager
    strategy_manager = StrategyManager(strategy_name, balance, auto_train)
    if not await strategy_manager.load_strategy():
        print(f"❌ Failed to load strategy: {strategy_name}")
        return
    
    # Create WebSocket client
    ws_client = RouletteWebSocketClient(WS_URL, CASINO_ID, TABLE_ID, CURRENCY)
    
    # Register callback to process new numbers
    ws_client.register_callback(strategy_manager.process_number)
    
    try:
        if simulate:
            print("🔄 Using simulated roulette data")
            await ws_client.simulate_data()
        else:
            # Connect to WebSocket
            if await ws_client.connect():
                print("✅ Connected to roulette WebSocket")
                await ws_client.listen()
            else:
                print("❌ Failed to connect to WebSocket")
                print("🔄 Falling back to simulation mode")
                await ws_client.simulate_data()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        if not simulate:
            await ws_client.disconnect()

async def async_main():
    """Async main function"""
    args = parse_arguments()
    
    if args.list_strategies:
        list_strategies()
        return
    
    # Create models directory if it doesn't exist
    os.makedirs("models", exist_ok=True)
    
    print(f"\n🚀 Starting NeuralRoulette-AI with {args.strategy} strategy")
    print(f"💰 Initial balance: ${args.balance}")
    print(f"🤖 Auto-training: {'Enabled' if args.auto_train else 'Disabled'}")
    print(f"🔄 Data source: {'Simulation' if args.simulate else 'Live WebSocket'}")
    
    # Show the configuration
    config = STRATEGIES[args.strategy]
    print(f"\n📊 Strategy Configuration:")
    print(f"  Name: {config.name}")
    print(f"  Description: {config.description}")
    print(f"  Risk Level: {config.risk_level}")
    print(f"  Target Win Rate: {config.target_win_rate}%")
    
    # Run the strategy
    await run_strategy(args.strategy, args.balance, args.auto_train, args.simulate)

def main():
    """Main application entry point"""
    # Set up logging
    setup_logging()
    
    # Run the async main function
    asyncio.run(async_main())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Graceful shutdown initiated...")
        print("Thank you for using NeuralRoulette-AI!")
