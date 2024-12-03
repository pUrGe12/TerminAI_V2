import sys
import os

# uncomment the following line of code if you don't see the terminal exactly how it looks like in the README file.
# os.environ["QT_QPA_PLATFORM"] = "wayland"

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
from concat_model.concat import concatenate

# Importing the generation models
from generation_models.model_1 import generate_command_1, execute_1         # File operations
from generation_models.model_2 import generate_command_2, execute_2         # OS-level operations
from generation_models.model_3 import generate_command_3, execute_3         # Application operations
from generation_models.model_4 import generate_command_4, execute_4         # Network operations
from generation_models.model_5 import generate_command_5, execute_5         # Installation operations
from generation_models.model_6 import generate_command_6, execute_6         # Content generation operations
from generation_models.model_7 import generate_command_7, execute_7         # Error fixing operations

# Supabase history initialisation
from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path

# Load the data from the setup files as a dictionary
from utils.setup.data import user_dict

load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')              # Loading the enviornment

url: str = str(os.getenv("SUPABASE_URL")).strip()
key: str = str(os.getenv("SUPABASE_KEY")).strip()

supabase: Client = create_client(url, key)


def add_history(user_prompt, categoriser_json, results):
    ''' 
    Requires the following fields
    1. Prompt: This is the user's prompt, needs to be added everytime
    2. Categorizer_json: We are also adding the categorizer's json because it contains a good summary of everything that needs to be done
    3. Results: This is a list of the results that is made, we'll add this for final outputs.

    Ensure that the models know how to handle this data. Also make sure that column type is jsonb. 
    '''
    assert type(results) == list, 'results must be a list'

    Info = {'Prompt': user_prompt, 'Categorizer_json': categoriser_json, 'Results': results}
    response = supabase.table('History_v3').insert(Info).execute()
    

def get_history(n):
    ''' Gets the last n entries from the History_v3 table. We'll usually just pull the last entry and thats all '''
    history = supabase.table('History_v3').select("*").order('id', desc=True).limit(n).execute().data
    return history


class Worker(QThread):
    '''
    QThread for running the processing logic in a seperate thread so that we can display "generating response..." while the processing is being done

    Creating a different class works the best! This has the the run and execute operations, and we simply initialise this class when we need.
    '''

    result_ready = pyqtSignal(list)             # Here we emit results when processing is done

    def __init__(self, prompt, parent=None):
        super().__init__(parent)
        self.prompt = prompt

    def run(self):
        """
        Run the GPT model and process the operations in a background thread. The run() function calls the following functions

        1. GPT_response --> which creates the initial json
        2. categoriser --> Which adds the categories to all operations
        3. process_json --> Returns a queue of operations based on the categoriser's json
        4. exeucte_queue --> picks each operation from the queue one by one and executes.
         """

        try:
            ''' We're going to pull from the database here, because we need to pass it to the GPT_response to get the main json right. '''

            history = get_history(1)
            print(f'Pulled history: {history}')

            username = user_dict.get("username")
            operating_system = user_dict.get("operating_system")
            sudo_password = user_dict.get("sudo_password")

            processed_output = GPT_response(
                user_prompt = self.prompt, 
                history = history, 
                username = username, 
                operating_system = operating_system, 
                sudo_password = sudo_password
                )

            print(f"processed_output = {processed_output}")
            
            categorised_output = categorise(processed_output)
            operations_q = process_json(f"{categorised_output}")
            results = self.execute_queue(operations_q, categorised_output)

            ''' We're gonna add to history here, because we have the necessary things '''
            add_history(user_prompt = self.prompt, categoriser_json = categorised_output, results = results)

            print('Added history')

        except Exception as e:
            results = [f"Error: {str(e)}"]
        
        self.result_ready.emit(results)

    def execute_queue(self, operations_q, categorised_output):
        """ 
        Process the queue of operations one by one, we get the queue from above after calling process_json on it.
        The queue contains the operation type, model name (which is required to execute that), and the parameters necessary for it.

        Here, we wait until the queue is empty and keep popping it and execute respectively.
        """
        results = []
        model_dispatch = {
            "model_1": ("generation_models.model_1", "generate_command_1", "execute_1"),
            "model_2": ("generation_models.model_2", "generate_command_2", "execute_2"),
            "model_3": ("generation_models.model_3", "generate_command_3", "execute_3"),
            "model_4": ("generation_models.model_4", "generate_command_4", "execute_4"),
            "model_5": ("generation_models.model_5", "generate_command_5", "execute_5"),
            "model_6": ("generation_models.model_6", "generate_command_6", "execute_6"),                # Not executing model_6 commands cause they're not commands
            "model_7": ("generation_models.model_7", "generate_command_7", "execute_7")
        }

        additional_data = ''

        while not operations_q.empty():

            # print('previous data: ', additional_data)

            operation = operations_q.get()
            # print(operation)

            operation_type = operation.get('operation_type')
            model_name = operation.get('model_name')
            parameters = operation.get('parameters')

            if model_name in model_dispatch:
                # Hopefully its not an unknown model, cause it shoudn't be at all

                module_path, generate_func, execute_func = model_dispatch[model_name]
                
                try:
                    model_module = __import__(module_path, fromlist=[generate_func, execute_func])
                    generate_command = getattr(model_module, generate_func)
                    execute_command = getattr(model_module, execute_func)

                    command = generate_command(
                        operation=operation_type, 
                        parameters=parameters, 
                        additional_data=additional_data
                    )                                       # Passing the additional_data here.

                    print('command: ', command)

                    # We're handling changing of directories here itself. This is because running this in a subprocess does not reflect in the terminal 
                    
                    if command.strip().startswith("cd "):
                        target_dir = command.split(" ", 1)[1]
                        target_dir = os.path.expanduser(target_dir)
                        os.chdir(target_dir)
                        
                        output = f"Changed directory to {os.getcwd()}"
                        concat_output = f"{concatenate(user_prompt = self.prompt, final_output = output)} \n"

                    else:
                        if model_name != "model_6":
                            # We only execute command when model is not for generation. 
                            
                            output = execute_command(command)
                            concat_output = f"{concatenate(user_prompt = self.prompt, final_output = output)} \n"
                        else:
                            output = command                                # we want the reply as it is because its not a system level change
                            print('this is the generated content: ', output)
                            concat_output = f"{concatenate(user_prompt = self.prompt, final_output = output)} \n"

                    results.append(concat_output)                           # We add the pretty output here 
                    additional_data = output                                # We can't add the concat output here because thats a summary

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

        # Setting up the main layout, setContentsMargins() defines the borders and the whitespacing.
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

        self.main_layout.addWidget(self.terminal_display, stretch=1)                # Stretch just means expand this thing till 0 padding.
        self.main_layout.setSpacing(0)                                              # Remove whitespace between the others and input field.
        self.main_layout.addWidget(self.input_field, stretch=0)

        self.setLayout(self.main_layout)
        
        # Setting up the prompt bar 
        self.append_prompt()

    def append_prompt(self):
        ''' The prompt bar is the little snippet when we enter the commands 

        We are keeping it simple with this one, just the username, hostname (that we didn't use), and the current directory.
        - In the future we can try adding color coding and git status?
        '''

        user = os.getenv("USER", 'user')        # We get the user name from here. We should probably pass this to the models as well
        host = os.uname().nodename
        current_dir = os.getcwd()
        home = os.path.expanduser("~")
        if current_dir.startswith(home):
            current_dir = "~" + current_dir[len(home):]

        # Keeping everything black, except the "$" sign which is white. Looks aesthetic!
        prompt_text = (
            f'<span style="color: #000000;">{user}</span>'
            f'<span style="color: #000000;">@UB</span>:'
            f'<span style="color: #000000;">{current_dir}</span>'
            f' <span style="color: #FFFFFF;">$</span> '
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

            # First we insert the prompt in the right place
            self.terminal_display.insertPlainText(self.current_prompt + "\n")
            
            # Calling the generating response part here, in a seperate thread.
            self.terminal_display.append(
                '<span style="color: #FFB86C;">Generating response...</span>'
            )
            self.terminal_display.moveCursor(QTextCursor.End)       # Ensuring that the cursor stays at the bottom
            QApplication.processEvents()

            self.worker = Worker(self.current_prompt)               # Here we are calling the Worker class, and processing the input in a seperate thread.
            self.worker.result_ready.connect(self.display_response)
            self.worker.start()

        self.input_field.clear()                                    # Since this is a different thread, it clears the input field as soon as we press enter

    def display_response(self, results):
        ''' This function is being used to display the final processed output from the results list '''

        cursor = self.terminal_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.select(QTextCursor.LineUnderCursor)
        
        cursor.removeSelectedText()
        cursor.deletePreviousChar()

        formatted_output = f"\n <span style='color: #007ACC;'>Response:</span> {results[-1]} \n"             # We're printing only the last entry in the results because it contains the concatenated output of all
        
        self.terminal_display.append(f"<pre>{formatted_output}</pre>")

        # Then we add the prompt bar again for the next input
        self.append_prompt()
        self.is_processing = False          # Keep track of stuff man

app = QApplication(sys.argv)
terminal = ModernTerminal()
terminal.show()
sys.exit(app.exec_())
