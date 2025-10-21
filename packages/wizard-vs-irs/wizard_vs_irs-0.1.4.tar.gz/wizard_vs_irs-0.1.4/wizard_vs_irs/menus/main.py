import arcade, arcade.gui, asyncio, pypresence, time, copy, json, os

from wizard_vs_irs.utils.preload import button_texture, button_hovered_texture
from wizard_vs_irs.utils.constants import big_button_style, discord_presence_id
from wizard_vs_irs.utils.utils import FakePyPresence

class Main(arcade.gui.UIView):
    def __init__(self, pypresence_client=None):
        super().__init__()

        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout())
        self.box = self.anchor.add(arcade.gui.UIBoxLayout(space_between=10), anchor_x='center', anchor_y='center')

        self.pypresence_client = pypresence_client

        with open("settings.json", "r") as file:
            self.settings_dict = json.load(file)

        if self.settings_dict.get('discord_rpc', True):
            if self.pypresence_client == None: # Game has started
                try:
                    asyncio.get_event_loop()
                except:
                    asyncio.set_event_loop(asyncio.new_event_loop())
                try:
                    self.pypresence_client = pypresence.Presence(discord_presence_id)
                    self.pypresence_client.connect()
                    self.pypresence_client.start_time = time.time()
                except:
                    self.pypresence_client = FakePyPresence()
                    self.pypresence_client.start_time = time.time()

            elif isinstance(self.pypresence_client, FakePyPresence): # the user has enabled RPC in the settings in this session.
                # get start time from old object
                start_time = copy.deepcopy(self.pypresence_client.start_time)
                try:
                    self.pypresence_client = pypresence.Presence(discord_presence_id)
                    self.pypresence_client.connect()
                    self.pypresence_client.start_time = start_time
                except:
                    self.pypresence_client = FakePyPresence()
                    self.pypresence_client.start_time = start_time

            self.pypresence_client.update(state='In Menu', details='In Main Menu', start=self.pypresence_client.start_time)
        else: # game has started, but the user has disabled RPC in the settings.
            self.pypresence_client = FakePyPresence()
            self.pypresence_client.start_time = time.time()

        self.pypresence_client.update(state='In Menu', details='In Main Menu', start=self.pypresence_client.start_time)

        if os.path.exists("data.json"):
            with open("data.json", "r") as file:
                self.data = json.load(file)
        else:
            self.data = {}
        
        if not "high_score" in self.data:
            self.data["high_score"] = 0

        if not "evaded_tax" in self.data:
            self.data["evaded_tax"] = 0

        if not "shop" in self.data:
            self.data["shop"] = {}

        with open("data.json", "w") as file:
            file.write(json.dumps(self.data, indent=4))

    def on_show_view(self):
        super().on_show_view()

        self.title_label = self.box.add(arcade.gui.UILabel(text="Wizard vs IRS", font_name="Roboto", font_size=48))
        self.high_score_label = self.box.add(arcade.gui.UILabel(text=f"High Score: {self.data['high_score']}$", font_name="Roboto", font_size=24))
        self.evaded_tax_label = self.box.add(arcade.gui.UILabel(text=f"Total Evaded Tax: {self.data['evaded_tax']}$", font_name="Roboto", font_size=24))

        self.play_button = self.box.add(arcade.gui.UITextureButton(text="Play", texture=button_texture, texture_hovered=button_hovered_texture, width=self.window.width / 2, height=self.window.height / 10, style=big_button_style))
        self.play_button.on_click = lambda event: self.play()

        self.shop_button = self.box.add(arcade.gui.UITextureButton(text="Shop", texture=button_texture, texture_hovered=button_hovered_texture, width=self.window.width / 2, height=self.window.height / 10, style=big_button_style))
        self.shop_button.on_click = lambda event: self.shop()

        self.settings_button = self.box.add(arcade.gui.UITextureButton(text="Settings", texture=button_texture, texture_hovered=button_hovered_texture, width=self.window.width / 2, height=self.window.height / 10, style=big_button_style))
        self.settings_button.on_click = lambda event: self.settings()

    def play(self):
        from wizard_vs_irs.game.play import Game
        self.window.show_view(Game(self.pypresence_client))

    def shop(self):
        from wizard_vs_irs.menus.shop import Shop
        self.window.show_view(Shop(self.pypresence_client))

    def settings(self):
        from wizard_vs_irs.menus.settings import Settings
        self.window.show_view(Settings(self.pypresence_client))
