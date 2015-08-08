.PHONY: clean-pyc clean-build docs

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
	flake8 djangocms_blog tests
	djangocms-helper djangocms_blog pyflakes --cms

test:
	djangocms-helper djangocms_blog test --cms --nose

test-all:
	tox

coverage:
	coverage erase
	coverage run `which djangocms-helper` djangocms_blog test --cms --nose
	coverage report -m

release: clean
	python setup.py sdist bdist_wheel
	twine upload dist/*

sdist: clean
	python setup.py sdist
	ls -l dist
