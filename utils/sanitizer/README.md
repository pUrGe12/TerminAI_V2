# Sanitizer

This takes the generated command and determines if its harmful to the sytem. From the 7 categories we've defined, we only need to implement this in the following categories

1. file operations: So that the user doesn't accidently delete important files
2. operating system operations: So that the user doesn't erase some important partition or something
3. application operations: To ensure that no critical applications are deleted (what if they write delete the terminal!)

---

## Functionality

The sanitizer takes in the command generated and checks for the above 3 cases. If it finds a harmful command then it returns "Harmful: {reason}", else it returns the exact same command with no changes.