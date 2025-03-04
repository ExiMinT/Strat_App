import asyncio
import websockets
import json


async def send_message():
    try:
        # Connect to WebSocket server
        async with websockets.connect('ws://35.197.214.65:8080') as websocket:
            print("Connected to WebSocket server.")

            # Message to send
            message = {
                "action": "select_strategy",
                "lobby_id": "lobby_1",
                "strategy": "Dust 2 - T-Side"
            }

            # Send the message
            await websocket.send(json.dumps(message))
            print("Message sent: ", message)

            # Receive a response
            response = await websocket.recv()
            print(f"Received response: {response}")

    except Exception as e:
        print(f"Error: {e}")


# Run the async function
asyncio.run(send_message())
