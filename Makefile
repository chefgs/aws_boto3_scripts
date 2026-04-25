.PHONY: install test lint

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v

lint:
	python -m py_compile $(shell find services utils -name "*.py")
