import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtCore import Qt, QTimer
 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # adding the root directory to path

from Model_json.model_json import GPT_response
from json_parsing.categoriser import categorise

class ModernTerminal(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.command_history = []
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
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # Terminal display area
        self.terminal_display = QTextEdit()
        self.terminal_display.setReadOnly(True)
        self.terminal_display.setStyleSheet("""
            QTextEdit {
                background-color: #282828;
                color: #FFFFFF;
                border: none;
                padding: 10px;
            }
        """)
        self.terminal_display.setFont(QFont("Monospace", 11))

        # Modifying the input field
        self.input_field = QLineEdit()
        self.input_field.setFont(QFont("Monospace", 11))
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #282828;
                color: #FFFFFF;
                border: none;
                padding: 2px;
            }
        """)
        self.input_field.returnPressed.connect(self.start_processing)

        # Add widgets to main layout
        self.main_layout.addWidget(self.terminal_display)
        self.main_layout.addWidget(self.input_field)

        # Set main layout
        self.setLayout(self.main_layout)

        # Setting up the prompt bar
        self.append_prompt()

    def append_prompt(self):
        '''
        This is the prompt bar. 
        '''
        current_dir = os.getcwd()
        home = os.path.expanduser("~")
        if current_dir.startswith(home):
            current_dir = "~" + current_dir[len(home):]

        arrow_color = "#98C379"  # Green color for the arrow
        path_color = "#56B6C2"   # Blue color for the current directory path
        symbol_color = "#C678DD"  # Purple color for the "$" symbol

        prompt_text = (
            f'<span style="color: {arrow_color};">➜</span> '
            f'<span style="color: {path_color};">{current_dir}</span> '
            f'<span style="color: {symbol_color};">$</span> '
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
            
            # Run the categoriser on the output
            categorised_output = categorise(processed_output)  
            self.response_output = categorised_output  # Store the categorised output
        except Exception as e:
            self.response_output = f"Error: {str(e)}"  # Handle errors gracefully

        # Simulate delay before displaying response
        QTimer.singleShot(5000, self.display_response)

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
        if isinstance(self.response_output, dict):              # pretty-print JSON if it's a dict
            import json
            formatted_output = json.dumps(self.response_output, indent=4)
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