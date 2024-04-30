include .env

.PHONY: all clean install format run run_d

all: install

clean:
	find . -name "*.pyc" -exec rm {} \;
	find . -name "*.log" -exec rm {} \;

format:
	black src/*
	isort src/*

install:
	cat env >> .env
	mkdir datasets
	python3.11 -m venv venv
	venv/bin/pip install -r requirements.txt

run_d:
	venv/bin/python src/main.py -r ${repo} -a ${author} &

run:
	venv/bin/python src/main.py -r ${repo} -a ${author}