'''
This piece of code defines a function that does the following

1. It takes in the json input with the categories and all, and based on the order puts them in a queue.
2. Inside the queue it keeps the operation, the model name (we'll keep a dictionary that translates the given function to the model name). 
   Note that it needn't keep the order now, since by virtue of the queue, they are ordered.
3. It returns the operations_queue. 

Now we have to make it importable and usable in the main file.
'''

import json
import queue

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # adding the root directory to path

from address import category_to_name

operations_queue = queue.Queue()

def add_operations(operation_type, model_name, parameters):
    """
    Add operations to the operations queue.
    Each operation includes:
    - operation_type: The type of operation (e.g., "list_wifi").
    - model_name: The name of the model (e.g., "NetworkScanner").
    - parameters: A dictionary of parameters for the operation.
    """
    operations_queue.put({
        "operation_type": operation_type,
        "model_name": model_name,
        "parameters": parameters,
    })

def process_json(input_json):
    """
    Process the input JSON, sort operations by 'order', and add them to the queue.
    """
    try:
        data = json.loads(input_json)
        
        # Convert the operations to a list if not already
        operations = data if isinstance(data, list) else [data]
        
        # Sort operations by 'order' key
        sorted_operations = sorted(operations, key=lambda x: x.get("operation", {}).get("order", float("inf")))
        
        for op in sorted_operations:
            operation_details = op.get("operation", {})
            operation_type = operation_details.get("type")
            category = operation_details.get("category", "unknown_category")
            parameters = operation_details.get("parameters", {})
            model_name = category_to_name.get(category.lower(), "UnknownModel")
            
            # Add to operations queue
            add_operations(operation_type, model_name, parameters)
        
        return operations_queue

    except json.JSONDecodeError:
        print("Invalid JSON format")
        return None

# sample_json = """

# 	{ 
# 		"operation": { 
# 			"type": "writing to a file", 
# 			"order": 1, 
# 			"parameters": { 
# 				"name": "abhraham lincon", 
# 				"location": "Desktop/", 
# 				"content": "Write a 500 word essay on abhraham lincon and save that in the desktop" 
# 			}, 
# 			"category": "file_operations" 
# 		}
# 	},
    
# 	{
# 		"operation": { 
# 			"type": "generating an essay", 
# 			"order": 0, 
# 			"parameters": { 
# 				"topic": "abhraham lincon", 
# 				"theme": "essay", 
# 				"word_count": 500 
# 			}, 
# 			"category": "content_operations" 
# 		} 
		
# 	}

# """

# # Process the JSON and populate queues
# operations_q = process_json(f"[{sample_json}]")


# ''' This is essentially what I need to do in the main code. We will get the operations queue.  '''

# while not operations_q.empty():
#     print("Operations Queue:", operations_q.get())

'''
output: 
Operations Queue: {'operation_type': 'generating an essay', 'model_name': 'model_6', 'parameters': {'topic': 'abhraham lincon', 'theme': 'essay', 'word_count': 500}}
Operations Queue: {'operation_type': 'writing to a file', 'model_name': 'model_1', 'parameters': {'name': 'abhraham lincon', 'location': 'Desktop/', 'content': 'Write a 500 word essay on abhraham lincon and save that in the desktop'}}

Works!
'''