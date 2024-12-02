# Integrate concat into this.

import sys
import os

os.environ["QT_QPA_PLATFORM"] = "wayland"

# PyQT5 imports for the UI
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal

import queue

# Adding the root directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 

# Importing the required model functions and utilities
from Model_json.model_json import GPT_response
from json_parsing.categoriser import categorise
from sequencer.sequencer import process_json

# Importing the models
from generation_models.model_1 import generate_command_1, execute_1
from generation_models.model_2 import generate_command_2, execute_2
from generation_models.model_3 import generate_command_3, execute_3
from generation_models.model_4 import generate_command_4, execute_4
from generation_models.model_5 import generate_command_5, execute_5
from generation_models.model_6 import generate_command_6, execute_6
from generation_models.model_7 import generate_command_7, execute_7

class Worker(QThread):
    '''
    QThread for running the processing logic in a seperate thread so that we can display "generating response..." while the processing is being done

    Creating a different class works the best!
    '''
    result_ready = pyqtSignal(list)  # Here we emit results when processing is done

    def __init__(self, prompt, parent=None):
        super().__init__(parent)
        self.prompt = prompt

    def run(self):
        """
        Run the GPT model and process the operations in a background thread.
        """
        try:
            # Run the GPT model
            processed_output = GPT_response(self.prompt)

            # print(f"processed_output = {processed_output}")
            categorised_output = categorise(processed_output)
            operations_q = process_json(f"{categorised_output}")
            results = self.execute_queue(operations_q)
        except Exception as e:
            results = [f"Error: {str(e)}"]
        
        self.result_ready.emit(results)

    def execute_queue(self, operations_q):
        """
        Process the queue of operations one by one.
        """
        results = []
        model_dispatch = {
            "model_1": ("generation_models.model_1", "generate_command_1", "execute_1"),
            "model_2": ("generation_models.model_2", "generate_command_2", "execute_2"),
            "model_3": ("generation_models.model_3", "generate_command_3", "execute_3"),
            "model_4": ("generation_models.model_4", "generate_command_4", "execute_4"),
            "model_5": ("generation_models.model_5", "generate_command_5", "execute_5"),
            "model_6": ("generation_models.model_6", "generate_command_6", "execute_6"),
            "model_7": ("generation_models.model_7", "generate_command_7", "execute_7")
        }

        additional_data = ''

        while not operations_q.empty():
            operation = operations_q.get()
            print(operation)

            operation_type = operation.get('operation_type')
            model_name = operation.get('model_name')
            parameters = operation.get('parameters')

            if model_name in model_dispatch:
                module_path, generate_func, execute_func = model_dispatch[model_name]
                try:
                    model_module = __import__(module_path, fromlist=[generate_func, execute_func])
                    generate_command = getattr(model_module, generate_func)
                    execute_command = getattr(model_module, execute_func)

                    command = generate_command(
                        operation=operation_type, parameters=parameters, additional_data=additional_data
                    )
                    print(command)

                    if command.strip().startswith("cd "):
                        target_dir = command.split(" ", 1)[1]
                        target_dir = os.path.expanduser(target_dir)
                        os.chdir(target_dir)
                        output = f"Changed directory to {os.getcwd()}"
                    else:
                        output = execute_command(command)

                    results.append(output)
                    additional_data = output
                except Exception as e:
                    results.append(f"Error: {str(e)}")
            else:
                results.append(f"Error: Unknown model '{model_name}'.")
        return results


class ModernTerminal(QWidget):
    '''
    The terminal class, has the following important functions

    1. init_ui --> Define the UI here, the colors, size and everything goes here
    2. append_prompt --> This is defining the prompt bar, which tells the username, current directory and host
    3. start_processing --> Here we show the user the "generating response..." message, NEED to fix the delay's here!
    4. model_json --> Here we are calling the json creation and upgrading models. MAKE IT A BETTER NAME!
    5. execute --> Call the relevant models and execute in the sequence defined by the queue.
    6. display_response --> Here we display whatever we need too. UPDATE THIS AS WELL WITH concat.
    '''

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.command_history = []                   # This is so that we can press the 'up' key and get the previous prompt
        self.history_index = -1
        self.is_processing = False
        self.current_prompt = ""                       # Store the current prompt text for reuse

    def init_ui(self):
        ''' Terminal setup. For changing the color scheme and more, refer here.
        '''

        self.setWindowTitle("Terminal")
        self.setGeometry(100, 100, 800, 500)

        # Setting up the main layout, setContentsMargins() defines the size of the terminal as soon as launch the program
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Terminal display area
        self.terminal_display = QTextEdit()
        self.terminal_display.setReadOnly(True)
        self.terminal_display.setStyleSheet("""
            QTextEdit {
                background-color: #999999;
                color: #000000;
                border: none;
                padding: 0px;
            }
        """)
        self.terminal_display.setFont(QFont("Monospace", 11))

        # Modifying the input field, this is the space where we enter our prompts.
        self.input_field = QLineEdit()
        self.input_field.setFont(QFont("Monospace", 11))
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: 1px solid black;    /* Black border */
                border-radius: 3px;         /* Rounded corners */
                padding: 0px;               /* Inner padding */
                background-color: #999999;  /* Background color of the input field same as the general background */
                color: black;               /* Text color */
            }
        """)
        self.input_field.returnPressed.connect(self.start_processing)

        self.main_layout.addWidget(self.terminal_display, stretch=1)

        self.main_layout.addWidget(self.input_field, stretch=0)
        self.setLayout(self.main_layout)
        self.append_prompt()

    def append_prompt(self):
        user = os.getenv("USER", 'user')
        host = os.uname().nodename
        current_dir = os.getcwd()
        home = os.path.expanduser("~")
        if current_dir.startswith(home):
            current_dir = "~" + current_dir[len(home):]

        prompt_text = (
            f'<span style="color: #000000;">{user}</span>'
            f'<span style="color: #000000;">@UB</span>:'
            f'<span style="color: #000000;">{current_dir}</span>'
            f' <span style="color: #FFFFFF;">$</span> '
        )

        self.terminal_display.append(prompt_text)
        self.terminal_display.moveCursor(QTextCursor.End)

    def start_processing(self):
        if self.is_processing:
            return

        self.is_processing = True
        self.current_prompt = self.input_field.text()

        if self.current_prompt.strip():
            self.terminal_display.insertPlainText(self.current_prompt + "\n")
            self.terminal_display.append(
                '<span style="color: #FFB86C;">Generating response...</span>'
            )
            self.terminal_display.moveCursor(QTextCursor.End)
            QApplication.processEvents()

            self.worker = Worker(self.current_prompt)
            self.worker.result_ready.connect(self.display_response)
            self.worker.start()

        self.input_field.clear()

    def display_response(self, results):
        cursor = self.terminal_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.select(QTextCursor.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()

        formatted_output = "\n".join([f"<span style='color: #007ACC;'>Response:</span> {result} \n" for result in results])
        self.terminal_display.append(f"<pre>{formatted_output}</pre>")
        self.append_prompt()
        self.is_processing = False


app = QApplication(sys.argv)
terminal = ModernTerminal()
terminal.show()
sys.exit(app.exec_())
