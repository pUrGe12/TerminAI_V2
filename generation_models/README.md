# Generation models

These are different models, generating code for 5 broad categories.

1.
2.
3.
4.
5.

They basically ensure 2 things

1. They generate the necessary code
2. They open up a subprocess and execute it


We must be careful before executing it, in case the model decided to return `sudo rm -rf /*` cause then the user is fuckd.


Ideally we want a RAG or something that is specifically tailored to only giving out codes for a specific class of operations to handle this. For the first product, we'll just use Gemini.