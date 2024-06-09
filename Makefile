BLACK ?= \033[0;30m
RED ?= \033[0;31m
GREEN ?= \033[0;32m
YELLOW ?= \033[0;33m
BLUE ?= \033[0;34m
PURPLE ?= \033[0;35m
CYAN ?= \033[0;36m
GRAY ?= \033[0;37m
COFF ?= \033[0m

PYTHON_INTERPRETER = python3
SOURCE_FOLDER=src

PYTHON=$(shell command -v python3)

PYTHON_VERSION_MIN=3.9

# Create virtual environment and install dependencies
environment:
ifeq (,$(wildcard .venv))
		@printf ">>> No virtual environment found in project directory \n"
		@printf ">>> Creating virtual environment for the project...\n"
		$(PYTHON_INTERPRETER) -m venv .venv
endif
		@printf ">>> Installing dependencies from requirement.txt file"
		.venv/bin/pip install -U pip
		.venv/bin/pip install -r requirements.txt
		. .venv/bin/activate && pre-commit install
