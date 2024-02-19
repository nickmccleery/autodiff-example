# Environment Setup

Use of pyenv for is recommended for the management of multiple Python versions. To install pyenv on a Unix-based
system then configure the desired version for this project (3.11), steps are follows:

1. Install `pyenv`:
   - https://github.com/pyenv/pyenv#unixmacos
2. Install python version: `pyenv install 3.11`
3. Set local environment in working directory `pyenv local 3.11`.

This will create a `.python-version` file in the working directory.

Use a virtual environment is also recommended. To achieve this with `venv`, follow the steps below:

1. Install `venv`:
   - `sudo apt-get install python3-venv`
2. Create a virtual environment:
   - `python3 -m venv environment/venv/development`
3. Activate the virtual environment:
   - `source environment/venv/development/bin/activate`
4. Install the project dependencies:
   - `pip install -r environment/requirements.txt`

## VSCode Usage

If using VSCode, it will also be necessary to set the Python interpreter to the local environment. This can be achieved
by launching the command palette (`Ctrl+Shift+P` or `F1`) and searching for `Python: Select Interpreter`. Select
the file at `environment/venv/development/bin/python` to set the interpreter.
