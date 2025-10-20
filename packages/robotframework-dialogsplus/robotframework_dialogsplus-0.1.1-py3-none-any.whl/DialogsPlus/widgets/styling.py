from DialogsPlus.widgets.base import BaseDialog, filedialog, BooleanVar, IntVar
import time



class InputDialog(BaseDialog):
    
    def __init__(self, prompt, default="", config=None, is_error=False):
        super().__init__(config)
        self.prompt = prompt
        self.default = default
        self.is_error = is_error
    
    def build_ui(self, app):
        frame = self.create_frame(app)
        frame.pack(pady=8)

        label = self.create_label(frame, text=self.prompt)
        label.pack() 

        entry_frame = self.create_frame(app)
        entry_frame.pack(pady=8)
        entry = self.create_entry(entry_frame)
        entry.insert(0, self.default)
        entry.pack()
        
        def on_submit():
            self.result['value'] = entry.get()
            app.quit()
        
        app.protocol("WM_DELETE_WINDOW", app.quit)
        app.bind('<Return>', lambda e: on_submit())
        app.bind('<Escape>', lambda e: app.quit())
        
        entry.focus_set()
        
        button_frame = self.create_frame(app)
        button_frame.pack(pady=10)
        self.create_button(button_frame, text="Submit", command=on_submit).pack()


class ManualStepDialog(BaseDialog):
    
    def __init__(self, message, config=None):
        super().__init__(config)
        self.message = message
    
    def build_ui(self, app):
        def on_pass():
            self.result["status"] = "pass"
            app.quit()

        def on_fail():
            self.result["status"] = "fail"
            app.quit()

        app.protocol("WM_DELETE_WINDOW", app.quit)
        app.bind('<Escape>', lambda e: app.quit())

        self.create_label(app, text=self.message).pack(pady=25)

        button_frame = self.create_frame(app)
        button_frame.pack(pady=(10, self.config.spacing), expand=True)

        self.create_button(
            button_frame,
            text="PASS",
            command=on_pass).pack(side="left", padx=10)

        self.create_button(
            button_frame,
            text="FAIL",
            command=on_fail).pack(side="left", padx=10)


class CountdownDialog(BaseDialog):
    
    def __init__(self, seconds, message="Please wait...", config=None):
        super().__init__(config)
        self.seconds = seconds
        self.message = message
    
    def build_ui(self, app):
        
        label = self.create_label(app, text="")
        label.place(relx=0.5, rely=0.4, anchor="center")

        progress = self.create_progress_bar(app)
        progress.place(relx=0.5, rely=0.8, anchor="center")
        progress.set(0)

        start_time = time.perf_counter()

        def update():
            elapsed = time.perf_counter() - start_time
            remaining = self.seconds - elapsed

            if remaining > 0:
                mins, secs = divmod(int(remaining), 60)
                label.configure(text=f"{self.message}\n{mins:02}:{secs:02}")
                progress.set(min(elapsed / self.seconds, 1))
                app.after(100, update)
            else:
                progress.set(1)
                label.configure(text=f"{self.message}\n00:00")
                app.quit()

        update()


class ConfirmationDialog(BaseDialog):
    def __init__(self, message, default="Yes", config=None):
        super().__init__(config)
        self.message = message
        self.default = default
    
    def build_ui(self, app):

        def on_yes():
            self.result["status"] = "yes"
            app.quit()

        def on_no():
            self.result["status"] = "no"
            app.quit()

        def on_cancel():
            self.result["status"] = "cancel"
            app.quit()

        app.protocol("WM_DELETE_WINDOW", app.quit)
        app.bind('<Escape>', lambda e: app.quit())

        self.create_label(app, text=self.message).pack(pady=25)

        button_frame = self.create_frame(app)
        button_frame.pack(pady=(10, self.config.spacing), expand=True)

        self.create_button(
            button_frame,
            text="Yes",
            command=on_yes).pack(side="left", padx=5)

        self.create_button(
            button_frame,
            text="No",
            command=on_no).pack(side="left", padx=5)

        self.create_button(
            button_frame,
            text="Cancel",
            command=on_cancel).pack(side="left", padx=5)
        
        


class MultiValueInputDialog(BaseDialog):
    def __init__(self, fields, defaults=None, config=None):
        super().__init__(config)

        # Normalize string input to list
        self.fields = fields if isinstance(fields, list) else [fields]
        self.defaults = defaults or {}
        self.entries = {}

    def build_ui(self, app):
        def on_submit():
            self.result = {field: self.entries[field].get() for field in self.fields}
            self.result["status"] = "pass"
            app.quit()

        def on_cancel():
            self.result["status"] = "fail"
            app.quit()

        app.protocol("WM_DELETE_WINDOW", on_cancel)
        app.bind('<Escape>', lambda e: on_cancel())
        app.bind('<Return>', lambda e: on_submit())

        main_frame = self.create_frame(app)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        title = self.create_label(main_frame, text="Enter values")
        title.pack(pady=25)

        fields_frame = self.create_frame(main_frame)
        fields_frame.pack(fill="both", expand=True)

        for field in self.fields:
            row_frame = self.create_frame(fields_frame)
            row_frame.pack(fill="x", pady=5)

            label = self.create_label(row_frame, text=field)
            label.pack(side="left", padx=(0, 10))

            entry = self.create_entry(row_frame)
            entry.insert(0, self.defaults.get(field, ""))
            entry.pack(side="left", fill="x", expand=True)

            self.entries[field] = entry

        # Buttons
        button_frame = self.create_frame(app)
        button_frame.place(relx=0.5, rely=0.8, anchor="center")

        submit_btn = self.create_button(button_frame, text="Submit", command=on_submit)
        submit_btn.pack(side="left", padx=5)

        cancel_btn = self.create_button(button_frame, text="Cancel", command=on_cancel)
        cancel_btn.pack(side="left", padx=5)





class FileDialog(BaseDialog):
    def __init__(self, message="", filetypes=None, multiple=False, config=None):
        super().__init__(config)
        self.title = self.config.title
        self.message = message
        self.filetypes = filetypes or [("All files", "*.*")]
        self.multiple = multiple
    
    def build_ui(self, app):
        # app.withdraw()  # Hide the main window
        
        def on_browse():
            if self.multiple:
                files = filedialog.askopenfilenames(title=self.title, filetypes=self.filetypes)
                self.result['files'] = list(files) if files else None
                
            else:
                file = filedialog.askopenfilename(title=self.title, filetypes=self.filetypes)
                self.result['file'] = file if file else None
        
            app.quit()

        app.protocol("WM_DELETE_WINDOW", app.quit)
        app.bind('<Escape>', lambda e: app.quit())

        self.create_label(app, text=self.message).pack(pady=25)

        button_frame = self.create_frame(app)
        button_frame.pack(pady=(10, self.config.spacing), expand=True)


        self.create_button(
            button_frame,
            text="Browse",
            command=on_browse).pack(side="bottom", padx=10)


class FolderDialog(BaseDialog):
    def __init__(self, message, config=None):
        super().__init__(config)
        self.title = self.config.title
        self.message = message
    
    def build_ui(self, app):
        #app.withdraw()  # Hide the main window
        
        def on_browser_folder():
            folder = filedialog.askdirectory(title=self.title)
            self.result['folder'] = folder if folder else None
            app.quit()
        
        app.protocol("WM_DELETE_WINDOW", app.quit)
        app.bind('<Escape>', lambda e: app.quit())

        self.create_label(app, text=self.message).pack(pady=25)

        button_frame = self.create_frame(app)
        button_frame.pack(pady=(10, self.config.spacing), expand=True)


        self.create_button(
            button_frame,
            text="Browse",
            command=on_browser_folder).pack(side="bottom", padx=10)
        

class CheckboxConfirmationDialog(BaseDialog):
    def __init__(self, message, checkbox_text="I agree", config=None):
        super().__init__(config)
        self.message = message
        self.checkbox_text = checkbox_text
    
    def build_ui(self, app):
        checkbox_var = BooleanVar(value=False)
        
        def on_submit():
            self.result['confirmed'] = checkbox_var.get()
            app.quit()
        
        app.protocol("WM_DELETE_WINDOW", app.quit)
        app.bind('<Escape>', lambda e: app.quit())
        app.bind('<Return>', lambda e: on_submit())
        
        self.create_label(app, text=self.message).pack(pady=10)
        
        self.create_checkbox(app, text=self.checkbox_text, variable=checkbox_var).pack(pady=10)
        
        self.create_button(app, text="Submit", command=on_submit).pack(pady=10)


class MultiCheckboxDialog(BaseDialog):
    def __init__(self, message, options, defaults=None, config=None):
        super().__init__(config)
        self.message = message
        self.options = options if isinstance(options, list) else options.split('|')
        self.defaults = defaults or []
        self.checkbox_vars = {}
    
    def build_ui(self, app):
        def on_submit():
            self.result = {option: var.get() for option, var in self.checkbox_vars.items()}
            app.quit()
        
        app.protocol("WM_DELETE_WINDOW", app.quit)
        app.bind('<Escape>', lambda e: app.quit())
        app.bind('<Return>', lambda e: on_submit())
        
        self.create_label(app, text=self.message).pack(pady=20)
        
        # Checkboxes frame
        checkbox_frame = self.create_frame(app)
        checkbox_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        for option in self.options:
            var = BooleanVar(value=(option in self.defaults))
            self.checkbox_vars[option] = var
            
            self.create_checkbox(checkbox_frame, text=option, variable=var).pack(
                anchor="w", pady=5, padx=10
            )
        
        self.create_button(app, text="Submit", command=on_submit).pack(pady=20)



class PauseDialog(BaseDialog):
    def __init__(self, message="Test execution paused", config=None):
        super().__init__(config)
        self.message = message
    
    def build_ui(self, app):
        def on_continue():
            app.quit()
        
        app.protocol("WM_DELETE_WINDOW", on_continue)
        app.bind('<Return>', lambda e: on_continue())
        app.bind('<Escape>', lambda e: on_continue())
        
        self.create_label(app, text=self.message).pack(pady=20)
        self.create_button(app, text="Continue", command=on_continue).pack(pady=20)