from DialogsPlus.widgets.styling import ( 
    InputDialog, 
    ManualStepDialog, 
    CountdownDialog, 
    ConfirmationDialog, 
    MultiValueInputDialog,
    FileDialog,
    FolderDialog,
    CheckboxConfirmationDialog,
    MultiCheckboxDialog,
    PauseDialog)

from robot.api import logger
from robot.errors import ExecutionFailed


class GetValueFromUserDialog:
    @staticmethod
    def show(prompt="Enter value:", default="", config=None):
        dialog = InputDialog(prompt, default, config)
        return dialog.show().get('value')
    

class ExecuteManualStepDialog:
    @staticmethod
    def show(message="Please perform the step and confirm.", config=None):
        logger.info(message)
        
        dialog = ManualStepDialog(message, config)
        result = dialog.show()

        if result.get("status") == "pass":
            return
        else:
            failure_dialog = InputDialog("Test Failed - Reason:", "", config, is_error=True)
            reason = failure_dialog.show().get('value', 'No reason provided')
            logger.error(f"{message} | Reason: {reason}")
            raise ExecutionFailed(reason)

    @staticmethod
    def run_steps(steps, config=None):
        if isinstance(steps, str):
            ExecuteManualStepDialog.show(steps, config)
        elif isinstance(steps, list):
            for step in steps:
                ExecuteManualStepDialog.show(step, config)
        else:
            raise ExecutionFailed("Invalid input: must be a string or a list of strings.")
        

class CountdownDialogRunner:
    @staticmethod
    def show(seconds=10, message="Please wait...", config=None):
        logger.info(f"Starting countdown for {seconds} seconds...")
        dialog = CountdownDialog(seconds, message, config)
        dialog.show()


class GetConfirmationFromUser:
    @staticmethod
    def show(message="Are you sure?", default="Yes", config=None):
        logger.info(message)
        dialog = ConfirmationDialog(message, default, config)
        dialog.config.width = 450
        result = dialog.show().get("status")
        
        if result == "yes":
            return True
        elif result == "no":
            return False
        else:  # cancel
            return None
        

class MultiValueInput:
    @staticmethod
    def show(fields, defaults=None, config=None):
        logger.info(f"Showing input dialog for: {fields}")
        dialog = MultiValueInputDialog(fields, defaults=defaults, config=config)
        result = dialog.show()
        if result.get("status") == "pass":
            return result
        else:
            return None

    @staticmethod
    def run_multival(fields, config=None, defaults=None):
        return MultiValueInput.show(fields, defaults=defaults, config=config)

class ChooseFromFileDialog:
    @staticmethod
    def show(message="", filetypes=None, multiple=False, config=None):
        logger.info(f"Opening file picker: {message}")
        dialog = FileDialog(message, filetypes, multiple, config)
        result = dialog.show()
        return result.get('files' if multiple else 'file')


class ChooseFolderDialog:
    @staticmethod
    def show(message, config=None):
        logger.info(f"Opening folder picker: {message}")
        dialog = FolderDialog(message, config)
        return dialog.show().get('folder')
    

class ConfirmWithCheckbox:
    @staticmethod
    def show(message, checkbox_text="I agree", config=None):
        logger.info(f"Showing checkbox confirmation: {message}")
        dialog = CheckboxConfirmationDialog(message, checkbox_text, config)
        result = dialog.show()
        return result.get('confirmed', False)
    

class SelectOptionsWithCheckboxes:
    @staticmethod
    def show(message, options, defaults=None, config=None):
        logger.info(f"Showing multi-checkbox dialog: {message}")
        dialog = MultiCheckboxDialog(message, options, defaults, config)
        return dialog.show()
    


class PauseExecution:
    @staticmethod
    def show(message="Test execution paused", config=None):
        logger.info(f"Test paused: {message}")
        dialog = PauseDialog(message, config)
        dialog.show()