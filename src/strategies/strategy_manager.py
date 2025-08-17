"""Strategy Manager for NeuralRoulette-AI
Handles loading and running different betting strategies
"""

import importlib
import asyncio
import logging
from pathlib import Path

class StrategyManager:
    """Manages and runs different roulette betting strategies"""
    
    def __init__(self, strategy_name, balance=10.0, auto_train=False):
        self.strategy_name = strategy_name
        self.balance = balance
        self.auto_train = auto_train
        self.strategy = None
        self.logger = logging.getLogger("strategy_manager")
        
    async def load_strategy(self):
        """Dynamically load the selected strategy"""
        try:
            # Convert strategy name to class name (e.g., top1 -> Top1Strategy)
            class_name = f"{self.strategy_name.capitalize()}Strategy"
            
            # Import the strategy module
            module_name = f"src.strategies.{self.strategy_name}_strategy"
            module = importlib.import_module(module_name)
            
            # Get the strategy class
            strategy_class = getattr(module, class_name)
            
            # Create an instance of the strategy
            self.strategy = strategy_class(balance=self.balance, auto_train=self.auto_train)
            # self.logger.info(f"Loaded strategy: {self.strategy_name}")
            return True
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Failed to load strategy '{self.strategy_name}': {str(e)}")
            return False
    
    async def process_number(self, number):
        """Process a new roulette number"""
        if not self.strategy:
            self.logger.error("No strategy loaded")
            return
            
        # Add the number to the strategy's game history
        self.strategy.game_history.append(number)
        
        # If we have enough history, make a prediction and place bets
        if len(self.strategy.game_history) >= self.strategy.sequence_length:
            # Make prediction
            predicted_numbers = self.strategy.predict_numbers(self.strategy.game_history)
            
            # Calculate bets
            bets = self.strategy.calculate_bets(predicted_numbers)
            total_bet = sum(bets.values())
            
            # Check if prediction was correct
            if number in predicted_numbers:
                self.strategy.correct_predictions += 1
                winnings = bets[number] * self.strategy.payout
                self.strategy.balance += winnings - total_bet
            else:
                self.strategy.balance -= total_bet
            
            self.strategy.total_spins += 1
            
            # Calculate statistics
            win_rate = (self.strategy.correct_predictions / self.strategy.total_spins) * 100
            roi = ((self.strategy.balance - self.balance) / self.balance) * 100
            
            # Log results in a single line format
            self.logger.info(f"Number: {number}, Balance: ${self.strategy.balance:.2f}, Win Rate: {win_rate:.2f}%, ROI: {roi:.2f}%")
            
            # Display results
            print(f"\n🎲 Spin #{self.strategy.total_spins}")
            print(f"🎯 Result: {number} ({self.strategy.get_color(number)})")
            print(f"🔮 Predicted: {', '.join(str(n) for n in predicted_numbers)}")
            print("💰 Bets placed:")
            for bet_number, amount in bets.items():
                print(f"   {bet_number}: ${amount:.2f}")
            print(f"💵 Total bet: ${total_bet:.2f}")
            
            if number in predicted_numbers:
                print(f"✨ WIN! +${(winnings - total_bet):.2f}")
            else:
                print(f"❌ LOSS -${total_bet:.2f}")
            
            print(f"🏆 Win Rate: {win_rate:.2f}% ({self.strategy.correct_predictions}/{self.strategy.total_spins})")
            print(f"📈 ROI: {roi:.2f}%")
            print(f"💸 Balance: ${self.strategy.balance:.2f}")
            
            # Auto-train if enabled
            if self.auto_train and len(self.strategy.game_history) >= 20:
                try:
                    X, y = self.strategy.preprocess_data(self.strategy.game_history)
                    if X is not None and len(X) > 0:
                        model = self.strategy.load_model()
                        model.fit(X, y, epochs=5, batch_size=min(32, len(X)), verbose=0)
                        model.save(self.strategy.model_file)
                        print("💾 Model updated with new data")
                except Exception as e:
                    print(f"⚠️ Training error: {str(e)}")
                    # Continue without training
            
            # Limit history length to prevent memory issues
            if len(self.strategy.game_history) > 1000:
                self.strategy.game_history = self.strategy.game_history[-1000:]
            
            # Check if balance is depleted
            if self.strategy.balance <= 0:
                print("❌ Balance depleted. Stopping strategy.")
                return False
        else:
            # Not enough history yet
            print(f"📊 Not enough history yet ({len(self.strategy.game_history)}/{self.strategy.sequence_length}) - please wait, receiving numbers...")
        
        return True