import asyncio
import websockets
import json

connected_clients = set()


async def register_client(websocket):
    """Register a new WebSocket client."""
    connected_clients.add(websocket)
    print(f"New client connected. Total clients: {len(connected_clients)}")


async def unregister_client(websocket):
    """Unregister a disconnected WebSocket client."""
    connected_clients.remove(websocket)
    print(f"Client disconnected. Total clients: {len(connected_clients)}")


async def handle_client(websocket, path):
    """Handle incoming WebSocket connections."""
    await register_client(websocket)

    try:
        async for message in websocket:
            data = json.loads(message)
            # Process the incoming message here
            action = data.get("action")

            if action == "update_strategy":
                # Handle strategy update message (or any other action)
                strategy = data.get("strategy")
                lobby_id = data.get("lobby_id")
                print(f"Strategy update: {strategy} in lobby {lobby_id}")
                await broadcast_message(f"Strategy {strategy} selected for lobby {lobby_id}")
            else:
                print(f"Unknown action received: {action}")

    finally:
        await unregister_client(websocket)


async def broadcast_message(message):
    """Broadcast a message to all connected clients."""
    for client in connected_clients:
        try:
            await client.send(message)
        except:
            # If there's an error (client disconnected), remove the client
            connected_clients.remove(client)


async def start_server():
    """Start the WebSocket server."""
    server = await websockets.serve(handle_client, "localhost", 8080)
    print("WebSocket server started on ws://localhost:8080")
    await server.wait_closed()


# Run the WebSocket server
if __name__ == "__main__":
    asyncio.run(start_server())
