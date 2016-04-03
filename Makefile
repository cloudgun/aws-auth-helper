install: clean
	pip install -e .

build:
	python setup.py sdist bdist_wheel

release-test: clean build
	twine upload -r pypitest dist/aws-auth-helper-*

release: clean build
	twine upload -r pypi dist/aws-auth-helper-*

test: clean
	tox

test-server: clean
	devpi test route-registry

clean:
	rm -rf dist build *.egg-info MANIFEST .tox .eggs

doc:
	@echo 'building documentation'
	pip install sphinx
	pip install --editable .
	cd docs/ && $(MAKE) -f Makefile clean html
	cd docs/build/html && zip -r ../awsauthhelper.zip *
