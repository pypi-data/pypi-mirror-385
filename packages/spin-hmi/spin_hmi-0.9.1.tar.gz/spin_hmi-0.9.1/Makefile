# Makefile for spin.

SHELL = /bin/bash

T = test
PYTHON = python
JENKINS_HOST ?= jenkins.admin.frm2.tum.de

lint:
	pylint -r n --rcfile=pylintrc spin

clean:
	find . -name '*.pyc' -exec rm -f {} \;

.PHONY: lint clean

release-patch:
	MODE="patch" $(MAKE) release

release-minor:
	MODE="minor" $(MAKE) release

release:
	ssh $(JENKINS_HOST) -p 29417 build -v -s -p GERRIT_PROJECT=$(shell git config --get remote.origin.url | rev | cut -d '/' -f -3 | rev) -p ARCH=all -p MODE=$(MODE) ReleasePipeline

.PHONY: release release-patch release-minor
