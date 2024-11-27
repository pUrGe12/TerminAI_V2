import json

prompt = """connect to wifi "motog73" and start wireshark recording"""

test_js = """ 
[
	{ 
		"operation": "connect_wifi", 
			"order": 0, 
			"parameters": { "wifi_name": "motog73" } 
	},

	{ 
		"operation": "start_wireshark_recording", 
			"order": 1, 
			"parameters": {}  
	} 
] """


operations = json.loads(test_js)

sorted_operations = sorted(operations, key=lambda x: x['order']) 			# in general we can assume it will give us the sorted output only

for op in sorted_operations:
	''' We've ensured that the parameter will be "operation" itself and not "operation 1" or something'''
	a = op['operation'].replace('_', ' ') 			# In case we need to, will not give errors if none found
	print(a)


''' 
The next step is classifying them into one of the 6 categories and then calling the right function. We will prolly have to use a LLM here as well.

Alternatively, we can tell the main guy to classify it for us... Ponder...

'''
