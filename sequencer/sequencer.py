'''
This piece of code defines a function that does the following

1. It takes in the json input with the categories and all, and based on the order puts them in a queue.
2. Inside the queue it keeps the operation, the model name (we'll keep a dictionary that translates the given function to the model name), 
   and another queue for the user's prompt. Note that it needn't keep the order now, since by virtue of the queue, they are ordered.
3. It returns the user's prompt_queue and the operations_queue. Later we can probably add the history_queue as well.

'''

import json
import queue

prompt_queue = queue.Queue()
operations_queue = queue.Queue()

def add_prompt(prompt):
	prompt_queue.put(prompt)

def add_operations(op):
	'''
		op must be a list. The list contains the operation, and the model name.
	'''
	assert type(op) == list, 'op must be a list'
	operations_queue.put(op)

operation_to_name = {
		"file_operations": "model_1",
		"os_operations":"model_2",
		"application_operations":"model_3",
		"network_operations":"model_4",
		"installing_operations":"model_5",
		"content_operations":"model_6",
}

