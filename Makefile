install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt
	
format:
	black *.py
	
lint:
	# pylint --disable=R,C hello.py
	pylint --disable=R,C *.py
	
test:
	# python -m pytest -vv --cov=hello test_hello.py
	ptyhon -m pytest
	
all: install lint test