# TerminAI_V2

A python based terminal with AI capabilities. Forget commands, just tell it what it do!

# Framework 

This is the third draft of TerminAI. This is without history implementation.

![TerminAI](./images/TerminAI_V2_draft_3.png)

# To install

Run the following command to install the dependencies

		pip install -r requirements.txt

## Completed work

- [x] Created os environment for the API keys.
- [x] Created the json model framework.
- [x] Figure out how to import files present in other directories.
- [x] Write prompts for the json model.
- [x] Test terminal with the model.

## Pending work

- [ ] It's giving some errors sometimes. Why? Weird errors, not very frequent, but there must be some bug somewhere.
- [ ] Loading the `main.py` is sometimes triggering the "application not responding" dialogue box (even though it is).
- [ ] Create the dictionary that will relate the operation category to the relevant model call.

- [ ] Ensure that the model json using regular expressions correctly. If the model outputs the json in between '`' then we want to avoid printing that!
---

If it becomes too heavy for your computer to run all these models along with other systems in parallel, you can use the resources of a workstation and run this in your own computer! (Coming out soon)

---

The way we get the execution order working, we execute the first command, and get the output, then use that to execute the second command and so on.