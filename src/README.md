
### Imports

To import the different models and the `json model`, we use `__init__.py` files in each directory (that we want to play the import game with)

Then inside the file that you want to import things to (in our case the `main.py` file) we write the following line of code

		sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 

With this we are adding the root directory to the path, so that python knows where to start the referencing from. In this case, it's two directories back from the `src` directory and hence, we've used it twice.

We can do this locally using the terminal as well, but its better to do it dynamically as it makes it easier for the users.