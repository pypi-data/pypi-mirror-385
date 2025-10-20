import customtkinter as ctk
from customtkinter import BooleanVar, IntVar
from DialogsPlus.utils.config import DialogConfig
from tkinter import filedialog
import os


# Export for use in other modules
__all__ = [
    'BaseDialogRunner',
    'BaseDialog',
    'ctk',
    'BooleanVar',
    'filedialog',
    'IntVar'
]

class BaseDialogRunner:
    _theme_initialized = False
    
    @staticmethod
    def _center_window(app, config):
        app.update_idletasks()
        
        screen_width = app.winfo_screenwidth()
        screen_height = app.winfo_screenheight()
        
        x = (screen_width - config.width) // 2
        y = (screen_height - config.height) // 2       
        app.geometry(f"{config.width}x{config.height}+{x}+{y}")
    
    @staticmethod
    def create_app(config: DialogConfig):
        # Initialize theme once on first dialog creation
        if not BaseDialogRunner._theme_initialized:
            ctk.set_appearance_mode(config.appearance_mode)
            ctk.set_default_color_theme(config.theme)
            BaseDialogRunner._theme_initialized = True
        
        app = ctk.CTk()
        app.title(config.title)
        app.lift()  # Bring to front
        app.attributes('-topmost', True)  # Force on top
        app.after(100, lambda: app.attributes('-topmost', False)) 

        icon_path = os.path.join(os.path.dirname(__file__), "assets", "robot.ico")
        try:
            app.iconbitmap(icon_path)
        except (FileNotFoundError, Exception):
            pass

        BaseDialogRunner._center_window(app, config)
        return app

    @staticmethod
    def run_dialog(ui_builder_func, config: DialogConfig):
        app = BaseDialogRunner.create_app(config)
        ui_builder_func(app)
        app.mainloop()
        
        app.withdraw()
        
        try:
            after_ids = app.tk.call('after', 'info')
            for after_id in after_ids:
                try:
                    app.after_cancel(after_id)
                except:
                    pass
        except:
            pass
        
        app.update_idletasks()
        
        try:
            app.quit()
        except:
            pass
        
        try:
            app.destroy()
        except:
            pass


class BaseDialog:
    
    def __init__(self, config=None):
        self.config = config if config else DialogConfig()
        self.result = {}
    
    def create_button(self, parent, text, command, **kwargs):
        """Create a button with config styling"""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            font=self.config.button_font,
            fg_color=self.config.button_fg_color,
            text_color=self.config.button_text_color,
            hover_color=self.config.button_hover_color,
            width=kwargs.get('width', self.config.button_width),
            height=kwargs.get('height', self.config.button_height),
            **{k: v for k, v in kwargs.items() if k not in ['width', 'height']}
        )

    def create_label(self, parent, text, **kwargs):
        """Create a label with config styling"""
        return ctk.CTkLabel(
            parent,
            text=text,
            font=self.config.label_font,
            text_color=self.config.label_text_color,
            anchor=kwargs.get('anchor', "center"),
            justify=kwargs.get('justify', "left"),
            wraplength=kwargs.get('wraplength', 0),
            **{k: v for k, v in kwargs.items() if k not in ['anchor', 'justify', 'wraplength']}
        )
    
    def create_entry(self, parent, **kwargs):
        """Create an entry with consistent styling from config"""
        return ctk.CTkEntry(
            parent,
            width=kwargs.get('width', self.config.entry_width),
            height=kwargs.get('height', self.config.entry_height),
            font=kwargs.get('font', self.config.entry_font),
            text_color=kwargs.get('text_color', self.config.entry_text_color),
            fg_color=kwargs.get('fg_color', self.config.entry_fg_color),
            border_color=kwargs.get('border_color', self.config.entry_border_color),
            **{k: v for k, v in kwargs.items() if k not in ['width', 'height', 'font', 'text_color', 'fg_color', 'border_color']}
        )
    
    def create_frame(self, parent, **kwargs):
        return ctk.CTkFrame(
            parent,
            fg_color=kwargs.get('fg_color', self.config.frame_fg_color),
            **{k: v for k, v in kwargs.items() if k not in ['fg_color']}  # ← Add this
        )
        
    def create_progress_bar(self, parent, **kwargs):
        return ctk.CTkProgressBar(
            parent,
            width=kwargs.get('width', self.config.progress_bar_width),
            height=kwargs.get('height', self.config.progress_bar_height),
            progress_color=kwargs.get('progress_color', self.config.progress_bar_color),
            **{k: v for k, v in kwargs.items() if k not in ['width', 'height', 'progress_color']}
        )
    
    def create_checkbox(self, parent, text="", **kwargs):
        """Create a checkbox with consistent styling from config"""
        return ctk.CTkCheckBox(
            parent,
            text=text,
            font=kwargs.get('font', self.config.label_font),
            text_color=kwargs.get('text_color', self.config.label_text_color),
            fg_color=kwargs.get('fg_color', self.config.button_fg_color),
            hover_color=kwargs.get('hover_color', self.config.button_hover_color),
            **{k: v for k, v in kwargs.items() if k not in ['font', 'text_color', 'fg_color', 'hover_color']}
        )


# testing this shit
    
    def show(self):
        def ui(app):
            self.build_ui(app)
        
        BaseDialogRunner.run_dialog(ui, self.config)
        return self.result
    
    def build_ui(self, app):
        raise NotImplementedError