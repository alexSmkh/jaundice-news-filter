test:
	python -m pytest tests/*

run:
	python jaundice_rate/jaundice_analysis.py

server:
	python jaundice_rate/server.py

install:
	poetry install

env:
	poetry shell

.PHONY: test run install env