include .env

.PHONY: all clean venv install


all: install test

clean:
	find . -name "*.pyc" -exec rm {} \;
	find . -name "*.log" -exec rm {} \;

format:
	black src/*
	isort src/*

venv:
	python3.11 -m venv venv

install:
	echo "export git_token=\nepos_file=\nnumber_to_extract=\nstart_from=" >> .env
	mkdir datasets
	python3.11 -m venv venv
	venv/bin/pip install -r requirements.txt

run_d:
	venv/bin/python src/main.py -r mux -a gorilla &

run:
	venv/bin/python src/main.py -r mux -a gorilla -c 1 -t 0