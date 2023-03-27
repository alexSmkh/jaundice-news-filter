test:
	python -m pytest tests/*

run:
	python jaundice_rate/main.py

.PHONY: test run