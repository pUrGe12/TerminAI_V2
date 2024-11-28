
## Things that work

- [x] Terminal GUI that allows users to enter a prompt and processes it.
- [x] Imports across directories, so we don't have to write all the code in one file.
- [x] The Json generation model and it's output.

## Pending work

- [ ] Ensure execution in the desired sequence.
- [ ] Create a parser for the json object and figure out the number of operations and the sequence in which they are to be executed.
- [ ] Call the relevant models and execute them. All of this probably falls under the `start_processing` function. We can define other methods for each model and call them as and when required.
- [ ] Display the final captured output to the user.

### Imports

To import the different models and the `json model`, we use `__init__.py` files in each directory (that we want to play the import game with)

Then inside the file that you want to import things to (in our case the `main.py` file) we write the following line of code

		sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 

With this we are adding the root directory to the path, so that python knows where to start the referencing from. In this case, it's two directories back from the `src` directory and hence, we've used it twice.

We can do this locally using the terminal as well, but its better to do it dynamically as it makes it easier for the users.

