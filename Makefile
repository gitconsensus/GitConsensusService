
SHELL:=/bin/bash
ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

.PHONY: all fresh fulluninstall install dependencies clean

all: dependencies

fresh: clean dependencies

fulluninstall: uninstall clean

install:

dependencies:
	if [ ! -d $(ROOT_DIR)/venv ]; then python3 -m venv $(ROOT_DIR)/venv; fi
	source $(ROOT_DIR)/venv/bin/activate; yes w | pip install -e .

clean:
	rm -rf $(ROOT_DIR)/env;
	rm -rf $(ROOT_DIR)/gitconsensusservice/*.pyc;
