# dialog_config.py

import yaml

class DialogConfig:
    def __init__(
        self,
        title="Robot Framework",
        width=400,
        height=150,
        theme="blue",
        appearance_mode="dark",

        button_width=120,
        button_height=32,
        label_font=("Courier New", 16, "bold"),
        entry_width= 200,
        entry_height=28,
        spacing=10,
        button_fg_color="#06bdb1",
        button_font=("Courier New", 16, "bold"),
        label_text_color="white",
        button_text_color="black",
        button_hover_color="#57b7b0",
        entry_font=("Courier New", 14),
        entry_text_color="white",
        entry_fg_color="#212121",
        entry_border_color="#46fff4",
        frame_fg_color = "transparent",
        progress_bar_width = 300,
        progress_bar_height = 12,
        progress_bar_color = "#00c0b5",

        
    ):
        self.title = title
        self.width = width
        self.height = height
        self.theme = theme
        self.appearance_mode = appearance_mode

        self.button_width = button_width
        self.button_height = button_height
        self.label_font = label_font
        self.entry_width = entry_width
        self.entry_height = entry_height
        self.spacing = spacing
        self.button_fg_color=button_fg_color
        self.button_font = button_font
        self.label_text_color = label_text_color
        self.button_text_color = button_text_color
        self.button_hover_color = button_hover_color
        self.entry_font = entry_font
        self.entry_text_color = entry_text_color
        self.entry_fg_color = entry_fg_color
        self.entry_border_color = entry_border_color
        self.frame_fg_color = frame_fg_color
        self.progress_bar_width = progress_bar_width
        self.progress_bar_height = progress_bar_height
        self.progress_bar_color = progress_bar_color


    @classmethod
    def from_yaml(cls, path: str):
        print(f"[DEBUG] Received config path: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return cls(
            title=data.get("title", "Dialog"),
            width=data.get("width", 300),
            height=data.get("height", 150),
            theme=data.get("theme", "blue"),
            appearance_mode=data.get("appearance_mode", "system"),

            button_width=data.get("button_width", 120),
            button_height=data.get("button_height", 32),
            label_font=tuple(data.get("label_font", ("Arial", 12))),
            entry_height=data.get("entry_height", 28),
            entry_width=data.get("entry_width",60),
            spacing=data.get("spacing", 10),
            button_fg_color=data.get("button_fg_color", "#06bdb1")
        )
