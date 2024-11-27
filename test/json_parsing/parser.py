import json

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
	a = op['operation'].replace('_', ' ') 			# In case we need to, will not give errors if none found
	print(a)