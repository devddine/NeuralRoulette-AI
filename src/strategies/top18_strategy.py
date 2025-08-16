"""
Top-18 Strategy Implementation
Covers half the roulette wheel for lower risk
"""

import asyncio
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.utils import to_categorical
import os
from datetime import datetime

class Top18Strategy:
    """Strategy that covers 18 numbers (half the wheel)"""
    
    def __init__(self, balance=10.0, auto_train=False):
        self.name = "Top-18 Numbers"
        self.description = "Lower risk - covers half the wheel"
        self.balance = balance
        self.auto_train = auto_train
        self.game_history = []
        self.total_spins = 0
        self.correct_predictions = 0
        self.model_file = "models/top18_model.keras"
        
        # Configuration
        self.sequence_length = 10
        self.roulette_range = 37
        self.epochs = 50
        self.batch_size = 32
        
        # Betting
        self.bet_amount = 0.01
        self.payout = 35
        
        # Roulette colors
        self.red_numbers = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
        self.black_numbers = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}
    
    def get_color(self, number):
        """Get the color of a roulette number"""
        if number == 0:
            return "green"
        elif number in self.red_numbers:
            return "red"
        else:
            return "black"
        
    def load_model(self):
        """Load or create the LSTM model"""
        if os.path.exists(self.model_file):
            print(f"✅ Loading existing model: {self.model_file}")
            return load_model(self.model_file)
        else:
            print("🔄 Creating new model...")
            return self.build_model()
    
    def build_model(self):
        """Build LSTM neural network"""
        model = Sequential([
            LSTM(128, input_shape=(self.sequence_length, 1), return_sequences=True),
            Dropout(0.2),
            LSTM(64, return_sequences=False),
            Dropout(0.2),
            Dense(64, activation="relu"),
            Dense(self.roulette_range, activation="softmax")
        ])
        model.compile(
            loss="categorical_crossentropy",
            optimizer="adam",
            metrics=["accuracy"]
        )
        return model
    
    def preprocess_data(self, data):
        """Prepare roulette data for LSTM training"""
        X, y = [], []
        for i in range(len(data) - self.sequence_length):
            X.append(data[i : i + self.sequence_length])
            y.append(data[i + self.sequence_length])
        
        if not X:
            return None, None
            
        X = np.array(X) / 36.0
        X = X.reshape((X.shape[0], self.sequence_length, 1))
        y = to_categorical(y, num_classes=self.roulette_range)
        return X, y
    
    def predict_numbers(self, recent_results):
        """Predict the top 18 most likely numbers"""
        if len(recent_results) < self.sequence_length:
            return list(range(18))  # Default to first 18 numbers
            
        model = self.load_model()
        sequence = np.array(recent_results[-self.sequence_length:]) / 36.0
        sequence = sequence.reshape((1, self.sequence_length, 1))
        
        probabilities = model.predict(sequence, verbose=0)[0]
        top_indices = np.argsort(probabilities)[-18:][::-1]
        predicted_numbers = [int(idx) for idx in top_indices]
        
        return predicted_numbers
    
    def calculate_bets(self, predicted_numbers):
        """Calculate bet amounts for 18 numbers"""
        total_bet = min(self.balance * 0.1, 18.0 * self.bet_amount)
        bet_per_number = total_bet / len(predicted_numbers)
        return {num: bet_per_number for num in predicted_numbers}
    
    async def run_simulation(self):
        """Run the betting simulation"""
        print(f"\n🎰 Starting {self.name} Strategy")
        print(f"💰 Initial Balance: ${self.balance:.2f}")
        print(f"🎯 Numbers to Predict: 18")
        print(f"📊 Target Win Rate: 48.65%")
        print("=" * 50)
        
        # Simulate roulette spins for demonstration
        import random
        for spin in range(100):  # Simulate 100 spins
            # Generate random roulette number
            actual_number = random.randint(0, 36)
            self.game_history.append(actual_number)
            
            if len(self.game_history) >= self.sequence_length:
                # Make prediction
                predicted_numbers = self.predict_numbers(self.game_history)
                
                # Calculate bets
                bets = self.calculate_bets(predicted_numbers)
                total_bet = sum(bets.values())
                
                # Check if prediction was correct
                if actual_number in predicted_numbers:
                    self.correct_predictions += 1
                    winnings = bets[actual_number] * self.payout
                    self.balance += winnings - total_bet
                else:
                    self.balance -= total_bet
                
                self.total_spins += 1
                
                # Display results
                win_rate = (self.correct_predictions / self.total_spins) * 100
                print(f"\n🎯 Spin {self.total_spins}: {actual_number}")
                print(f"🔮 Predicted: {len(predicted_numbers)} numbers")
                print(f"💰 Bet: ${total_bet:.2f}")
                print(f"🏆 Win Rate: {win_rate:.2f}% ({self.correct_predictions}/{self.total_spins})")
                print(f"💸 Balance: ${self.balance:.2f}")
                
                # Auto-train if enabled
                if self.auto_train and len(self.game_history) >= 20:
                    X, y = self.preprocess_data(self.game_history)
                    if X is not None:
                        model = self.load_model()
                        model.fit(X, y, epochs=self.epochs, batch_size=self.batch_size, verbose=0)
                        model.save(self.model_file)
                        print("💾 Model updated with new data")
                
                # Stop if balance depleted
                if self.balance <= 0:
                    print("❌ Balance depleted. Ending simulation.")
                    break
                
                await asyncio.sleep(0.1)  # Simulate real-time delay
