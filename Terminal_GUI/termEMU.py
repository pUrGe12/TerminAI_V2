import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtCore import Qt, QTimer


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
        if self.is_processing:
            return

        self.is_processing = True
        self.current_prompt = self.input_field.text()

        if self.current_prompt.strip():
            self.terminal_display.insertPlainText(self.current_prompt + "\n")
            self.command_history.append(self.current_prompt)
            self.history_index = len(self.command_history)

            self.terminal_display.append(
                '<span style="color: #FFB86C;">Generating response...</span>'
            )
            self.terminal_display.moveCursor(QTextCursor.End)

            self.model_json(self.current_prompt)        # This is where we give the processing logic

        self.input_field.clear()

    def model_json(self, prompt):
        '''
        This function is to replicate the running of the models. At first, we'll run the json creator model.
    
        For now, we're omitting the history implementation. If not, then this function would take as input the history as well.
        '''

        processed_output = self.current_prompt              # currently setting the processed prompt as the current prompt
        QTimer.singleShot(5000, self.display_response)
        return processed_output


    def display_response(self):
        '''
            This function first removes the "generating response..." part and displays the output from proces_prompt.
        '''
        cursor = self.terminal_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.select(QTextCursor.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()  # Remove the newline after the prompt
        self.terminal_display.append(
            f'<span style="color: #FFFFFF;">{self.current_prompt}</span>'
        )
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    terminal = ModernTerminal()
    terminal.show()
    sys.exit(app.exec_())
