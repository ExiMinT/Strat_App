

import uuid
import sqlite3
import time

import asyncio
import websockets
import json

import threading


from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button

from kivy.clock import Clock

# SQLite Database Setup
DB_NAME = "strategies.db"

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS strategies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            map_name TEXT,
            side TEXT,
            strategy_name TEXT,
            description TEXT,
            timestamp INTEGER
        )
    """)
    conn.commit()
    conn.close()

setup_database()


# Main Screen
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=20, padding=50)

        title = Label(text="Welcome to the Strategy App", font_size=24)
        create_strategy_btn = Button(text="Create Strategy", size_hint=(1, 0.3))
        play_btn = Button(text="Play", size_hint=(1, 0.3))

        create_strategy_btn.bind(on_press=lambda x: setattr(self.manager, "current", "create_strategy_menu"))
        play_btn.bind(on_press=lambda x: setattr(self.manager, "current", "play_mode_screen"))

        layout.add_widget(title)
        layout.add_widget(create_strategy_btn)
        layout.add_widget(play_btn)

        self.add_widget(layout)


# Create Strategy Menu Screen
class CreateStrategyMenu(Screen):
    def __init__(self, **kwargs):
        super(CreateStrategyMenu, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=20, padding=50)

        title = Label(text="Create or Edit Strategy", font_size=24)
        create_strategy_btn = Button(text="Create Strategy", size_hint=(1, 0.3))
        edit_strategy_btn = Button(text="Edit Strategy", size_hint=(1, 0.3))
        back_btn = Button(text="Return to Menu", size_hint=(1, 0.2))

        create_strategy_btn.bind(on_press=lambda x: setattr(self.manager, "current", "create_edit_menu"))
        edit_strategy_btn.bind(on_press=lambda x: setattr(self.manager, "current", "edit_strategy"))
        back_btn.bind(on_press=lambda x: setattr(self.manager, "current", "main_screen"))

        layout.add_widget(title)
        layout.add_widget(create_strategy_btn)
        layout.add_widget(edit_strategy_btn)
        layout.add_widget(back_btn)

        self.add_widget(layout)




class CreateStrategyScreen(Screen):
    def __init__(self, **kwargs):
        super(CreateStrategyScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=15, padding=20)

        # Map Selection Dropdown
        self.map_spinner = Spinner(
            text="Select Map",
            values=["Train", "Ancient", "Anubis", "Dust 2", "Inferno", "Mirage", "Nuke"],
            size_hint=(1, 0.2)
        )

        # Side Selection Dropdown (T-Side / CT-Side)
        self.side_spinner = Spinner(
            text="Select Side",
            values=["T-Side", "CT-Side"],
            size_hint=(1, 0.2)
        )

        # Input Fields
        self.strategy_name_input = TextInput(hint_text="Enter Strategy Name", size_hint=(1, 0.2))
        self.description_input = TextInput(hint_text="Enter Strategy Description", size_hint=(1, 0.5), multiline=True)

        # Buttons
        save_btn = Button(text="Save Strategy", size_hint=(1, 0.2))
        back_btn = Button(text="Back", size_hint=(1, 0.2))

        save_btn.bind(on_press=self.save_strategy)
        back_btn.bind(on_press=lambda x: setattr(self.manager, "current", "create_strategy_menu"))

        # Add widgets to layout
        layout.add_widget(Label(text="Create New Strategy", font_size=24))
        layout.add_widget(self.map_spinner)
        layout.add_widget(self.side_spinner)
        layout.add_widget(self.strategy_name_input)
        layout.add_widget(self.description_input)
        layout.add_widget(save_btn)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def save_strategy(self, instance):
        """Save the strategy with the selected map and side to the database."""
        strategy_name = self.strategy_name_input.text
        description = self.description_input.text
        selected_map = self.map_spinner.text
        selected_side = self.side_spinner.text
        timestamp = int(time.time())

        # Ensure required fields are filled
        if strategy_name and description and selected_map != "Select Map" and selected_side != "Select Side":
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO strategies (map_name, side, strategy_name, description, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (selected_map, selected_side, strategy_name, description, timestamp))
            conn.commit()
            conn.close()

            # Reset input fields after saving
            self.strategy_name_input.text = ""
            self.description_input.text = ""
            self.map_spinner.text = "Select Map"
            self.side_spinner.text = "Select Side"

            # Return to the menu
            self.manager.current = "create_strategy_menu"





# Map Screen Template
class MapScreen(Screen):
    def __init__(self, map_name, mode, **kwargs):
        super().__init__(name=f"{mode}_{map_name.lower().replace(' ', '_')}_screen", **kwargs)
        layout = BoxLayout(orientation='vertical', spacing=15, padding=50)

        title = Label(text=f"{map_name} - {mode.capitalize()} Mode", font_size=24)
        t_side_btn = Button(text="T-Side", size_hint=(1, 0.3))
        ct_side_btn = Button(text="CT-Side", size_hint=(1, 0.3))
        back_btn = Button(text="Back", size_hint=(1, 0.2))

        if mode == "play":
            back_btn.bind(on_press=lambda x: setattr(self.manager, "current", "play_screen"))
        else:
            back_btn.bind(on_press=lambda x: setattr(self.manager, "current", "create_map_select"))

        layout.add_widget(title)
        layout.add_widget(t_side_btn)
        layout.add_widget(ct_side_btn)
        layout.add_widget(back_btn)

        self.add_widget(layout)

# Edit Strategy Screen
class EditStrategyScreen(Screen):
    def __init__(self, **kwargs):
        super(EditStrategyScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=15, padding=20)

        # Dropdowns for filtering
        self.map_spinner = Spinner(
            text="Select Map",
            values=["All Maps", "Train", "Ancient", "Anubis", "Dust 2", "Inferno", "Mirage", "Nuke"],
            size_hint=(1, 0.2)
        )
        self.side_spinner = Spinner(
            text="Select Side",
            values=["All Sides", "T-Side", "CT-Side"],
            size_hint=(1, 0.2)
        )

        # Button to apply filters
        filter_btn = Button(text="Apply Filters", size_hint=(1, 0.2))
        filter_btn.bind(on_press=self.load_strategies)

        # Strategy list display
        self.strategy_list = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.scroll_view.add_widget(self.strategy_list)

        # Back button
        self.back_btn = Button(text="Back", size_hint=(1, 0.2))
        self.back_btn.bind(on_press=self.go_back)

        # Add widgets to layout
        self.layout.add_widget(Label(text="Edit Strategies", font_size=24))
        self.layout.add_widget(self.map_spinner)
        self.layout.add_widget(self.side_spinner)
        self.layout.add_widget(filter_btn)
        self.layout.add_widget(self.scroll_view)
        self.layout.add_widget(self.back_btn)

        self.add_widget(self.layout)

    def on_pre_enter(self):
        """Refresh strategies list when screen is entered."""
        self.load_strategies()

    def load_strategies(self, instance=None):
        """Load strategies based on selected filters."""
        self.strategy_list.clear_widgets()

        # Get selected filters
        selected_map = self.map_spinner.text
        selected_side = self.side_spinner.text

        # Build SQL query dynamically
        query = "SELECT id, strategy_name, description FROM strategies WHERE 1=1"
        params = []

        if selected_map != "All Maps":
            query += " AND map_name=?"
            params.append(selected_map)

        if selected_side != "All Sides":
            query += " AND side=?"
            params.append(selected_side)

        query += " ORDER BY timestamp DESC"

        # Fetch filtered strategies
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, params)
        strategies = cursor.fetchall()
        conn.close()

        # Display strategies as buttons
        for strategy_id, name, description in strategies:
            btn = Button(text=name, size_hint_y=None, height=50)
            btn.bind(on_press=lambda instance, id=strategy_id: self.edit_strategy(id))
            self.strategy_list.add_widget(btn)

    def edit_strategy(self, strategy_id):
        """Navigate to strategy edit screen with selected strategy details."""
        self.manager.current = "create_edit_menu"
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT strategy_name, description FROM strategies WHERE id=?", (strategy_id,))
        strategy = cursor.fetchone()
        conn.close()

        if strategy:
            self.manager.get_screen("create_edit_menu").strategy_name_input.text = strategy[0]
            self.manager.get_screen("create_edit_menu").description_input.text = strategy[1]

    def go_back(self, instance):
        """Return to the create strategy menu."""
        self.manager.current = "create_strategy_menu"

class PlayModeScreen(Screen):
    def __init__(self, **kwargs):
        super(PlayModeScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=20, padding=50)

        title = Label(text="Select Your Role", font_size=24)
        igl_btn = Button(text="IGL", size_hint=(1, 0.3))
        players_btn = Button(text="Players", size_hint=(1, 0.3))
        back_btn = Button(text="Back", size_hint=(1, 0.2))

        igl_btn.bind(on_press=lambda x: setattr(self.manager, "current", "igl_screen"))
        players_btn.bind(on_press=lambda x: setattr(self.manager, "current", "players_screen"))
        back_btn.bind(on_press=lambda x: setattr(self.manager, "current", "main_screen"))

        layout.add_widget(title)
        layout.add_widget(igl_btn)
        layout.add_widget(players_btn)
        layout.add_widget(back_btn)

        self.add_widget(layout)


class IGLScreen(Screen):
    def __init__(self, **kwargs):
        super(IGLScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=20, padding=50)

        title = Label(text="Select a Map", font_size=24)

        # GridLayout for map buttons (2 columns to avoid stacking)
        self.map_list = GridLayout(cols=2, spacing=10, size_hint_y=None)
        self.map_list.bind(minimum_height=self.map_list.setter('height'))

        back_btn = Button(text="Back", size_hint=(1, 0.2))
        back_btn.bind(on_press=lambda x: setattr(self.manager, "current", "play_mode_screen"))

        layout.add_widget(title)
        layout.add_widget(self.map_list)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def on_pre_enter(self):
        """Load maps dynamically when entering the screen."""
        self.map_list.clear_widgets()
        maps = ["Train", "Ancient", "Anubis", "Dust 2", "Inferno", "Mirage", "Nuke"]

        for map_name in maps:
            btn = Button(text=map_name, size_hint=(1, None), height=80)
            btn.bind(on_press=lambda instance, m=map_name: self.go_to_strategy_list(m))
            self.map_list.add_widget(btn)

    def go_to_strategy_list(self, map_name):
        """Switch to strategy list screen and load strategies for the selected map."""
        self.manager.get_screen("strategy_list_screen").load_strategies(map_name)
        self.manager.current = "strategy_list_screen"


class StrategyListScreen(Screen):
    def __init__(self, **kwargs):
        super(StrategyListScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=15, padding=20)
        self.title = Label(text="Strategies", font_size=24)

        self.side_spinner = Spinner(
            text="Select Side",
            values=["All", "T-Side", "CT-Side"],
            size_hint=(1, 0.2)
        )
        self.side_spinner.bind(text=self.apply_side_filter)

        self.strategy_list = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.scroll_view.add_widget(self.strategy_list)

        self.back_btn = Button(text="Back", size_hint=(1, 0.2))
        self.back_btn.bind(on_press=lambda x: setattr(self.manager, "current", "igl_screen"))

        self.layout.add_widget(self.title)
        self.layout.add_widget(self.side_spinner)
        self.layout.add_widget(self.scroll_view)
        self.layout.add_widget(self.back_btn)

        self.add_widget(self.layout)

        self.selected_map = None
        self.lobby_id = "default_lobby"  # Change this if needed

    def load_strategies(self, map_name):
        """Load strategies for the selected map."""
        self.selected_map = map_name
        self.title.text = f"Strategies for {map_name}"
        self.apply_side_filter()

    def apply_side_filter(self, *args):
        """Filter strategies based on the selected side."""
        self.strategy_list.clear_widgets()
        selected_side = self.side_spinner.text

        query = "SELECT strategy_name FROM strategies WHERE map_name = ?"
        params = [self.selected_map]

        if selected_side != "All":
            query += " AND side = ?"
            params.append(selected_side)

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, params)
        strategies = cursor.fetchall()
        conn.close()

        if not strategies:
            self.strategy_list.add_widget(Label(text="No strategies found", size_hint_y=None, height=50))
        else:
            for (strategy_name,) in strategies:
                btn = Button(text=strategy_name, size_hint_y=None, height=50)
                btn.bind(on_press=lambda instance, s=strategy_name: self.select_strategy(s))
                self.strategy_list.add_widget(btn)

    def select_strategy(self, strategy_name):
        """Send the selected strategy to the WebSocket server."""
        asyncio.run(self.send_strategy(strategy_name))

    async def send_strategy(self, strategy_name):
        """Send strategy selection to WebSocket server."""
        async with websockets.connect("ws://35.197.214.65:8080") as websocket:
            message = {
                "action": "select_strategy",
                "lobby_id": self.lobby_id,
                "strategy": strategy_name
            }
            await websocket.send(json.dumps(message))


class PlayerScreen(Screen):
    def __init__(self, **kwargs):
        super(PlayerScreen, self).__init__(**kwargs)
        self.client_id = str(uuid.uuid4())  # Generate a unique client ID
        self.lobby_id = "default_lobby"
        self.layout = BoxLayout(orientation='vertical', spacing=15, padding=20)

        # Strategy display
        self.title = Label(text="Waiting for Strategy...", font_size=24)
        self.layout.add_widget(self.title)

        # Back Button
        self.back_btn = Button(text="Back", size_hint=(1, 0.2))
        self.back_btn.bind(on_press=lambda x: setattr(self.manager, "current", "main_screen"))
        self.layout.add_widget(self.back_btn)

        self.add_widget(self.layout)

        # Start the WebSocket client in an async event loop
        self.websocket_task = asyncio.ensure_future(self.websocket_client())

    def update_strategy(self, strategy):
        """Update the UI with the received strategy."""
        Clock.schedule_once(lambda dt: setattr(self.title, 'text', f"Current Strategy: {strategy}"))

    async def websocket_client(self):
        """WebSocket client to listen for strategy updates."""
        try:
            async with websockets.connect("ws://35.197.214.65:8080") as websocket:
                print("WebSocket connected")  # Debug log
                # Join the lobby with a unique client ID
                join_message = {
                    "action": "join_lobby",
                    "lobby_id": self.lobby_id,
                    "client_id": self.client_id
                }
                await websocket.send(json.dumps(join_message))
                print(f"Sent join message: {join_message}")  # Debug log

                while True:
                    try:
                        message = await websocket.recv()
                        print(f"Received message: {message}")  # Debug log

                        # Check if the message is empty
                        if not message:
                            print("Received empty message, skipping...")
                            continue

                        data = json.loads(message)

                        if data.get("action") == "update_strategy":
                            print(f"Updating strategy: {data['strategy']}")  # Debug log
                            self.update_strategy(data["strategy"])

                    except json.JSONDecodeError as e:
                        print(f"Error decoding message: {e}")
                        continue
        except Exception as e:
            print(f"Error connecting to WebSocket: {e}")

    def on_leave(self, *args):
        """Cancel the WebSocket task when leaving the screen."""
        if self.websocket_task:
            self.websocket_task.cancel()

    def update_strategy(self, strategy):
        """Update the UI with the received strategy."""
        # We use Clock.schedule_once to update the UI on the main thread
        Clock.schedule_once(lambda dt: setattr(self.title, 'text', f"Current Strategy: {strategy}"))

    async def websocket_client(self):
        """WebSocket client to listen for strategy updates."""
        try:
            async with websockets.connect("ws://35.197.214.65:8080") as websocket:
                # Join the lobby
                join_message = {
                    "action": "join_lobby",
                    "lobby_id": self.lobby_id
                }
                await websocket.send(json.dumps(join_message))

                while True:
                    try:
                        message = await websocket.recv()

                        # Check if the message is empty
                        if not message:
                            print("Received empty message, skipping...")
                            continue

                        data = json.loads(message)

                        if data.get("action") == "update_strategy":
                            self.update_strategy(data["strategy"])

                    except json.JSONDecodeError as e:
                        print(f"Error decoding message: {e}")
                        continue
        except Exception as e:
            print(f"Error connecting to WebSocket: {e}")

# App with Screen Manager
class StrategyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main_screen"))
        sm.add_widget(CreateStrategyMenu(name="create_strategy_menu"))
        sm.add_widget(CreateStrategyScreen(name="create_edit_menu"))
        sm.add_widget(EditStrategyScreen(name="edit_strategy"))
        sm.add_widget(PlayModeScreen(name="play_mode_screen"))
        sm.add_widget(IGLScreen(name="igl_screen"))
        sm.add_widget(StrategyListScreen(name="strategy_list_screen"))
        sm.add_widget(PlayerScreen(name="players_screen"))




        # Add screens for each map in both play and create modes
       # maps = ["Train", "Ancient", "Anubis", "Dust 2", "Inferno", "Mirage", "Nuke"]
       # for map_name in maps:
       #     sm.add_widget(MapScreen(map_name, mode="play"))
      #      sm.add_widget(MapScreen(map_name, mode="create"))

        return sm


# Run the App
if __name__ == '__main__':
    StrategyApp().run()