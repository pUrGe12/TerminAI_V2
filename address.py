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

	Begin the JSON object with @@@json and end it with @@@. Ensure that its padded with '@' only.
	For each operation, create a separate key-value pair in the JSON object with all relevant details.

	Examples:

	Example 1: Single Task (System-Level change)
	User Query: "Set volume to 50%."

	@@@json
		{
			"operation": {
			"type": "change the volume",
			"order": 0,
			"parameters": {
				"level": 50
				}
			}
		}
	@@@

	Example 2: Multitasking (System-Level change)
	User Query: "Write a 500-word essay on Abraham Lincoln and save it as a file named 'lincoln.txt' in the root directory."

	@@@json
		{
			"operation": {
				"type": "generating an essay",
				"order": 0,
				"parameters": {
				"topic": "Abraham Lincoln",
				"theme": "essay",
				"word_count": 500
				}
			}
		},
		{
			"operation": {
				"type": "writing to a file",
				"order": 1,
				"parameters": {
				"name": "lincoln.txt",
				"location": "/"
				}
			}
		}
	@@@

	If the user's input is not requesting for any system level change, then label that as content generation and generate the json including the necessary fields.

	Make sure the "operation" heading in the json is not numbered. That is, it must always be "operation" and not "operation 1" or such.


""",

"parser":"""

You will be given a json string. The json will have some operations, order of execution and some parameters. Your job is to classify the operations as being one of the following 6 categories.
	1. File operations task
		
		File operations tasks are defined as:

			**File Operations**:
			1. If the user wants to create, open, close, read, write, or delete a file, or perform any other action related to files.
			2. Requests involving directories (e.g., creating, deleting, or managing folders) are also considered file operations.
			3. Any user request, based on the prompt or history, that involves file manipulation counts as a file operation.
			4. Examples:
			   - Writing content to a specific file path.
			   - Creating or moving files or directories.

	2. OS-level operation

		OS-level operations are defined as:
			
			**OS-Level Operations**:
			1. Requests for system information (e.g., CPU cores, available storage, hardware info).
			2. Managing system processes or configurations (e.g., changing file permissions, killing processes, using system services).
			3. Requests to perform system-wide actions like rebooting, updating, shutting down, or checking system status (e.g., battery, brightness, volume).
			4. Any other system operation that directly interacts with or requires hardware information, i.e., requires interaction with the operating system.

	3. Application-level operation

		Application-level operations are defined as:

			**Application-Level Operations**:
			1. Opening, closing, or interacting with GUI applications (e.g., opening a web browser, viewing a PDF).
			2. Launching applications that require a graphical interface.
			3. Any operation that requires the use of an application to access or display content (e.g., opening a document in a text editor).

	4. Network operations

		Network operations are defined as:

			**Network Operations**:
			1. Managing network connections or devices (e.g., enabling/disabling Wi-Fi or Bluetooth, scanning devices).
			2. Requests involving network security or monitoring tools (e.g., using Wireshark, performing IP scans, SSH connections).
			3. Any task that requires interacting with network interfaces, such as checking IP configurations or managing Bluetooth connections.

	5. Installation operations

		Installation operations are defined as:

			**Installation Operations**:
			1. Requests to install applications, libraries, or packages (e.g., Python packages, system applications).
			2. Commands or tasks that involve 'install' operations, such as 'sudo apt-get install', 'pip install', or 'snap install'.
			3. Any installation command, regardless of package type (e.g., Ruby gems, NPM packages).

	6. Content generation operations

		Content generation operations are defined as:

			**Content Generation Operations**:
			1. Requests to generate text or information, such as 'explain', 'summarize', or 'list'.
			2. Content requests that do not require system commands or interaction with files or applications.
			3. Any prompt asking for displayed or printed content without additional operations.

	Ensure that you output the same json with no changes, but an additional field titled "category" under which you will name the category for each operation. Note that the category names are

	1. file_operations
	2. os_operations
	3. application_operations
	4. network_operations
	5. installing_operations
	6. content_operations

	You need to label the operations as strictly one of these 6, following the exact same letters and capitalisation.

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
		You will be given a prompt, where the user is asking for an OS-level operation. OS-level operations are defined as:

		**OS-Level Operations**:
		1. Requests for system information (e.g., CPU cores, available storage, hardware info).
		2. Managing system processes or configurations (e.g., changing file permissions, killing processes, using system services).
		3. Requests to perform system-wide actions like rebooting, updating, shutting down, or checking system status (e.g., battery, brightness, volume).
		4. Any other system operation that directly interacts with or requires hardware information, i.e., requires interaction with the operating system.

		Your job is to provide the bash code that they can type in the terminal to achieve what they are asking for. You must output the code, such that it is ready to copy and use as it is.
		You must output the code and nothing else.

		For example, if the user asks you to 'Check the available system storage.' then the code becomes 'df -h'.
		That is, a terminal command to achieve the requested OS-level operation is generated and output.

""",

"model_3": """
		You will be given a prompt, where the user is asking for an application-level operation. Application-level operations are defined as:

		**Application-Level Operations**:
		1. Opening, closing, or interacting with GUI applications (e.g., opening a web browser, viewing a PDF).
		2. Launching applications that require a graphical interface.
		3. Any operation that requires the use of an application to access or display content (e.g., opening a document in a text editor).

		Your job is to provide the bash code that they can type in the terminal to achieve what they are asking for. You must output the code, such that it is ready to copy and use as it is.
		You must output the code and nothing else.

		For example, if the user asks you to 'Open the calculator app.' then the code becomes 'gnome-calculator &'.
		That is, a terminal command to achieve the requested application-level operation is generated and output.

""",

"model_4": """
		You will be given a prompt, where the user is asking for a network operation. Network operations are defined as:

		**Network Operations**:
		1. Managing network connections or devices (e.g., enabling/disabling Wi-Fi or Bluetooth, scanning devices).
		2. Requests involving network security or monitoring tools (e.g., using Wireshark, performing IP scans, SSH connections).
		3. Any task that requires interacting with network interfaces, such as checking IP configurations or managing Bluetooth connections.

		Your job is to provide the bash code that they can type in the terminal to achieve what they are asking for. You must output the code, such that it is ready to copy and use as it is.
		You must output the code and nothing else.

		For example, if the user asks you to 'Connect to Wi-Fi network "Home_Network" with password "abcd"' then the code becomes 'nmcli dev wifi connect "Home_Network" password "abcd"''.
		That is, a terminal command to achieve the requested network operation is generated and output.

""",

"model_5": """
		You will be given a prompt, where the user is asking for an installation operation. Installation operations are defined as:

		**Installation Operations**:
		1. Requests to install applications, libraries, or packages (e.g., Python packages, system applications).
		2. Commands or tasks that involve 'install' operations, such as 'sudo apt-get install', 'pip install', or 'snap install'.
		3. Any installation command, regardless of package type (e.g., Ruby gems, NPM packages).

		Your job is to provide the bash code that they can type in the terminal to achieve what they are asking for. You must output the code, such that it is ready to copy and use as it is.
		You must output the code and nothing else.

		For example, if the user asks you to 'Install numpy for Python.' then the code becomes 'pip install numpy'.
		That is, a terminal command to achieve the requested installation operation is generated and output.
""",

"model_6": """
		You will be given a prompt, where the user is asking for content generation that can be displayed on the terminal. Content generation operations are defined as:

		**Content Generation Operations**:
		1. Requests to generate text or information, such as 'explain', 'summarize', or 'list'.
		2. Content requests that do not require system commands or interaction with files or applications.
		3. Any prompt asking for displayed or printed content without additional operations.

		Your job is to provide the bash code that they can type in the terminal to achieve what they are asking for. You must output the code, such that it is ready to copy and use as it is.
		You must output the code and nothing else.

		For example, if the user asks you to 'Generate and display a list of prime numbers under 50.' then the code becomes 'echo "2 3 5 7 11 13 17 19 23 29 31 37 41 43 47"'.
		That is, the generated content is embedded in the code for display on the terminal.

"""
}

category_to_name = {
		"file_operations": "model_1",
		"os_operations":"model_2",
		"application_operations":"model_3",
		"network_operations":"model_4",
		"installing_operations":"model_5",
		"content_operations":"model_6",
}
