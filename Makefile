.PHONY: clean-pyc clean-build docs livehtml
PYTHON = python

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "testall - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "release - package and upload a release"
	@echo "sdist - package"

clean: clean-build clean-pyc

clean-build:
	python setup.py clean --all
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

lint:
	tox -epep8,isort

test:
	python cms_helper.py djangocms_blog test

test-all:
	tox

coverage:
	coverage erase
	coverage run cms_helper.py djangocms_blog
	coverage report -m


sdist: clean
	python setup.py sdist
	ls -l dist

release: clean
	python setup.py clean --all sdist bdist_wheel
	python -mtwine upload dist/*

livehtml:
	sphinx-autobuild -b html -p5000 -H0.0.0.0 -E -j auto  -d docs/_build/doctrees --poll docs docs/_build/html
