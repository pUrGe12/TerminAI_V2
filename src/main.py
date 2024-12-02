# Integrate concat into this.

import sys
import os

# PyQT5 imports for the UI
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtCore import Qt, QTimer

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
        self.current_prompt = ""                    # Store the current prompt text for reuse

    def init_ui(self):
        '''
        Terminal setup. For changing the color scheme and more, refer here.
        '''
        self.setWindowTitle("Terminal")
        self.setGeometry(100, 100, 800, 500)

        # Set up the main layout
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

        # Modifying the input field
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

        # Add widgets to main layout
        self.main_layout.addWidget(self.terminal_display, stretch = 1)              # Stretch just means expand this thing till 0 padding.
        self.main_layout.setSpacing(0)                                              # Remove whitespace between the others and input field.
        self.main_layout.addWidget(self.input_field, stretch = 0)

        # Set main layout
        self.setLayout(self.main_layout)

        # Setting up the prompt bar
        self.append_prompt()

    def append_prompt(self):
        '''
        This is the prompt bar. 
        '''
        user = os.getenv("USER", 'user')
        host = os.uname().nodename
        current_dir = os.getcwd()

        home = os.path.expanduser("~")
        
        if current_dir.startswith(home):
            current_dir = "~" + current_dir[len(home):]

        prompt_color_user = "56B6C2"
        prompt_color_host = "E06C75"
        prompt_color_path = "#000000"
        prompt_symbol_color = "#FFFFFF"

        # arrow_color = "#98C379"  # Green color for the arrow
        # path_color = "#56B6C2"   # Blue color for the current directory path
        # symbol_color = "#C678DD"  # Purple color for the "$" symbol

        prompt_text = (
            f'<span style="color: {prompt_color_user};">{user}</span>'
            f'<span style="color: {prompt_color_host};">@{host}</span>:'
            f'<span style="color: {prompt_color_path};">{current_dir}</span>'
            f' <span style="color: {prompt_symbol_color};">$</span> '
        )

        self.terminal_display.append(prompt_text)
        self.terminal_display.moveCursor(QTextCursor.End)

    def start_processing(self):
        '''
        We're pushing the UI updates first before calling the heavy computation tasks to give some semblance to the users.

        This function essentially does 2 things,
            - Displays the user's prompt and the output
            - Processes the prompt through the following steps
                a. Creating the main Json object
                b. Categorise the operations in one of the 6 areas of interest.

        '''

        if self.is_processing:
            return

        self.is_processing = True
        self.current_prompt = self.input_field.text()

        if self.current_prompt.strip():
            self.terminal_display.insertPlainText(self.current_prompt + "\n")
            self.terminal_display.moveCursor(QTextCursor.End)  # Ensure cursor stays at the bottom

            QApplication.processEvents()  # Force immediate update of the UI

            self.command_history.append(self.current_prompt)
            self.history_index = len(self.command_history)

            self.terminal_display.append(
                '<span style="color: #FFB86C;">Generating response...</span>'
            )
            self.terminal_display.moveCursor(QTextCursor.End)

            self.model_json(self.current_prompt)  # Call the processing logic

        self.input_field.clear()

    def model_json(self, prompt):
        """
        Run the GPT model and process the response with categorise. This is the actual processing logic on the prompt.
        """
        user_prompt = self.current_prompt
        try:
            # Run the GPT model
            processed_output = GPT_response(user_prompt)
            print(processed_output)
            # Run the categoriser on the output
            categorised_output = categorise(processed_output)
            print(categorised_output)
            
            # Converting the JSON output to a queue of operations using the sequencer
            operations_q = process_json(f"{categorised_output}")

            # Process the queue
            final_results = self.execute_queue(operations_q)

            self.response_output = final_results  # Store the final output
        except Exception as e:
            self.response_output = f"Error: {str(e)}"  # Handling errors, we need to make this better before production

        # Simulate delay before displaying response
        QTimer.singleShot(5000, self.display_response)

    def execute_queue(self, operations_q):
        """
        Process the queue of operations one by one.
        For each operation:
          - Access the `model_name` and `parameters`.
          - Dynamically call the appropriate model function.
        """

        results = [] 

        # Dispatch dictionary mapping model names to their corresponding generate and execute methods
        model_dispatch = {
            "model_1": ("generation_models.model_1", "generate_command_1", "execute_1"),
            "model_2": ("generation_models.model_2", "generate_command_2", "execute_2"),
            "model_3": ("generation_models.model_3", "generate_command_3", "execute_3"),
            "model_4": ("generation_models.model_4", "generate_command_4", "execute_4"),
            "model_5": ("generation_models.model_5", "generate_command_5", "execute_5"),
            "model_6": ("generation_models.model_6", "generate_command_6", "execute_6"),
        }

        additional_data = ''

        while not operations_q.empty():
            operation = operations_q.get()
            operation_type = operation.get('operation_type')
            model_name = operation.get('model_name')
            parameters = operation.get('parameters')

            print(f"Processing operation: {operation}")

            if model_name in model_dispatch:
                module_path, generate_func, execute_func = model_dispatch[model_name]
                try:
                    # Dynamically import and execute
                    model_module = __import__(module_path, fromlist=[generate_func, execute_func])
                    generate_command = getattr(model_module, generate_func)
                    execute_command = getattr(model_module, execute_func)

                    # Generating the command, function has been imported
                    command = generate_command(
                        operation=operation_type, parameters=parameters, additional_data=additional_data
                    )
                    
                    '''
                    We will have to process commands like "cd" dynamically and not through the model, because if we run that through a subprocess then 
                    it doesn't really change the directory at all.
                    '''
                    if command.strip().startswith("cd "):
                        try:
                            target_dir = command.split(" ", 1)[1]
                            target_dir = os.path.expanduser(target_dir)         # Get the complete directory
                            os.chdir(target_dir)                                # Change the working directory
                            self.append_prompt()                                # Update the prompt to reflect the new directory
                            output = f"Changed directory to {os.getcwd()}"
                        except IndexError:
                            output = "Error: No directory specified."
                        except FileNotFoundError:
                            output = f"Error: Directory not found: {target_dir}"
                        except Exception as e:
                            output = f"Error: {str(e)}"
                    else:
                        # Execute non-cd commands normally
                        output = execute_command(command)

                    print(output)

                    results.append(output)          # Appending the result
                    additional_data = output        # This is so we can pass that in the next model if sequential execution
                except Exception as e:
                    results.append(f"Error processing model {model_name}: {e}")
            else:
                results.append(f"Error: Unknown model '{model_name}'.")

        return results


    def display_response(self):
        """
        Display the processed output from the model.
        """
        # Remove the "Generating response..." placeholder
        cursor = self.terminal_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.select(QTextCursor.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()

        # Display the actual processed response
        if isinstance(self.response_output, list):                        # pretty-print results if it's a list
            formatted_output = "\n".join([f"Response: {str(result)}" for result in self.response_output])
            self.terminal_display.append(f"<pre>{formatted_output}</pre>")
        else:
            self.terminal_display.append(
                f'<span style="color: #FFFFFF;">{self.response_output}</span>'
            )

        # Re-add the prompt bar for the next input
        self.append_prompt()
        self.is_processing = False
        self.terminal_display.moveCursor(QTextCursor.End)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            if self.history_index > 0:
                self.history_index -= 1
                self.input_field.setText(self.command_history[self.history_index])
        elif event.key() == Qt.Key_Down:
            if self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self.input_field.setText(self.command_history[self.history_index])
            elif self.history_index == len(self.command_history) - 1:
                self.history_index = len(self.command_history)
                self.input_field.clear()
        else:
            super().keyPressEvent(event)

app = QApplication(sys.argv)
terminal = ModernTerminal()
terminal.show()
sys.exit(app.exec_())
