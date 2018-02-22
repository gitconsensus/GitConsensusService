
SHELL:=/bin/bash
ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

.PHONY: all fresh fulluninstall install dependencies clean

all: application

fresh: clean dependencies

fulluninstall: uninstall clean

install:

dependencies:
	if [ ! -d $(ROOT_DIR)/venv ]; then python3 -m venv $(ROOT_DIR)/venv; fi
	source $(ROOT_DIR)/venv/bin/activate; yes w | pip install -e .

application:
	if [ ! -d $(ROOT_DIR)/venv ]; then python3 -m venv $(ROOT_DIR)/venv; fi
	source $(ROOT_DIR)/venv/bin/activate; yes w | pip install -r requirements.txt

clean:
	rm -rf $(ROOT_DIR)/venv;
	rm -rf $(ROOT_DIR)/gitconsensusservice/*.pyc;
	rm -rf $(ROOT_DIR)/gitconsensusservice.egg-info;
