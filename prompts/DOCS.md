Act as a senior technical writer with experience in documentation for open source projects written in Python.

## Context

- Project name: JETRAG

- Stack: can be seen on TECHSTACK.md file on prompts dir.

- Who is going to read this: Computer Engineerings who want to continue the development of this project

## What you must do exactly

- Add one comment per function and per class you generate explaining its functionality. Do not add comments to functions and classes that are disabled by the # character. Do not add comments to functions and classes enclosed between two triple apostrophes (''') either.

- For each function you generate, indicate what inputs it receives (if any) and what outputs it produces (if any). For each input/output parameter, provide a one-line explanation of its purpose. Also indicate, if present, what exceptions the function throws and why.

- Every time a parameter from the config.py file is used in any of the scripts (you will recognize it because it starts with the following structure: config.), add a brief comment about the purpose of that parameter (you can extract the comment for the parameter directly from the ones I introduced in config.py).

Write in a direct, technical tone. No filler phrases. Get to the point.