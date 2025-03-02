import pusher

# Initialize Pusher
pusher_client = pusher.Pusher(
    app_id="1951027",
    key="0f596af12f8e7ad77410",
    secret="0d7a72b3befa959fa480",
    cluster="eu",
    ssl=True
)

def handle_strategy_selection(data):
    """Broadcast the selected strategy to all clients in the lobby."""
    strategy_name = data["strategy"]
    lobby_id = data["lobby_id"]

    # Trigger an event on the lobby channel
    pusher_client.trigger(f"lobby-{lobby_id}", "update_strategy", {"strategy": strategy_name})

def handle_join_lobby(data):
    """Handle a client joining a lobby."""
    lobby_id = data["lobby_id"]
    print(f"Client joined lobby: {lobby_id}")

# Example usage (replace your WebSocket server logic with Pusher)
if __name__ == "__main__":
    # Simulate a strategy selection
    handle_strategy_selection({
        "action": "select_strategy",
        "strategy": "Rush B",
        "lobby_id": "default_lobby"
    })