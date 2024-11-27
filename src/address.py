prompts = {"model_json": """
	You will be given a user query. The user's intent may involve system-level changes or multitasking requests. Your role is to:

	Understand the User's Intent: Analyze the user’s prompt to determine if it involves:

	OS-level changes
	Multitasking (e.g., performing multiple system-level tasks or content generation alongside system changes).
	Generate a JSON Object: If the user's prompt involves one or more tasks, create a structured JSON object. The JSON object should adhere to the following:

	Mandatory Fields:

	operation: The type of operation being requested (e.g., "starting wifi", "checking usb devices", "file writing", "content generation").
	order: The execution sequence for multiple tasks. Use integers to indicate the sequence starting from 0.
	Custom Fields: Include additional fields specific to the operation (e.g., for file writing, include "name" and "location"; for volume change, include "level").

	Special Handling for Multitasking: If multiple tasks are requested:

	Break the tasks into separate operations.
	Assign each operation a unique sequence number in the order field.
	Formatting Guidelines:

	Begin the JSON object with @@@json and end it with @@@.
	For each operation, create a separate key-value pair in the JSON object with all relevant details.
	Examples:

	Example 1: Single Task (System-Level change)
	User Query: "Set volume to 50%."

	@@@json
		{
			"operation": "change_volume",
			"order": 0,
			"parameters": {
				"level": 50
				}
		}
	@@@

	Example 2: Multitasking (System-Level change)
	User Query: "Write a 500-word essay on Abraham Lincoln and save it as a file named 'lincoln.txt' in the root directory."

	@@@json
		{
			"operation 1": {
				"type": "content_generation",
				"order": 0,
				"parameters": {
				"topic": "Abraham Lincoln",
				"theme": "essay",
				"word_count": 500
				}
			},
			"operation 2": {
				"type": "file_writing",
				"order": 1,
				"parameters": {
				"name": "lincoln.txt",
				"location": "/"
				}
			}
	}
	@@@

	If the user's input is not requesting for any system level change, then label that as content generation and generate the json including the necessary fields.

""",

# Making sample ones for now

"model_1": """
		You will be given a prompt, where the user is asking for a file operations task. File operations tasks are defined as:

		**File Operations**:
		1. If the user wants to create, open, close, read, write, or delete a file, or perform any other action related to files.
		2. Requests involving directories (e.g., creating, deleting, or managing folders) are also considered file operations.
		3. Any user request, based on the prompt or history, that involves file manipulation counts as a file operation.
		4. Examples:
		   - Writing content to a specific file path.
		   - Creating or moving files or directories.

		Your job is to provide the bash code that they can type in the terminal to achieve what they are asking for. You must output the code, such that it is ready to copy and use as it is.
		You must output the code and nothing else.

		If you're asked to generate and write content, then you must generate the said content and then write it. 

		For example, if the user asks you to "Write a 10-word phrase to a file on the desktop." then the code becomes "echo "To be or not to be, that is the question." > ~/Desktop/essay_file.txt".
		That is, a 10 word phrase actually written, and then added to a file in the desktop.


""",

"model_2": """
		You will be given a prompt and some history. Your task is to determine if the given prompt requires any OS-level operations.

		Note on operating system applications:

		There is a difference between user programs and operating system. Any program that is not using the restricted instructions of the micro-processor and if using then using it through APIs is a user program.
		If the prompt and history demand the use of a user program then it is not an operating system level application.

		In general, you will have to classify the following as operating system operations as well. There may be more, but this is the general trend.

		**OS-Level Operations**:
		1. Requests for system information (e.g., CPU cores, available storage, hardware info).
		2. Managing system processes or configurations (e.g., changing file permissions, killing processes, using system services).
		3. Requests to perform system-wide actions like rebooting, updating, shutting down, or checking system status (e.g., battery, brightness, volume).
		4. Any other system operation that directly interacts with or required hardware information, that is, requires interaction with the operating system.
		5. Examples:
		   - Rebooting the system or viewing system settings.

		If the prompt requires any OS-level operation, output "yes".
		If the prompt does not involve OS-level operations, output "no".

		**Examples**:
		Prompt: Check the available system storage.
		Output: yes (reason: Retrieving system storage is an OS-level operation.)

		Prompt: Write a paragraph on renewable energy.
		Output: no (reason: The request only involves content generation, not system-level interaction.)

		Prompt: Write a 500 word essay on xyz and save it on the desktop.
		Output: no (reason: This requires file operations, and no direct correlation with the operating system, rather uses only user applications.)

""",

"model_3": """
		You will be given a prompt and some history. Your task is to determine if the given prompt requires any application-level operations.

		**Application-Level Operations**:
		1. Opening, closing, or interacting with GUI applications (e.g., opening a web browser, viewing a PDF).
		2. Launching applications that require a graphical interface.
		3. Any operation that requires the use of an application to access or display content (e.g., opening a document in a text editor).
		4. Examples:
		   - Opening a web page in a browser or a PDF in a PDF reader.

		If the prompt requires any application-level operation, output "yes".
		If the prompt does not involve application-level operations, output "no".

		**Examples**:
		Prompt: Open the calculator app.
		Output: yes (reason: This requires launching a GUI application.)

		Prompt: List all prime numbers under 50.
		Output: no (reason: This is a content generation task without application-specific interaction.)

""",

"model_4": """
		You will be given a prompt and some history. Your task is to determine if the given prompt requires any network operations.

		**Network Operations**:
		1. Managing network connections or devices (e.g., enabling/disabling Wi-Fi or Bluetooth, scanning devices).
		2. Requests involving network security or monitoring tools (e.g., using Wireshark, performing IP scans, SSH connections).
		3. Any task that requires interacting with network interfaces, such as checking IP configurations or managing Bluetooth connections.
		4. Examples:
		   - Enabling Wi-Fi, connecting to a Bluetooth device, or performing network scans.

		If the prompt requires any network-related operation, output "yes".
		If the prompt does not involve network-related operations, output "no".

		**Examples**:
		Prompt: Connect to Wi-Fi network "Home_Network".
		Output: yes (reason: Managing Wi-Fi is a network operation.)

		Prompt: Explain network topologies.
		Output: no (reason: This only involves generating content, not performing network operations.)

""",

"model_5": """
		You will be given a prompt and some history. Your task is to determine if the given prompt requires any installation operations.

		**Installation Operations**:
		1. Requests to install applications, libraries, or packages (e.g., Python packages, system applications).
		2. Commands or tasks that involve "install" operations, such as "sudo apt-get install", "pip install", or "snap install".
		3. Any installation command, regardless of package type (e.g., Ruby gems, NPM packages).
		4. Examples:
		   - Installing a new application or library.

		If the prompt requires any installation operation, output "yes".
		If the prompt does not involve installation operations, output "no".

		**Examples**:
		Prompt: Install NumPy for Python.
		Output: yes (reason: This request requires installing a Python package.)

		Prompt: Describe the uses of NumPy.
		Output: no (reason: This only requests content without installation.)

""",

"model_6": """
		You will be given a prompt and some history. Your task is to determine if the given prompt requires content generation operations.

		**Content Generation Operations**:
		1. Requests to generate text or information without any further action, such as "explain", "summarize", or "list".
		2. Content requests that do not require system commands (e.g., `os.system()`) or interaction with files or applications.
		3. Any prompt asking for displayed or printed content without additional operations.
		4. Examples:
		   - Generating summaries, essays, or examples.

		If the user is in a conversational tone, then the output should be "yes"

		If the prompt requires content generation, output "yes".
		If the prompt does not involve content generation, output "no".

		**Examples**:
		Prompt: Write a 300-word essay on climate change.
		Output: yes (reason: This requires content creation without other operations.)

		Prompt: Write a 300-word essay to a file on the desktop.
		Output: no (reason: This includes file operations for saving content.)

"""
}