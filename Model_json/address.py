prompts = {"model_json": """
	
	You will be given a prompt and a history of prompts and responses. The user wants to perform OS-level operations on their system.

	**OS-Level Operations** include any actions that interact with the operating system directly. These may include, but are not limited to:
	  1. **System Information**: Retrieving details like the number of CPU cores, total available storage, RAM usage, or other hardware-related information.
	  2. **System Management**: Managing processes, changing file permissions, using `systemctl` commands in Linux (e.g., to start, stop, enable, or disable services).
	  3. **System Control**: Rebooting, shutting down, installing updates, or other actions that affect the system's state.
	  4. **Device Settings**: Adjusting brightness, changing volume, or other hardware settings.
	  
	**Your Task**:
	1. **Generate a JSON object** that contains all necessary fields for the OS-level action requested. Tailor each field specifically to the type of operation.
	   - **Required Fields in JSON**:
	     - **operation**: Specify the action (e.g., "get_cpu_cores", "shutdown", "change_volume").
	     - **target**: Describe the target if applicable (e.g., "CPU", "volume", "brightness", or "service name" for systemctl actions).
	     - **parameters**: List any additional parameters or settings relevant to the action (e.g., "level: 75" for volume, "permissions: 755" for chmod).
	     - **confirmation_required**: Specify if the operation requires confirmation (e.g., `true` for reboot or shutdown actions).
	   
	   There might be more relevant fields, include that as well. Include everything that is necessary.

	2. **Generate a summary** of the action performed in under 20 words.
	   - The summary should **describe the action** (e.g., "Adjusted volume to 50%" or "Retrieved CPU core count").

	**Output Format**:
	- **JSON Object**: Format the JSON output exactly as shown below. Begin with `@@@json` and end with `@@@`.
	  
	@@@json
	{
	  "operation": "value",
	  "target": "value",
	  "parameters": {
	    "param_1": "value",
	    "param_2": "value",
	    ...
	  },
	  "confirmation_required": true/false
	}
	@@@

	- **Summary**: Format the summary exactly as shown below. Begin with `$$$summary` and end with `$$$`.

	$$$summary
	<summary text>
	$$$

	**Example Output** (These are examples, you do not have to follow them exactly but they are a good reference point):

	For a request to adjust system volume:
	  
	@@@json
	{
	  "operation": "change_volume",
	  "target": "volume",
	  "parameters": {
	    "level": 75
	  },
	  "confirmation_required": false
	}
	@@@

	$$$summary
	Set volume to 75%.
	$$$

	For a request to retrieve CPU core count:

	@@@json
	{
	  "operation": "get_cpu_cores",
	  "target": "CPU",
	  "parameters": {},
	  "confirmation_required": false
	}
	@@@

	$$$summary
	Retrieved CPU core count.
	$$$

	**Important**: Generate only the JSON and summary exactly as specified, following the formatting strictly.
	
""",

"model_1": """
		You will be given a prompt and some history. Your task is to determine if the given prompt requires any file operations.

		**File Operations**:
		1. If the user wants to create, open, close, read, write, or delete a file, or perform any other action related to files.
		2. Requests involving directories (e.g., creating, deleting, or managing folders) are also considered file operations.
		3. Any user request, based on the prompt or history, that involves file manipulation counts as a file operation.
		4. Examples:
		   - Writing content to a specific file path.
		   - Creating or moving files or directories.

		If the prompt requires any file operation, output "yes".
		If the prompt does not involve file operations, output "no".

		**Examples**:
		Prompt: Write a 500-word essay to a file on the desktop.
		Output: yes (reason: Writing content to a file is a file operation.)

		Prompt: Write a 500-word essay about Lincoln.
		Output: no (reason: This only requests content generation without file operations.)

		Use the history for additional context.

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