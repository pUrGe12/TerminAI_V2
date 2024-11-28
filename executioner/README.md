# Executioner

This piece of code does the following

- [ ] Takes the categorised json.


## The plan

		- operation 0
		- category: something, operation: something, parameters: something

		based on category call the right model, pass it the operation and parameters. Get the code

		- operation 1 
		- category: something, operation: something, parameters: something

		based on category call the right model, pass it the operation and parameters. Get the code

		- operation 2 
		- category: something, operation: something, parameters: something

		based on category call the right model, pass it the operation and parameters. Get the code

		Now, execute them in order,

		first execute operation 0,
		then execute operation 1,
		then execute operation 2.

		So, we'll first get all their codes, push that in a queue (fifo - so, the first code in, will be the first out when we use get), then empty the queue and execute the commands
