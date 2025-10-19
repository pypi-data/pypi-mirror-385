from robot.api.deco import keyword
import os
from DialogsPlus.utils.config import DialogConfig
from DialogsPlus.widgets.wrappers import ( GetValueFromUserDialog, 
                                          ExecuteManualStepDialog, 
                                          CountdownDialogRunner,
                                          GetConfirmationFromUser, 
                                          MultiValueInput,
                                          ChooseFromFileDialog,
                                          ChooseFolderDialog,
                                          ConfirmWithCheckbox,
                                          SelectOptionsWithCheckboxes)


ROBOT_LIBRARY_SCOPE = 'SUITE'

class DialogsPlus:

    def __init__(self, config=None):
    
        if config and os.path.exists(config):
            self.config = DialogConfig.from_yaml(config)
        else:
            self.config = DialogConfig()  # use defaults

    
    @keyword
    def get_value_from_user(self, prompt="Enter value:", default=""):
        return GetValueFromUserDialog.show(prompt,default,config=self.config)

    @keyword
    def run_manual_steps(self, steps):
        ExecuteManualStepDialog.run_steps(steps, config=self.config)

    @keyword
    def count_down(self, seconds):
        CountdownDialogRunner.show(int(seconds), config=self.config)
            
    @keyword
    def get_confirmation(self, message):
        return GetConfirmationFromUser.show(message=message,config=self.config)
    
    @keyword
    def get_multi_value(self, fields, default=None):
        fields_list = fields if isinstance(fields, list) else [fields]
        calculated_height = 150 + (len(fields_list) * 40) + 60
        #max_field_length = max(len(field) for field in fields_list)
        max_field_length = 20
        calculated_width = 300 + (max_field_length * 8)
        self.config.height = calculated_height
        self.config.width = calculated_width
        return MultiValueInput.run_multival(fields=fields,defaults=default,config=self.config)
    
    @keyword
    def choose_file(self, message="",  filetypes=None, multiple=False):
        return ChooseFromFileDialog.show( message, filetypes, multiple, self.config)

    @keyword
    def choose_folder(self, message):
        return ChooseFolderDialog.show(message, self.config)
    

    @keyword
    def confirm_with_checkbox(self, message, checkbox_text="I agree"):
        return ConfirmWithCheckbox.show(message, checkbox_text, self.config)
    

    @keyword
    def select_options_with_checkboxes(self, message, options, defaults=None):
        """Show multiple checkboxes and return selected options as dictionary."""
        
        options_list = options if isinstance(options, list) else options.split('|')
        
        # Base sizing
        num_options = len(options_list)
        max_option_length = max(len(opt) for opt in options_list)
        message_length = len(message)
        
        # Height: base + checkboxes + some buffer
        calculated_height = 180 + (num_options * 40)
        
        # Width: consider both message and longest option
        width_from_message = min(600, max(300, message_length * 7))
        width_from_options = max(300, 200 + (max_option_length * 8))
        calculated_width = max(width_from_message, width_from_options)
        
        self.config.height = calculated_height
        self.config.width = calculated_width
        
        return SelectOptionsWithCheckboxes.show(message, options, defaults, self.config)