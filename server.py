import asyncio
import websockets
import json

clients = {}


async def handle_connection(websocket):  # Accept two arguments
    client_id = str(websocket.remote_address)
    clients[client_id] = websocket
    print(f"New connection from {client_id}")

    try:
        async for message in websocket:
            data = json.loads(message)

            if data["action"] == "select_strategy":
                await handle_strategy_selection(data)

            elif data["action"] == "join_lobby":
                await handle_join_lobby(data, websocket)

            else:
                print(f"Unhandled action: {data['action']}")

    except websockets.exceptions.ConnectionClosed:
        print(f"Connection closed from {client_id}")
    finally:
        clients.pop(client_id, None)


async def handle_strategy_selection(data):
    strategy_name = data["strategy"]
    message = {"action": "update_strategy", "strategy": strategy_name}

    for client in clients.values():
        await client.send(json.dumps(message))


async def handle_join_lobby(data, websocket):
    lobby_id = data["lobby_id"]
    print(f"Client joined lobby: {lobby_id}")
    join_message = {"action": "lobby_joined", "lobby_id": lobby_id}


async def start_server():
    async with websockets.serve(handle_connection, "localhost", 8080):
        print("WebSocket server running on ws://localhost:8080")
        await asyncio.Future()  # Keep server running


if __name__ == "__main__":
    asyncio.run(start_server())
