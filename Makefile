FLAGS=


flake:
	flake8 gengine tests

develop:
	pip install -r requirements.txt
	pip install -Ue .

test: flake develop
	nosetests -s $(FLAGS) ./tests/

vtest: flake develop
	nosetests -s -v $(FLAGS) ./tests/

cov cover coverage: flake develop
	@coverage erase
	@coverage run -m nose -s $(FLAGS) tests
	@coverage report
	@coverage html
	@echo "open file://`pwd`/coverage/index.html"

clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -f `find . -type f -name '@*' `
	rm -f `find . -type f -name '#*#' `
	rm -f `find . -type f -name '*.orig' `
	rm -f `find . -type f -name '*.rej' `
	rm -f .coverage
	rm -rf coverage
	rm -rf build
	rm -rf cover
	python setup.py clean

.PHONY: all build venv flake test vtest testloop cov clean doc