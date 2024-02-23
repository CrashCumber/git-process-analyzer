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
	pip install --upgrade pip
	pip install -r requirements.txt

run_d:
	python3.11 src/main.py -r mux -a gorilla -c 10 -t 0 &

run:
	python3.11 src/main.py -r mux -a gorilla -c 10 -t 0