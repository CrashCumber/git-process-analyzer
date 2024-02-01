include .env

.PHONY: all clean venv install


all: install test

clean:
	find . -name "*.pyc" -exec rm {} \;
	find . -name "*.log" -exec rm {} \;

venv:
	python3.11 -m venv venv

install:
	pip install --upgrade pip
	pip install -r requirements.txt

run_d:
	python3.11 src/main.py &

run:
	python3.11 src/main.py