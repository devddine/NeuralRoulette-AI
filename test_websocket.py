import asyncio
import json
from src.data.websocket_client import RouletteWebSocketClient

async def test_callback(number):
    print(f'Callback received number: {number}')

async def main():
    # Create a client
    client = RouletteWebSocketClient('ws://example.com', '123', '236')
    client.register_callback(test_callback)
    
    # Test with the provided message format
    test_message = '{"tableId":"236","last20Results":[{"time":"Aug 16, 2025 08:19:15 PM","result":"16","color":"red","multiplier":null,"slots":null,"gameId":"7337686411","powerUpList":null,"powerUpMultipliers":null,"resultMultiplier":null,"isFortuneRoulette":null,"frWinType":null,"frMul":null,"isPinballRoulette":null,"bonusWin":null,"privateRoulette":null}]}'
    
    # Process the message
    await client.process_message(test_message)
    
    # Test the simulation
    print("\nTesting simulation:")
    simulation_task = asyncio.create_task(client.simulate_data())
    
    # Let it run for a few seconds
    await asyncio.sleep(10)
    
    # Stop the simulation
    client.connected = False
    await simulation_task

if __name__ == "__main__":
    asyncio.run(main())